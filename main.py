import sys
import datetime
import pandas
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as mp

def parse_data(feed):
	raw_data = pandas.read_csv(feed, parse_dates=[0])
	dataset = pandas.DataFrame(raw_data)
	dataset = dataset.drop(columns=[    # We can already drop some NaN values here
		"stato",
		"note_it",
		"note_en"])
	return dataset


def cleanup_data(dataset):
	dataset = dataset.drop(columns=[
		"ricoverati_con_sintomi",
		"terapia_intensiva",
		"totale_ospedalizzati",
		"isolamento_domiciliare",
		"totale_positivi",
		"nuovi_positivi",
		"dimessi_guariti",
		"deceduti",
		"totale_casi"])
	return dataset


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


def select_data_tail(dataset, quantity):
	if quantity >= dataset.shape[0]:
		return
	for n in range(1, dataset.shape[0] - (quantity - 1)):
		dataset = dataset.drop(index=n)
	return dataset


def predict_data(dataset):
	dataset["data"] = pandas.to_datetime(dataset["data"])
	dataset["data"] = dataset["data"].map(datetime.datetime.toordinal)
	x = dataset["data"].to_numpy().reshape(-1, 1)
	y = dataset["rapporto"].to_numpy().reshape(-1, 1)
	linear_regressor = LinearRegression()
	linear_regressor.fit(x, y)
	predictor = linear_regressor.predict(x)
	return predictor


if (len(sys.argv) != 2):
	print("Please provide a CSV filename")
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
