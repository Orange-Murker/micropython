#!/bin/pyhton3

#
# This basic script uploads all .py files and files in sub-folders to
# the board through the serial REPL.
#

from serial.tools import list_ports
from pyboard import Pyboard, PyboardError
import glob
import os


class PyboardExtended(Pyboard):
	"""Extends the original Pyboard class"""
	
	def fs_mkdir_s(self, dir):
		"""
		Make a directory but do nothing if it already exists (safely)

		Made after fs_mkdir() in Pyboard
		"""
		self.exec_("import uos\ntry:\n    uos.mkdir('%s')\nexcept OSError:\n    pass" % dir)


def find_ports():
	"""Get list of ports with the index of the suggested port"""

	ports = list_ports.comports()

	hints = ["pyboard", "stm", "st-link"]
	i_hint = 0
	found = False

	for hint in hints:
		for i_port, port in enumerate(ports):

			if port.description.lower().find(hint) >= 0:
				print("Found:", i_port)
				i_hint = i_port
				found = True
				break
		if found:
			break

	return ports, i_hint


def select_port(ports, i_hint = 0):
	"""Ask the user which port he wants to use"""

	print("Devices found:")
	for i, port in enumerate(ports):
		print("[{}]".format(i), port)

	selected_port = -1

	while not (selected_port >= 0 and selected_port < len(ports)):
		selected_port = input("Choose device [{}]: ".format(i_hint))
		try:
			selected_port = int(selected_port)
		except ValueError:
			selected_port = i_hint

	return ports[selected_port]


ports, i_hint = find_ports()

port = select_port(ports, i_hint)

# Connect
pyb = PyboardExtended(port.device, 115200)

# Files to be copied
files = glob.glob("**/*py", recursive=True)


# Start copy
pyb.enter_raw_repl()

for file in files:
	print("Moving ", file)

	dir = os.path.dirname(file)
	if dir:
		pyb.fs_mkdir_s(dir)


	pyb.fs_put(file, file)

pyb.exit_raw_repl()

pyb.close()

print("Done")
