#
#   COVID-19 Italy tracker
#
#   Copyright (c) 2020 Lorenzo Billi
#
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
#   License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any
#   later version.
#
#   This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
#   more details.
#
#   You should have received a copy of the GNU General Public License along with this program.
#   If not, see <http://www.gnu.org/licenses/>.
#

import datetime
import sys
from enum import IntEnum
from pathlib import Path

import matplotlib.pyplot as mp
import numpy
import pandas
from sklearn.linear_model import LinearRegression
import tabulate

#
#   Brief:
#       Enum used for regions. Integer values correspond to the internal regional ID used in the datasets.
#
class Region(IntEnum):
	ABRUZZO = 13
	BASILICATA = 17
	CALABRIA = 18
	CAMPANIA = 15
	EMILIA_ROMAGNA = 8
	FRIULI_VENEZIA_GIULIA = 6
	LAZIO = 12
	LIGURIA = 7
	LOMBARDIA = 3
	MARCHE = 11
	MOLISE = 14
	PA_BOLZANO = 21
	PA_TRENTO = 22
	PIEMONTE = 1
	PUGLIA = 16
	SARDEGNA = 20
	SICILIA = 19
	TOSCANA = 9
	UMBRIA = 10
	VALLE_D_AOSTA = 2
	VENETO = 5


tabify = lambda dataframe: tabulate.tabulate(dataframe, headers="keys", tablefmt="psql")

#
#   Brief:
#       Parses raw data retrieved from a CSV file and returns a dataset as a pandas DataFrame object.
#   Parameters:
#       - feed: Raw data to be parsed (must contain/point to a CSV file).
#   Returns:
#       A dataset as a pandas DataFrame object.
#
def parse_data(feed):
	raw_data = pandas.read_csv(feed, parse_dates=[0])
	dataset = pandas.DataFrame(raw_data)
	dataset["data"] = pandas.to_datetime(dataset["data"])
	dataset["data"] = dataset["data"].dt.date
	return dataset


#
#   Brief:
#       Cleans up a given dataset by removing all columns that are not used during data analysis.
#   Parameters:
#       - dataset: Dataset from which the data shall be removed.
#       - region: If provided, marks current dataset as a regional one, thus removing additional unneeded columns.
#   Returns:
#       A new dataset without the unnecessary columns.
#
def cleanup_data(dataset, region=None):
	dataset = dataset.drop(columns=
	[
		"stato",
		"ricoverati_con_sintomi",
		"terapia_intensiva",
		"totale_ospedalizzati",
		"isolamento_domiciliare",
		"totale_positivi",
		"variazione_totale_positivi",
		"dimessi_guariti",
		"deceduti",
		"casi_da_sospetto_diagnostico",
		"casi_da_screening",
		"totale_casi",
		"note"
	])
	if region is not None:
		dataset.drop(dataset[dataset["codice_regione"] != Region(region)].index, inplace=True)
		dataset.reset_index(drop=True, inplace=True)
		dataset = dataset.drop(columns=["codice_regione", "denominazione_regione", "lat", "long"])
	return dataset


#
#   Brief:
#       Enriches data with new columns with data used to analyze trends, and renames existing ones to a known,
#       standardized string format.
#   Detailed description:
#       We can't draw a trend line without knowing how large the sample size is. By default, only new COVID-19 positive
#       patients are indicated in official data. In order to achieve any vaguely scientific results we NEED to know the
#       sample size. Fortunately, data contains also the total number of executed tests from the beginning.
#       We first calculate the daily sample size, then a ratio is calculated between new positive patients and new
#       daily tests. This value is the multiplied by 100 in order to obtain the % value of positive patients of the
#       daily tests pool. This lets us draw a trend line that actually makes sense.
#   Parameters:
#       - dataset: Dataset to be enriched.
#   Returns:
#       A new dataset with all the new data required.
#
def elaborate_data(dataset):
	tests = [0]
	for n in range(1, dataset.shape[0]):
		if numpy.isnan(dataset.at[n - 1, "casi_testati"]):
			tests.append(dataset.at[n, "tamponi"] - dataset.at[n - 1, "tamponi"])
		else:
			tests.append(dataset.at[n, "casi_testati"] - dataset.at[n - 1, "casi_testati"])
	dataset.drop(columns="tamponi", inplace=True)
	dataset.drop(columns="casi_testati", inplace=True)
	dataset["TAMPONI"] = tests
	dataset.rename(columns={"data" : "DATA", "nuovi_positivi" : "NUOVI POSITIVI"}, inplace=True)
	ratio = [0]
	for n in range(1, dataset.shape[0]):
		# Makes sure we're not dividing by 0 in case no tests are registered.
		if dataset.at[n, "TAMPONI"] != 0:
			ratio.append(dataset.at[n, "NUOVI POSITIVI"] / dataset.at[n, "TAMPONI"] * 100)
		else:
			ratio.append(0)
	dataset["RAPPORTO"] = ratio
	dataset.drop(index=0, inplace=True)
	return dataset


