#
#   COVID-19 Italy tracker
#
#   Copyright (c) 2020-2021 Lorenzo Billi
#
#   This program is free software: you can redistribute it and/or modify it under the terms of the
#   GNU General Public License as published by the Free Software Foundation, either version 3 of
#   the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#   without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#   See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along with this program.
#   If not, see <http://www.gnu.org/licenses/>.
#


import datetime
import numpy
import pandas
from sklearn.linear_model import LinearRegression
from joblib import Parallel, delayed
from region import *
from utils import *


#
#   Brief:
#       Parses raw data retrieved from a CSV file and returns a dataset as a pandas DataFrame object.
#   Parameters:
#       - feed: Raw data to be parsed (must contain/point to a CSV file).
#   Returns:
#       A dataset as a pandas DataFrame object.
#
def parse_csv_data(feed):
	raw_data = pandas.read_csv(feed, parse_dates=[0])
	dataset = pandas.DataFrame(raw_data)
	dataset["data"] = pandas.to_datetime(dataset["data"])
	dataset["data"] = dataset["data"].dt.date
	return dataset


#
#   Brief:
#       Parses raw data retrieved from a JSON file and returns a dataset as a Python dictionary.
#   Parameters:
#       - feed: Raw data to be parsed (must contain/point to a JSON file).
#   Returns:
#       A dataset as a Python dictionary.
#
def parse_json_data(feed):
	raw_data = pandas.read_json(feed)
	dataset = pandas.DataFrame(raw_data)
	return dataset


#
#   Brief:
#       Cleans up a given dataset by removing all columns that are not used during data analysis.
#   Parameters:
#       - dataset: Dataset from which the data shall be removed.
#       - region: If provided, marks current dataset as a regional one, thus removing additional
#                 unneeded columns.
#   Returns:
#       A new dataset without the unnecessary columns.
#
def cleanup_data(dataset, region=None):
	dataset.drop(columns=["stato", "ricoverati_con_sintomi", "totale_ospedalizzati",
	                      "isolamento_domiciliare", "totale_positivi", "variazione_totale_positivi",
	                      "dimessi_guariti", "casi_da_sospetto_diagnostico", "casi_da_screening",
	                      "totale_casi", "note"], inplace=True)
	if region is not None:
		dataset.drop(dataset[dataset["codice_regione"] != region.value[0]].index, inplace=True)
		dataset.drop(columns=["codice_regione", "denominazione_regione", "lat", "long"], inplace=True)
		dataset.reset_index(drop=True, inplace=True)
	return dataset


#
#   Brief:
#       Cleans up a given RT dataset and prepares it for reports generation.
#   Parameters:
#       - dataset: Dataset from which the data shall be transformed.
#       - region: If provided, changes some of the data being removed from the dataset.
#   Returns:
#       A new dataset without the unnecessary columns.
#
def cleanup_rt_data(dataset, region=None):
	if (region == None):
		dataset.drop(columns={"data"}, inplace=True)
	dataset.drop(columns={"data_IT_format", "note", "link"}, inplace=True)

	if (region != None):
		dataset.rename(columns={"data": "DATA"}, inplace=True)
	dataset.rename(columns={
		"Abruzzo": Region.ABRUZZO.value[1],
		"Basilicata": Region.BASILICATA.value[1],
		"Calabria": Region.CALABRIA.value[1],
		"Campania": Region.CAMPANIA.value[1],
		"Emilia Romagna": Region.EMILIA_ROMAGNA.value[1],
		"Friuli Venezia Giulia": Region.FRIULI_VENEZIA_GIULIA.value[1],
		"Lazio": Region.LAZIO.value[1],
		"Liguria": Region.LIGURIA.value[1],
		"Lombardia": Region.LOMBARDIA.value[1],
		"Marche": Region.MARCHE.value[1],
		"Molise": Region.MOLISE.value[1],
		"Piemonte": Region.PIEMONTE.value[1],
		"PA Bolzano/Bozen": Region.PA_BOLZANO.value[1],
		"PA Trento": Region.PA_TRENTO.value[1],
		"Puglia": Region.PUGLIA.value[1],
		"Sardegna": Region.SARDEGNA.value[1],
		"Sicilia": Region.SICILIA.value[1],
		"Toscana": Region.TOSCANA.value[1],
		"Umbria": Region.UMBRIA.value[1],
		"Valle d'Aosta": Region.VALLE_D_AOSTA.value[1],
		"Veneto": Region.VENETO.value[1]
	}, inplace=True)
	dataset.reset_index(drop=True, inplace=True)
	return dataset


#
#   Brief:
#       Calculates deltas between tests from current and previous day.
#   Parameters:
#       - n: Index of the list where the calculated result shall be inserted.
#       - dataset: Dataset from where data is retrieved.
#
def calculate_tests_delta(n, dataset):
	if numpy.isnan(dataset.at[n - 1, "casi_testati"]):
		return int(dataset.at[n, "tamponi"] - dataset.at[n - 1, "tamponi"])
	else:
		return int(dataset.at[n, "casi_testati"] - dataset.at[n - 1, "casi_testati"])


