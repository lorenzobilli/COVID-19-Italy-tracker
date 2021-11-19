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


import multiprocessing
import tabulate


#
#   Brief:
#       Number of processes used by the parallelized sections of the program.
#
cpus = multiprocessing.cpu_count()


#
#   Brief:
#       Quickly tabulates ready-to-be-printed data.
#   Parameters:
#       - dataframe: Data to be tabulated.
#   Returns:
#       Formatted data in tabular, printable form.
#
def tabify(dataframe):
	return tabulate.tabulate(dataframe, headers="keys", tablefmt="pretty", numalign="center", stralign="center")
