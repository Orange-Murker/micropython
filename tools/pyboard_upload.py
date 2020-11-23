#!/bin/python3

"""
This basic script uploads all .py files and files in sub-folders to the
board through the serial REPL.

It should be called from your project directory like:

    >> python 'C:\Program Files\micropython\pyboard_upload.py'

Use `--help` to get information about CLI arguments.
"""

from serial.tools import list_ports
import glob
import argparse

from pyboard_tools.pyboard import PyboardExtended


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


def command_line_interface():
    """Use the parser modules to define a CLI"""

    parser = argparse.ArgumentParser(
        description='Upload python program recursively over serial to '
                    'micropython board'
    )
    parser.add_argument('-p', '--port', default=None,
                        help='Specify the COM port and skip the selection '
                             'prompt (user is prompted by default)')
    parser.add_argument('-c', '--clear_fs', default=True, type=bool,
                        help='Set to False to skip clearing the file system '
                             'first (True by default)')
    return parser.parse_args()


def main():
    """Main function, executed when running file like a script"""

    args = command_line_interface()  # Get sys args

    if args.port is None:

        ports, i_hint = find_ports()

        if not ports:
            print("No serial devices found")
            return 1

        port = select_port(ports, i_hint)
        device = port.device
    else:
        device = args.port

    # Connect
    pyb = PyboardExtended(device, 115200)

    # Files to be copied
    files = glob.glob("**/*py", recursive=True)

    if not files:
        print("No files found to upload")
        return 2

    # Connect
    print("Connecting to REPL...")
    with pyb:

        print('Performing sync...')
        pyb.fs_rsync(files)

    print("Done")

    return 0


if __name__ == "__main__":

    code = main()

    exit(code)
