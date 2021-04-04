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


import sys
from pathlib import Path
from colorama import Fore, Style

from report import *


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
		if (region == None):
			subtitle = "- ANDAMENTO NAZIONALE -"
			for n in range(0, len(subtitle)):
				print("=", end="")
			print("\n" + subtitle)
			for n in range(0, len(subtitle)):
				print("=", end="")
		else:
			subtitle = "- ANDAMENTO REGIONE " + region.value[1].upper() + " -"
			for n in range(0, len(subtitle)):
				print("=", end="")
			print("\n" + subtitle)
			for n in range(0, len(subtitle)):
				print("=", end="")
		print("\n")
		print("1) Visualizza report globale")
		print("2) Visualizza primi N giorni")
		print("3) Visualizza ultimi N giorni")
		print("4) Visualizza intervallo personalizzato")
		print("5) Indietro")
		option = input(">: ")
		if int(option) == 1:
			show_report(dataset_path, region)
		elif int(option) == 2:
			begin = input("Numero giorni: ")
			show_report(dataset_path, region, begin=begin)
		elif int(option) == 3:
			end = input("Numero giorni: ")
			show_report(dataset_path, region, end=end)
		elif int(option) == 4:
			begin = input("Giorno iniziale: ")
			end = input("Giorno finale: ")
			show_report(dataset_path, region, begin=begin, end=end)
		elif int(option) == 5:
			break
		else:
			print("Opzione selezionata non valida")


#
#	Brief:
#		Chooses which region should be used for data analysis.
#	Returns:
#		Selected region by user.
#
def select_region():
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
		option = input(">: ")
		if int(option) == 1:
			return Region.ABRUZZO
		elif int(option) == 2:
			return Region.BASILICATA
		elif int(option) == 3:
			return Region.CALABRIA
		elif int(option) == 4:
			return Region.CAMPANIA
		elif int(option) == 5:
			return Region.EMILIA_ROMAGNA
		elif int(option) == 6:
			return Region.FRIULI_VENEZIA_GIULIA
		elif int(option) == 7:
			return Region.LAZIO
		elif int(option) == 8:
			return Region.LIGURIA
		elif int(option) == 9:
			return Region.LOMBARDIA
		elif int(option) == 10:
			return Region.MARCHE
		elif int(option) == 11:
			return Region.MOLISE
		elif int(option) == 12:
			return Region.PA_BOLZANO
		elif int(option) == 13:
			return Region.PA_TRENTO
		elif int(option) == 14:
			return Region.PIEMONTE
		elif int(option) == 15:
			return Region.PUGLIA
		elif int(option) == 16:
			return Region.SARDEGNA
		elif int(option) == 17:
			return Region.SICILIA
		elif int(option) == 18:
			return Region.TOSCANA
		elif int(option) == 19:
			return Region.UMBRIA
		elif int(option) == 20:
			return Region.VALLE_D_AOSTA
		elif int(option) == 21:
			return Region.VENETO
		elif int(option) == 22:
			return None
		else:
			print("Opzione selezionata non valida")


#
#   Brief:
#       Prints a formatted welcome splash screen.
#
def print_splashscreen():
	print(Fore.LIGHTGREEN_EX + "")
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
	print(Style.RESET_ALL + "")


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

	national_data_path = Path(sys.argv[1] + "COVID-19/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv")
	regional_data_path = Path(sys.argv[1] + "COVID-19/dati-regioni/dpc-covid19-ita-regioni.csv")
	rt_data_path = Path(sys.argv[1] + "Indice-RT/File-JSON.json")

	print_splashscreen()

	while True:
		print("")
		print("1) Andamento nazionale")
		print("2) Andamento regionale")
		print("3) Classifica nazionale contagi")
		print("4) Indici RT")
		print("5) Uscita")
		option = input(">: ")
		if int(option) == 1:
			choose_report_type(national_data_path)
		elif int(option) == 2:
			region = select_region()
			if (region != None):
				choose_report_type(regional_data_path, region)
		elif int(option) == 3:
			show_national_ranking(regional_data_path)
		elif int(option) == 4:
			while True:
				print("")
				print("1) Valori RT attuali")
				print("2) Cronologia valori RT")
				print("3) Indietro")
				option_rt = input(">: ")
				if int(option_rt) == 1:
					show_rt_index_global_latest(rt_data_path)
				elif int(option_rt) == 2:
					region = select_region()
					if (region != None):
						show_rt_index_region(rt_data_path, region)
				elif int(option_rt) == 3:
					break
				else:
					print("Opzione selezionata non valida")
		elif int(option) == 5:
			break
		else:
			print("Opzione selezionata non valida")


if __name__ == "__main__":
	main()
