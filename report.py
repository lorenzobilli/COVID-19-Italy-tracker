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


import matplotlib.pyplot as mp

from data import *
from utils import *


#
#   Brief:
#       Runs a report based on the given parameters.
#   Parameters:
#       - dataset_path: Path pointing to the CSV file used as dataset.
#       - begin: Number of days to analyze in the report starting from the beginning.
#       - end: Number of days to analyze in the report starting from the end.
#
def show_report(dataset_path, region=None, begin=None, end=None):
	pandas.set_option("display.max_rows", None)
	pandas.set_option("display.max_columns", None)
	pandas.set_option("display.width", None)

	dataset = parse_csv_data(dataset_path)
	dataset = cleanup_data(dataset, region)
	dataset = elaborate_data(dataset)

	figure, report = mp.subplots(1)
	title = "COVID-19 - ANDAMENTO E REGRESSIONE LINEARE: "
	if region is None:
		title += " ITALIA"
	else:
		title += " REGIONE " + region.value[1].upper()
	figure.suptitle(title)
	mp.ylabel("Nuovi positivi (%)")

	if begin is not None and end is not None:
		report.set_title("Dal giorno " + str(begin) + " al giorno " + str(end))
		dataset = select_data_range(dataset, int(begin), int(end))
	elif begin is not None and end is None:
		report.set_title("Primi " + str(begin) + " giorni")
		dataset = select_data_head(dataset, int(begin))
	elif begin is None and end is not None:
		report.set_title("Ultimi " + str(end) + " giorni")
		dataset = select_data_tail(dataset, int(end))
	else:
		report.set_title("Report globale")
	report.autoscale()
	report.scatter(dataset["DATA"], dataset["%"])

	predictor = predict_data(dataset.copy())
	report.plot(dataset["DATA"], predictor, color="red")

	print("")
	print(tabify(dataset))

	print("")
	print("1) Mostra grafico regressione lineare")
	print("2) Indietro")
	option = input(">: ")

	if int(option) == 1:
		mp.show()
	else:
		return


#
#   Brief:
#       Shows the national daily ranking sorted by ratio values.
#   Parameters:
#       - dataset_path: Path pointing to the CSV file used to generate the report.
#
def show_national_ranking(dataset_path):
	dataset = parse_csv_data(dataset_path)
	results = {}
	ranking = pandas.DataFrame()

	Parallel(cpus, require="sharedmem")(
		delayed(collect_regional_dataset)(dataset, region, results) for region in Region
	)

	regions = []
	ratios = []

	Parallel(cpus, require="sharedmem")(
		delayed(build_ranking_lists)(n, regions, ratios, region, results) for n, region in enumerate(Region)
	)

	ranking["REGIONE"] = regions
	ranking["%"] = ratios
	ranking["%"] = ranking["%"].astype(float)
	ranking.sort_values(by="%", ascending=False, inplace=True)
	ranking.reset_index(drop=True, inplace=True)
	ranking.index += 1

	print("")
	print(tabify(ranking))


def show_rt_index_global_latest(dataset_path):
	rt_list = parse_json_data(dataset_path)
	rt_list = select_data_bottom(rt_list)
	timestamp = pandas.to_datetime(rt_list["data"]).dt.date

	dataset = cleanup_rt_data(rt_list, None)

	#rt_list.drop(columns={"data", "data_IT_format", "note", "link"}, inplace=True)
	#rt_list.reset_index(drop=True, inplace=True)

	rt_list = rt_list.transpose().reset_index()
	rt_list.columns = ["REGIONE", "INDICE RT"]
	rt_list["INDICE RT"] = pandas.to_numeric(rt_list["INDICE RT"])
	rt_list.sort_values(by="INDICE RT", ascending=False, inplace=True)
	rt_list.reset_index(drop=True, inplace=True)
	rt_list.index += 1

	print(tabify(rt_list))


def show_rt_index_region(dataset_path, region):
	rt_list = parse_json_data(dataset_path)
	timestamp = pandas.to_datetime(rt_list["data"]).dt.date
	dataset = cleanup_rt_data(rt_list, region)

	print(tabify(rt_list))