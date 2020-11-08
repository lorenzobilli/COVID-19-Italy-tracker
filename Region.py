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

from enum import Enum


#
#   Brief:
#       Enum used for regions. Integer values correspond to the internal regional ID used in the datasets.
#
class Region(Enum):
	ABRUZZO = 13, "Abruzzo"
	BASILICATA = 17, "Basilicata"
	CALABRIA = 18, "Calabria"
	CAMPANIA = 15, "Campania"
	EMILIA_ROMAGNA = 8, "Emilia-Romagna"
	FRIULI_VENEZIA_GIULIA = 6, "Friuli Venezia Giulia"
	LAZIO = 12, "Lazio"
	LIGURIA = 7, "Liguria"
	LOMBARDIA = 3, "Lombardia"
	MARCHE = 11, "Marche"
	MOLISE = 14, "Molise"
	PA_BOLZANO = 21, "P.A. Bolzano"
	PA_TRENTO = 22, "P.A. Trento"
	PIEMONTE = 1, "Piemonte"
	PUGLIA = 16, "Puglia"
	SARDEGNA = 20, "Sardegna"
	SICILIA = 19, "Sicilia"
	TOSCANA = 9, "Toscana"
	UMBRIA = 10, "Umbria"
	VALLE_D_AOSTA = 2, "Valle d'Aosta"
	VENETO = 5, "Veneto"