#
#   Brief:
#       Calculates ratio between new positive cases and new tests.
#   Parameters:
#       - n: Index of the list where the calculated result shall be inserted.
#       - dataset: Dataset from where data is retrieved.
#
def calculate_ratio(n, dataset):
	if dataset.at[n, "testati"] == 0:
		return 0
	else:
		return round(dataset.at[n, "nuovi_positivi"] / dataset.at[n, "testati"] * 100, 2)


#
#   Brief:
#       Calculates deltas between deaths from current and previous day.
#   Parameters:
#       - n: Index of the list where the calculated result shall be inserted.
#       - dataset: Dataset from where data is retrieved.
#
def calculate_deaths_delta(n, dataset):
	delta = dataset.at[n, "deceduti"] - dataset.at[n - 1, "deceduti"]
	if delta >= 0:
		return int(delta)
	else:
		return 0


#
#   Brief:
#       Calculates deltas between ICUs from current and previous day.
#   Parameters:
#       - n: Index of the list where the calculated result shall be inserted.
#       - dataset: Dataset from where data is retrieved.
#
def calculate_icu_delta(n, dataset):
	return int(dataset.at[n, "terapia_intensiva"] - dataset.at[n - 1, "terapia_intensiva"])


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
	tests = Parallel(cpus)(
		delayed(calculate_tests_delta)(n, dataset) for n in range(1, dataset.shape[0])
	)
	tests.insert(0, 0)
	dataset["testati"] = list(tests)

	ratio = Parallel(cpus)(
		delayed(calculate_ratio)(n, dataset) for n in range(1, dataset.shape[0])
	)
	ratio.insert(0, 0)
	dataset["rapporto"] = ratio

	deaths = Parallel(cpus)(
		delayed(calculate_deaths_delta)(n, dataset) for n in range(1, dataset.shape[0])
	)
	deaths.insert(0, 0)
	dataset["morti"] = deaths

	icus = Parallel(cpus)(
		delayed(calculate_icu_delta)(n, dataset) for n in range(1, dataset.shape[0])
	)
	icus.insert(0, 0)
	dataset["terapia_intensiva_diff"] = icus

	# Removing unneeded columns
	dataset.drop(columns={"tamponi", "casi_testati", "deceduti"}, inplace=True)

	# Renaming resulting columns
	dataset.rename(columns={"data": "DATA", "nuovi_positivi": "N. POS.", "testati": "TEST",
	                        "rapporto": "%", "terapia_intensiva": "T.I.", "terapia_intensiva_diff": "DIFF.",
	                        "morti": "MORTI"}, inplace=True)

	# Reordering dataset
	dataset = dataset.loc[:, ["DATA", "N. POS.", "TEST", "%", "T.I.", "DIFF.", "MORTI"]]
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
#       Trims a given dataset by keeping only the latest row of data.
#   Parameters:
#       - dataset: Dataset to be trimmed down.
#   Returns:
#       A new dataset containing only the latest row of data.
#
def select_data_bottom(dataset):
	for n in range(0, dataset.shape[0] - 1):
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
#
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
#       - value_label: Values to be regressed.
#   Returns:
#       A plottable line representing the computed linear regression.
#
def predict_data(dataset, value_label):
	dataset["DATA"] = dataset["DATA"].map(datetime.datetime.toordinal)
	x = dataset["DATA"].to_numpy().reshape(-1, 1)
	y = dataset[value_label].to_numpy().reshape(-1, 1)
	linear_regressor = LinearRegression(n_jobs=multiprocessing.cpu_count())
	linear_regressor.fit(x, y)
	predictor = linear_regressor.predict(x)
	return predictor


#
#   Brief:
#       Collects given regional dataset and puts it into a dictionary.
#   Parameters:
#       - dataset: Dataset used.
#       - region: Region selected.
#       - results: Dictionary where collected dataset shall be stored.
#
def collect_regional_dataset(dataset, region, results):
	regional_dataset = dataset.copy()
	regional_dataset = cleanup_data(regional_dataset, region)
	regional_dataset = elaborate_data(regional_dataset)
	results[region] = regional_dataset


#
#   Brief:
#       Populates two separate lists containing regions and corresponding ratios for building up the ranking.
#   Parameters:
#       - n: Index of the lists where regions name and ratios shall be inserted.
#       - regions: List containing all regions' names
#       - ratios: List containing all regions' ratios
#       - results: Dictionary from where ratios are retrieved.
#
def build_ranking_lists(n, regions, ratios, region, results):
	regions.insert(n, region.value[1])
	ratios.insert(n, results.get(region).tail(1).loc[:, "%"])