#
#   Brief:
#       Trims a given dataset by keeping only a certain amount of data starting from the top.
#   Parameters:
#       - dataset: Dataset to be trimmed down.
#       - quantity: Amount of data to be kept in the dataset.
#   Returns:
#       A new dataset containing the first n values (where n is the quantity parameter).
#
def select_data_head(dataset, quantity):
	if quantity > dataset.shape[0]:
		return
	for n in range(1 + quantity, dataset.shape[0] + 1):
		dataset = dataset.drop(index=n)
	return dataset


#
#   Brief:
#       Trims a given dataset by keeping only a certain amount of data starting from the bottom.
#   Parameters:
#       - dataset: Dataset to be trimmed down.
#       - quantity: Amount of data to be kept in the dataset.
#   Returns:
#       A new dataset containing the last n values (where n is the quantity parameter).
#
def select_data_tail(dataset, quantity):
	if quantity > dataset.shape[0]:
		return
	for n in range(1, dataset.shape[0] - (quantity - 1)):
		dataset = dataset.drop(index=n)
	return dataset


#
#   Brief:
#       Trims a given dataset by keeping only a certain range of data.
#   Parameters:
#       - dataset: Dataset to be trimmed down.
#       - begin: Begin of the range of data to be kept.
#       - end: End of the range of data to be kept.
#   Returns:
#       A new dataset containing the selected range of values.
def select_data_range(dataset, begin, end):
	if begin <= 0:
		return
	if end > dataset.shape[0]:
		return
	if end <= begin:
		return
	for n in range(1, begin):
		dataset = dataset.drop(index=n)
	for n in range(end, dataset.shape[0] + 1):
		dataset = dataset.drop(index=n)
	return dataset


#
#   Brief:
#       Predicts trend with linear regression on the given dataset values.
#   Parameters:
#       - dataset: Dataset where the prediction shall be made.
#   Returns:
#       A plottable line representing the computed linear regression.
#
def predict_data(dataset):
	dataset["DATA"] = dataset["DATA"].map(datetime.datetime.toordinal)
	x = dataset["DATA"].to_numpy().reshape(-1, 1)
	y = dataset["RAPPORTO"].to_numpy().reshape(-1, 1)
	linear_regressor = LinearRegression()
	linear_regressor.fit(x, y)
	predictor = linear_regressor.predict(x)
	return predictor


#
#   Brief:
#       Runs a report based on the given parameters. By default it plots the global national report.
#   Parameters:
#       - dataset_path: Path pointing to the CSV file used as dataset.
#       - begin: Number of days to analyze in the report starting from the beginning.
#       - end: Number of days to analyze in the report starting from the end.
#
def show_national_report(dataset_path, begin=None, end=None):
	pandas.set_option("display.max_rows", None)
	pandas.set_option("display.max_columns", None)
	pandas.set_option("display.width", None)

	dataset = parse_data(dataset_path)
	dataset = cleanup_data(dataset)
	dataset = elaborate_data(dataset)

	figure, report = mp.subplots(1)
	figure.suptitle("COVID-19 LINEAR REGRESSION: ITALIA")
	if begin is not None and end is not None:
		report.set_title("From day " + str(begin) + " to day " + str(end))
		dataset = select_data_range(dataset, int(begin), int(end))
	elif begin is not None and end is None:
		report.set_title("First " + str(begin) + " days")
		dataset = select_data_head(dataset, int(begin))
	elif begin is None and end is not None:
		report.set_title("Last " + str(end) + " days")
		dataset = select_data_tail(dataset, int(end))
	else:
		report.set_title("Global report")
	report.autoscale()
	report.scatter(dataset["DATA"], dataset["RAPPORTO"])

	predictor = predict_data(dataset.copy())
	report.plot(dataset["DATA"], predictor, color="red")

	print("")
	print(tabify(dataset))
	mp.show()


