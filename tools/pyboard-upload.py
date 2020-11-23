#!/bin/python3

"""
This basic script uploads all .py files and files in sub-folders to the
board through the serial REPL.

It should be called from your project directory like:

    >> python 'C:\Program Files\micropython\pyboard-upload.py'

"""

from serial.tools import list_ports
from pyboard import Pyboard, PyboardError, stdout_write_bytes
import glob
import os
import inspect
import argparse


def uos_remove_all_files():
    """Recursively remove all files and directories"""
    import uos

    def rmdir_recursive(directory):
        for name, is_folder, inode, size in uos.ilistdir(directory):

            path = directory + '/' + name

            if is_folder == 0x4000:
                rmdir_recursive(path)
                uos.rmdir(path)
            else:
                if name in ['pybcdc.inf', 'README.txt']:
                    continue  # Keep
                uos.remove(path)

    rmdir_recursive('.')


class PyboardExtended(Pyboard):
    """Extends the original Pyboard class"""
    
    def fs_mkdir_s(self, directory):
        """Make a directory but do nothing if it already exists (safely)

        Made after fs_mkdir() in Pyboard
        """
        self.exec_("import uos\ntry:\n    uos.mkdir('%s')"
                   "\nexcept OSError:\n    pass" % directory)

    def fs_remove_all(self):
        """Remove all files on the file system

        Except the standard 'README.txt' and 'pybcdc.inf'
        """

        # `commands` will include the function name, we need to call it too
        commands = inspect.getsource(uos_remove_all_files)

        self.exec_(commands)
        self.exec_("uos_remove_all_files()", stdout_write_bytes)

    def fs_put_files(self, files):
        """Upload a list of files

        Directories will be created for files if needed (unlike the basic
        `fs_put`).
        The files list should point relatively to paths as they exist on the
        PC filesystem. Those files will be created on the pyboard with the
        same structure.

        :param files: List of relative file paths
        """

        # Copy files
        for file in files:

            file_name = os.path.basename(file)
            if file_name in ['pyboard.py', 'pyboard-upload.py']:
                continue  # Prevent uploading of itself (only relevant if
                # the script was not used correctly in the first place)

            print("Moving ", file)

            target = file.replace('\\', '/')  # Replace Windows separator

            directory = os.path.dirname(target)
            if directory:
                self.fs_mkdir_s(directory)

            attempts = 0
            done = False

            while not done:
                try:
                    self.fs_put(file, target)
                    done = True  # Successful
                except PyboardError as err:
                    attempts += 1  # Another failure
                    if attempts >= 5:
                        raise PyboardError(
                            "Failed to upload `{}` in {} attempts".format(
                                target, attempts)) from err
                    # Throw error again if it keeps failing

    def __enter__(self):
        """Run at the start of `with ...:`"""
        self.enter_raw_repl()  # Enter raw REPL by default

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Run at the end of `with ...:`"""
        self.exit_raw_repl()
        self.close()  # Close connection


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

        if args.clear_fs:
            print('Clearing filesystem...')
            pyb.fs_remove_all()

        pyb.fs_put_files(files)

    print("Done")

    return 0


if __name__ == "__main__":

    code = main()

    exit(code)
