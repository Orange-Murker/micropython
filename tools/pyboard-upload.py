#!/bin/python3

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
    
    def fs_mkdir_s(self, directory):
        """Make a directory but do nothing if it already exists (safely)

        Made after fs_mkdir() in Pyboard
        """
        self.exec_("import uos\ntry:\n    uos.mkdir('%s')"
                   "\nexcept OSError:\n    pass" % directory)


def find_ports():
    """Get list of ports with the index of the suggested port"""

    ports = list_ports.comports()

    hints = ["pyboard", "stm", "st-link"]
    i_hint = len(ports) - 1  # Last one is likely what we're looking for
    found = False

    for hint in hints:
        for i_port, port in enumerate(ports):
            if port.description.lower().find(hint) >= 0:
                i_hint = i_port
                found = True
                break
        if found:
            break

    return ports, i_hint


def select_port(ports, i_hint=0):
    """Ask the user which port he wants to use"""

    print("Devices found:")
    for i, port in enumerate(ports):
        print("[{}]".format(i), port)

    selected_port = -1

    while not (0 <= selected_port < len(ports)):
        query = "Choose device [{}]: ".format(i_hint)
        selected_port = input(query)
        try:
            selected_port = int(selected_port)
        except ValueError:
            selected_port = i_hint

    return ports[selected_port]


def main():
    """Main function, executed when running file like a script"""

    ports, i_hint = find_ports()

    if not ports:
        print("No serial devices found")
        return 1

    port = select_port(ports, i_hint)

    # Connect
    pyb = PyboardExtended(port.device, 115200)

    # Files to be copied
    files = glob.glob("**/*py", recursive=True)

    # Start copy
    print("Connecting to REPL...")
    pyb.enter_raw_repl()

    for file in files:
        print("Moving ", file)

        directory = os.path.dirname(file)
        if directory:
            pyb.fs_mkdir_s(directory)

        attempts = 0
        done = False

        while not done and attempts < 10:  # Include attempts limit for safety
            try:
                pyb.fs_put(file, file)
                done = True  # Successful
            except PyboardError as err:
                attempts += 1  # Another failure
                if attempts >= 5:
                    raise PyboardError(
                        "Failed to upload `{}` in {} attempts".format(
                            file, attempts)) from err
                # Throw error again if it keeps failing

    pyb.exit_raw_repl()
    pyb.close()

    print("Done")

    return 0


if __name__ == "__main__":

    code = main()

    exit(code)