#
#   Brief:
#       Runs a report based on the given parameters. By default it plots the global regional report.
#   Parameters:
#       - dataset_path: Path pointing to the CSV file used as dataset.
#       - region: Region which will be analyzed to generate the report.
#       - begin: Number of days to analyze in the report starting from the beginning.
#       - end: Number of days to analyze in the report starting from the end.
#
def show_regional_report(dataset_path, region, begin=None, end=None):
	pandas.set_option("display.max_rows", None)
	pandas.set_option("display.max_columns", None)
	pandas.set_option("display.width", None)

	dataset = parse_data(dataset_path)
	dataset = cleanup_data(dataset, region)
	dataset = elaborate_data(dataset)

	figure, report = mp.subplots(1)
	title = "COVID-19 LINEAR REGRESSION: "
	if region == Region.ABRUZZO:
		title += "REGIONE ABRUZZO"
	elif region == Region.BASILICATA:
		title += "REGIONE BASILICATA"
	elif region == Region.CALABRIA:
		title += "REGIONE CALABRIA"
	elif region == Region.CAMPANIA:
		title += "REGIONE CAMPANIA"
	elif region == Region.EMILIA_ROMAGNA:
		title += "REGIONE EMILIA-ROMAGNA"
	elif region == Region.FRIULI_VENEZIA_GIULIA:
		title += "REGIONE FRIULI-VENEZIA GIULIA"
	elif region == Region.LAZIO:
		title += "REGIONE LAZIO"
	elif region == Region.LIGURIA:
		title += "REGIONE LIGURIA"
	elif region == Region.LOMBARDIA:
		title += "REGIONE LOMBARDIA"
	elif region == Region.MARCHE:
		title += "REGIONE MARCHE"
	elif region == Region.MOLISE:
		title += "REGIONE MOLISE"
	elif region == Region.PA_BOLZANO:
		title += "P.A. BOLZANO"
	elif region == Region.PA_TRENTO:
		title += "P.A. TRENTO"
	elif region == Region.PIEMONTE:
		title += "REGIONE PIEMENTE"
	elif region == Region.PUGLIA:
		title += "REGIONE PUGLIA"
	elif region == Region.SARDEGNA:
		title += "REGIONE SARDEGNA"
	elif region == Region.SICILIA:
		title += "REGIONE SICILIA"
	elif region == Region.TOSCANA:
		title += "REGIONE TOSCANA"
	elif region == Region.UMBRIA:
		title += "REGIONE VALLE D'AOSTA"
	elif region == Region.VENETO:
		title += "REGIONE VENETO"
	figure.suptitle(title)
	if begin is not None and end is not None:
		report.set_title("From day " + str(begin) + " to day " + str(end))
		dataset = select_data_range(dataset, int(begin), int(end))
	elif begin is not None and end is None:
		report.set_title("First " + str(begin) + " days")
		dataset = select_data_head(dataset, int(begin))
	elif begin is None and end is not None:
		report.set_title("Last " + str(end) + " days")
		dataset = select_data_tail(dataset, int(end))
	else:
		report.set_title("Global report")
	report.autoscale()
	report.scatter(dataset["DATA"], dataset["RAPPORTO"])

	predictor = predict_data(dataset.copy())
	report.plot(dataset["DATA"], predictor, color="red")

	print("")
	print(tabify(dataset))
	mp.show()


#
#   Brief:
#       Chooses the type of report (time-wise) that will be produced.
#   Parameters:
#       - dataset_path: Path pointing to the CSV file used to generate the report.
#       - region: If provided, specifies the CSV region file from which data will be picked up. If no parameter is
#           specified, data will be picked from the national CSV file.
#
def choose_report_type(dataset_path, region=None):
	while True:
		print("")
		print("1) Visualizza report globale")
		print("2) Visualizza primi N giorni")
		print("3) Visualizza ultimi N giorni")
		print("4) Visualizza intervallo personalizzato")
		print("5) Indietro")
		option = input(">: ")
		if int(option) == 1:
			if region is None:
				show_national_report(dataset_path)
			else:
				show_regional_report(dataset_path, region)
		elif int(option) == 2:
			begin = input("Numero giorni: ")
			if region is None:
				show_national_report(dataset_path, begin=begin)
			else:
				show_regional_report(dataset_path, region, begin=begin)
		elif int(option) == 3:
			end = input("Numero giorni: ")
			if region is None:
				show_national_report(dataset_path, end=end)
			else:
				show_regional_report(dataset_path, region, end=end)
		elif int(option) == 4:
			begin = input("Giorno iniziale: ")
			end = input("Giorno finale: ")
			if region is None:
				show_national_report(dataset_path, begin, end)
			else:
				show_regional_report(dataset_path, region, begin, end)
		elif int(option) == 5:
			break
		else:
			print("Opzione selezionata non valida")


