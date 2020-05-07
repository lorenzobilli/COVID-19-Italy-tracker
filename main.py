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

from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as mp
import sys
import datetime
import pandas
import numpy

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
	# We can already drop some NaN values here
	dataset = dataset.drop(columns=[ "stato", "note_it", "note_en" ])
	return dataset

#
#   Brief:
#       Cleans up a given dataset by removing all columns that are not used during data analysis.
#   Parameters:
#       - dataset: Dataset from which the data shall be removed.
#   Returns:
#       A new dataset without the unnecessary columns.
#
def cleanup_data(dataset):
	dataset = dataset.drop(columns=
	[
		"ricoverati_con_sintomi",
		"terapia_intensiva",
		"totale_ospedalizzati",
		"isolamento_domiciliare",
		"totale_positivi",
		"nuovi_positivi",
		"dimessi_guariti",
		"deceduti",
		"totale_casi"
	])
	return dataset

#
#   Brief:
#       Enriches data with new columns with data used to analyze trends.
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
def enrich_data(dataset):
	new_tests = [0]
	new_cases = [0]
	for n in range(1, dataset.shape[0]):
		new_tests.append(dataset.at[n, "tamponi"] - dataset.at[n - 1, "tamponi"])
		if numpy.isnan(dataset.at[n - 1, "casi_testati"]):
			new_cases.append(numpy.nan)
		else:
			new_cases.append(dataset.at[n, "casi_testati"] - dataset.at[n - 1, "casi_testati"])
	dataset = dataset.drop(columns="tamponi")
	dataset = dataset.drop(columns="casi_testati")
	dataset["nuovi_tamponi"] = new_tests
	dataset["nuovi_casi_testati"] = new_cases

	ratio = [0]
	validated = [0]
	for n in range(1, dataset.shape[0]):
		if numpy.isnan(dataset.at[n, "nuovi_casi_testati"]):
			ratio.append(dataset.at[n, "variazione_totale_positivi"] / dataset.at[n, "nuovi_tamponi"] * 100)
			validated.append(False)
		else:
			ratio.append(dataset.at[n, "variazione_totale_positivi"] / dataset.at[n, "nuovi_casi_testati"] * 100)
			validated.append(True)
	dataset["rapporto"] = ratio
	dataset["validati"] = validated
	dataset = dataset.drop(index=0)
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
	for n in range(end, dataset.shape[0]):
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
	dataset["data"] = pandas.to_datetime(dataset["data"])
	dataset["data"] = dataset["data"].map(datetime.datetime.toordinal)
	x = dataset["data"].to_numpy().reshape(-1, 1)
	y = dataset["rapporto"].to_numpy().reshape(-1, 1)
	linear_regressor = LinearRegression()
	linear_regressor.fit(x, y)
	predictor = linear_regressor.predict(x)
	return predictor

#
#   Brief:
#       Runs the predefined set of reports (global and weekly) and plots them in a single image.
#
def show_global_report():
	pandas.set_option("display.max_rows", None)

	dataset = parse_data(sys.argv[1])
	print(dataset)

	dataset = cleanup_data(dataset)
	dataset = enrich_data(dataset)
	print(dataset)

	figure, (global_report, weekly_report) = mp.subplots(2)
	figure.suptitle("ITALY COVID-19 LINEAR REGRESSION")
	global_report.set_title("Total")
	weekly_report.set_title("Weekly")
	global_report.autoscale()
	weekly_report.autoscale()
	global_report.scatter(dataset["data"], dataset["rapporto"])

	predictor = predict_data(dataset)
	global_report.plot(dataset["data"], predictor, color="red")

	weekly_dataset = parse_data(sys.argv[1])
	weekly_dataset = cleanup_data(weekly_dataset)
	weekly_dataset = enrich_data(weekly_dataset)
	weekly_dataset = select_data_tail(weekly_dataset, 7)
	print(weekly_dataset)

	weekly_report.scatter(weekly_dataset["data"], weekly_dataset["rapporto"])
	weekly_predictor = predict_data(weekly_dataset)
	weekly_report.plot(weekly_dataset["data"], weekly_predictor, color="red")

	mp.show()

#
#   Brief:
#       Runs report for the last given number of days.
#   Parameters:
#       - days: Number of days to be included in the report starting from the bottom of the dataset.
#
def show_custom_tail(days):
	pandas.set_option("display.max_rows", None)

	dataset = parse_data(sys.argv[1])
	print(dataset)

	dataset = cleanup_data(dataset)
	dataset = enrich_data(dataset)
	dataset = select_data_tail(dataset, days)
	print(dataset)

	figure, tail_report = mp.subplots(1)
	figure.suptitle("ITALY COVID-19 LINEAR REGRESSION")
	tail_report.set_title("Last " + str(days) + " days")
	tail_report.autoscale()
	tail_report.scatter(dataset["data"], dataset["rapporto"])

	predictor = predict_data(dataset)
	tail_report.plot(dataset["data"], predictor, color="red")

	mp.show()

#
#   Brief:
#       Runs report for the first given number of days.
#   Parameters:
#       - days: Number of days to be included in the report starting from the top of the dataset.
#
def show_custom_head(days):
	pandas.set_option("display.max_rows", None)

	dataset = parse_data(sys.argv[1])
	print(dataset)

	dataset = cleanup_data(dataset)
	dataset = enrich_data(dataset)
	dataset = select_data_head(dataset, days)
	print(dataset)

	figure, head_report = mp.subplots(1)
	figure.suptitle("ITALY COVID-19 LINEAR REGRESSION")
	head_report.set_title("First " + str(days) + " days")
	head_report.autoscale()
	head_report.scatter(dataset["data"], dataset["rapporto"])

	predictor = predict_data(dataset)
	head_report.plot(dataset["data"], predictor, color="red")

	mp.show()

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
#       Program entrypoint
#   Parameters:
#       - argv[1]: points the CSV file to be analyzed.
#       - argv[2]: days to be checked starting from the beginning. 0 to ignore this value.
#       - argv[3]: days to be checked starting from the end. 0 to ignore this value.
#
def main():

	if len(sys.argv) < 2:
		print("Percorso file dati CSV mancante")
		exit(-1)

	print_splashscreen()

	leave = False
	while not leave:
		print("1) Andamento nazionale")
		print("2) Andamento regionale")
		print("3) Uscita")
		option = input(">: ")
		if int(option) == 1:
			show_global_report()
		elif int(option) == 2:
			print("Funzione attualmente non implementata")
		elif int(option) == 3:
			leave = True
		else:
			print("Opzione selezionata non valida")


if __name__ == "__main__":
	main()