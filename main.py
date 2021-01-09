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

	national_data_path = Path(sys.argv[1] + "/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv")
	regional_data_path = Path(sys.argv[1] + "/dati-regioni/dpc-covid19-ita-regioni.csv")

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
			print("Funzione attualmente non implementata")
		elif int(option) == 5:
			break
		else:
			print("Opzione selezionata non valida")


if __name__ == "__main__":
	main()