def show_national_ranking(dataset_path):
	dataset = parse_data(dataset_path)
	results = {}
	ranking = pandas.DataFrame()

	for region in Region:
		regional_dataset = dataset.copy()
		regional_dataset = cleanup_data(regional_dataset, region)
		regional_dataset = elaborate_data(regional_dataset)
		results[region] = regional_dataset

	ranking["REGIONE"] = [
		"Abruzzo",
		"Basilicata",
		"Calabria",
		"Campania",
		"Emilia-Romagna",
		"Friuli Venezia Giulia",
		"Lazio",
		"Liguria",
		"Lombardia",
		"Marche",
		"Molise",
		"P.A. Bolzano",
		"P.A. Trento",
		"Piemonte",
		"Puglia",
		"Sardegna",
		"Sicilia",
		"Toscana",
		"Umbria",
		"Valle d'Aosta",
		"Veneto"
	]

	ranking["RAPPORTO"] = [
		results.get(Region.ABRUZZO).tail(1).loc[:, "RAPPORTO"],
		results.get(Region.BASILICATA).tail(1).loc[:, "RAPPORTO"],
		results.get(Region.CALABRIA).tail(1).loc[:, "RAPPORTO"],
		results.get(Region.CAMPANIA).tail(1).loc[:, "RAPPORTO"],
		results.get(Region.EMILIA_ROMAGNA).tail(1).loc[:, "RAPPORTO"],
		results.get(Region.FRIULI_VENEZIA_GIULIA).tail(1).loc[:, "RAPPORTO"],
		results.get(Region.LAZIO).tail(1).loc[:, "RAPPORTO"],
		results.get(Region.LIGURIA).tail(1).loc[:, "RAPPORTO"],
		results.get(Region.LOMBARDIA).tail(1).loc[:, "RAPPORTO"],
		results.get(Region.MARCHE).tail(1).loc[:, "RAPPORTO"],
		results.get(Region.MOLISE).tail(1).loc[:, "RAPPORTO"],
		results.get(Region.PA_BOLZANO).tail(1).loc[:, "RAPPORTO"],
		results.get(Region.PA_TRENTO).tail(1).loc[:, "RAPPORTO"],
		results.get(Region.PIEMONTE).tail(1).loc[:, "RAPPORTO"],
		results.get(Region.PUGLIA).tail(1).loc[:, "RAPPORTO"],
		results.get(Region.SARDEGNA).tail(1).loc[:, "RAPPORTO"],
		results.get(Region.SICILIA).tail(1).loc[:, "RAPPORTO"],
		results.get(Region.TOSCANA).tail(1).loc[:, "RAPPORTO"],
		results.get(Region.UMBRIA).tail(1).loc[:, "RAPPORTO"],
		results.get(Region.VALLE_D_AOSTA).tail(1).loc[:, "RAPPORTO"],
		results.get(Region.VENETO).tail(1).loc[:, "RAPPORTO"]
	]

	ranking["RAPPORTO"] = ranking["RAPPORTO"].astype(float)
	ranking.sort_values(by="RAPPORTO", ascending=False, inplace=True)

	print("")
	print(tabify(ranking))


#
#   Brief:
#       Prints a formatted welcome splash screen.
#
def print_splashscreen():
	print("")
	print(" / ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ \\")
	print("|  /~~\\                                                               /~~\\  |")
	print("|\\ \\   |           ____ _____     _____ ____        _  ___           |   / /|")
	print("| \\   /|          / ___/ _ \\ \\   / /_ _|  _ \\      / |/ _ \\          |\\   / |")
	print("|  ~~  |         | |  | | | \\ \\ / / | || | | |_____| | (_) |         |  ~~  |")
	print("|      |         | |__| |_| |\\ V /  | || |_| |_____| |\\__, |         |      |")
	print("|      |          \\____\\___/  \\_/  |___|____/      |_|  /_/          |      |")
	print("|      |                                                             |      |")
	print("|      |   ___ _        _         _                  _               |      |")
	print("|      |  |_ _| |_ __ _| |_   _  | |_ _ __ __ _  ___| | _____ _ __   |      |")
	print("|      |   | || __/ _` | | | | | | __| '__/ _` |/ __| |/ / _ \\ '__|  |      |")
	print("|      |   | || || (_| | | |_| | | |_| | | (_| | (__|   <  __/ |     |      |")
	print("|      |  |___|\\__\\__,_|_|\\__, |  \\__|_|  \\__,_|\\___|_|\\_\\___|_|     |      |")
	print("|      |                  |___/                                      |      |")
	print("|      |                                                             |      |")
	print(" \\     |~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|     /")
	print("  \\   /                                                               \\   /")
	print("   ~~~                                                                 ~~~")
	print("")


