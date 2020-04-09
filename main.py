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
	for n in range(1, dataset.shape[0]):
		new_tests.append(dataset.at[n, "tamponi"] - dataset.at[n - 1, "tamponi"])
	dataset = dataset.drop(columns="tamponi")
	dataset["nuovi_tamponi"] = new_tests

	ratio = [0]
	for n in range(1, dataset.shape[0]):
		ratio.append(dataset.at[n, "variazione_totale_positivi"] / dataset.at[n, "nuovi_tamponi"] * 100)
	dataset["rapporto"] = ratio
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
	for n in range(1 + quantity, dataset.shape[0]):
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
#       Predict trend with linear regression on the given dataset values.
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
#       Program entrypoint
#   Parameters:
#       - argv[1]: points the CSV file to be analyzed
#
def main():
	if (len(sys.argv) < 2):
		print("Usage: ./main.py <csv file>")
		exit(-1)

	dataset = parse_data(sys.argv[1])
	print(dataset)

	dataset = cleanup_data(dataset)
	dataset = enrich_data(dataset)
	print(dataset)

	figure, (total, weekly) = mp.subplots(2)
	figure.suptitle("ITALY COVID-19 LINEAR REGRESSION")
	total.set_title("Total")
	weekly.set_title("Weekly")
	total.autoscale()
	weekly.autoscale()
	total.scatter(dataset["data"], dataset["rapporto"])

	predictor = predict_data(dataset)
	total.plot(dataset["data"], predictor, color="red")

	weekly_dataset = parse_data(sys.argv[1])
	weekly_dataset = cleanup_data(weekly_dataset)
	weekly_dataset = enrich_data(weekly_dataset)
	weekly_dataset = select_data_tail(weekly_dataset, 7)
	print(weekly_dataset)

	weekly.scatter(weekly_dataset["data"], weekly_dataset["rapporto"])
	weekly_predictor = predict_data(weekly_dataset)
	weekly.plot(weekly_dataset["data"], weekly_predictor, color="red")

	mp.show()


if __name__ == "__main__":
	main()