#
#   Brief:
#       Program entrypoint.
#   Parameters:
#       - argv[1]: Path (either absolute or relative) to the data repository containing the CSV files.
#
def main():
	if len(sys.argv) < 2:
		print("Percorso repository dati COVID-19 mancante")
		exit(-1)

	national_data_path = Path(sys.argv[1] + "/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv")
	regional_data_path = Path(sys.argv[1] + "/dati-regioni/dpc-covid19-ita-regioni.csv")

	print_splashscreen()

	while True:
		print("")
		print("1) Andamento nazionale")
		print("2) Andamento regionale")
		print("3) Classifica nazionale contagi")
		print("4) Uscita")
		option = input(">: ")
		if int(option) == 1:
			choose_report_type(national_data_path)
		elif int(option) == 2:
			while True:
				print("")
				print("1) Abruzzo")
				print("2) Basilicata")
				print("3) Calabria")
				print("4) Campania")
				print("5) Emilia-Romagna")
				print("6) Friuli Venezia Giulia")
				print("7) Lazio")
				print("8) Liguria")
				print("9) Lombardia")
				print("10) Marche")
				print("11) Molise")
				print("12) P.A. Bolzano")
				print("13) P.A. Trento")
				print("14) Piemonte")
				print("15) Puglia")
				print("16) Sardegna")
				print("17) Sicilia")
				print("18) Toscana")
				print("19) Umbria")
				print("20) Valle d'Aosta")
				print("21) Veneto")
				print("22) Indietro")
				suboption = input(">: ")
				if int(suboption) == 1:
					choose_report_type(regional_data_path, Region.ABRUZZO)
				elif int(suboption) == 2:
					choose_report_type(regional_data_path, Region.BASILICATA)
				elif int(suboption) == 3:
					choose_report_type(regional_data_path, Region.CALABRIA)
				elif int(suboption) == 4:
					choose_report_type(regional_data_path, Region.CAMPANIA)
				elif int(suboption) == 5:
					choose_report_type(regional_data_path, Region.EMILIA_ROMAGNA)
				elif int(suboption) == 6:
					choose_report_type(regional_data_path, Region.FRIULI_VENEZIA_GIULIA)
				elif int(suboption) == 7:
					choose_report_type(regional_data_path, Region.LAZIO)
				elif int(suboption) == 8:
					choose_report_type(regional_data_path, Region.LIGURIA)
				elif int(suboption) == 9:
					choose_report_type(regional_data_path, Region.LOMBARDIA)
				elif int(suboption) == 10:
					choose_report_type(regional_data_path, Region.MARCHE)
				elif int(suboption) == 11:
					choose_report_type(regional_data_path, Region.MOLISE)
				elif int(suboption) == 12:
					choose_report_type(regional_data_path, Region.PA_BOLZANO)
				elif int(suboption) == 13:
					choose_report_type(regional_data_path, Region.PA_TRENTO)
				elif int(suboption) == 14:
					choose_report_type(regional_data_path, Region.PIEMONTE)
				elif int(suboption) == 15:
					choose_report_type(regional_data_path, Region.PUGLIA)
				elif int(suboption) == 16:
					choose_report_type(regional_data_path, Region.SARDEGNA)
				elif int(suboption) == 17:
					choose_report_type(regional_data_path, Region.SICILIA)
				elif int(suboption) == 18:
					choose_report_type(regional_data_path, Region.TOSCANA)
				elif int(suboption) == 19:
					choose_report_type(regional_data_path, Region.UMBRIA)
				elif int(suboption) == 20:
					choose_report_type(regional_data_path, Region.VALLE_D_AOSTA)
				elif int(suboption) == 21:
					choose_report_type(regional_data_path, Region.VENETO)
				elif int(suboption) == 22:
					break
				else:
					print("Opzione selezionata non valida")
		elif int(option) == 3:
			show_national_ranking(regional_data_path)
		elif int(option) == 4:
			break
		else:
			print("Opzione selezionata non valida")


if __name__ == "__main__":
	main()
