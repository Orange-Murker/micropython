"""
Contains the extended pyboard class.

Perhaps some or all of these methods will be ported into the official
pyboard class. When this has happened, this extension will be redundant.
"""

import os
import inspect

from .system import get_file_checksum, split_path_components
from .micropython import uos_file_checksums, uos_remove_all_files, \
    uos_mkdir_safe
from pyboard import Pyboard, PyboardError, stdout_write_bytes


def bytes_to_string(bytes_list):
    """Convert `exec_` output to string"""
    bytes_list = bytes_list.replace(b"\x04", b"")
    return bytes_list.decode()


class PyboardExtended(Pyboard):
    """Extends the original Pyboard class"""

    def execute_function(self, func, *args, data_consumer=None):
        """Execute a function on the pyboard

        The function source code is send line-by-line, after which
        the function is called.

        :param func: Handle of the function to be transmitted
        :param data_consumer: Callback to handle returned bytes
        """
        # `commands` will include the function name, we need to call it too
        commands = inspect.getsource(func)

        self.exec_(commands)

        call_str = func.__name__ + '('

        first = True
        for argument in args:
            if first:
                first = False
            else:
                call_str += ", "

            if isinstance(argument, str):
                call_str += "'" + argument + "'"
            else:
                call_str += argument

        call_str += ')'

        data = self.exec_(call_str, data_consumer)
        return bytes_to_string(data)

    def fs_mkdir_s(self, directory, recursive=True):
        """Make a directory but do nothing if it already exists (safely)

        Made after fs_mkdir() in Pyboard

        :param directory: Directory to be created
        :param recursive: If true, directory can also be a path,
            all intermediate folders will be created too
        """

        if not recursive:
            self.execute_function(uos_mkdir_safe, directory)
            return  # Done

        path = ''  # Incrementally build path
        for component in split_path_components(directory):
            if path:
                path += '/'
            path += component
            self.execute_function(uos_mkdir_safe, path)

    def fs_remove_all(self):
        """Remove all files on the file system

        Except the standard 'README.txt' and 'pybcdc.inf'
        """
        return self.execute_function(uos_remove_all_files,
                                     data_consumer=stdout_write_bytes)

    def fs_put_file(self, file, retries=5):
        """Upload a single file to the pyboard

        Directories will be created for files if needed (unlike the basic
        `fs_put`).
        The file path should be relative to paths as they exist on the
        PC filesystem. Those files will be created on the pyboard with the
        same structure.

        :param file: File to be uploaded, including relative path
        :param retries: File uploads tend to randomly fail, so will catch
            any errors and re-try a failed upload for this number of times
        """
        file_name = os.path.basename(file)
        if file_name in ['pyboard.py', 'pyboard_upload.py']:
            return  # Prevent uploading of itself (only relevant if
            # the script was not used correctly in the first place)

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
                if attempts >= retries:
                    raise PyboardError(
                        "Failed to upload `{}` in {} attempts".format(
                            target, attempts)) from err
                # Throw error again if it keeps failing

    def fs_put_files(self, files, verbose=True):
        """Upload a list of files

        :param files: List of relative file paths
        """

        # Copy files
        for file in files:
            if verbose:
                print('Copying:', file)
            self.fs_put_file(file)

    def fs_rsync(self, files, verbose=True):
        """Synchronize a list of local files to the pyboard

        Any remote files that are not in the local set will be removed. Only
        files that are different will be uploaded.
        The files list should contain relative paths. The same structure will
        be created on the pyboard.

        :param files: List of relative file paths
        :param verbose: Set to `True` to print info
        """
        files_remote = self.get_file_checksums()

        # Create list of tuples of local files, and replace "\" by "/"
        files_local = {}
        for file in files:
            file_unix = file.replace("\\", "/")
            files_local[file_unix] = get_file_checksum(file)

        for file_remote in files_remote.keys():
            if file_remote in files_local:
                continue
            if verbose:
                print('Removing remote:', file_remote)
            self.fs_rm(file_remote)  # Not in current target

        for file_local, checksum_local in files_local.items():
            if file_local in files_remote:
                if checksum_local == files_remote[file_local]:
                    continue  # File already exists and is identical
            if verbose:
                print('Copying:', file_local)
            self.fs_put_file(file_local)

    def get_file_checksums(self):
        commands = inspect.getsource(uos_file_checksums)

        self.exec_(commands)
        data_bytes = self.exec_("uos_file_checksums()")
        data = bytes_to_string(data_bytes)

        # Remove leading `./` from path
        files_list = [line[2:] for line in data.splitlines()]

        files = {}

        for line in files_list:
            path, checksum = line.split(":")
            files[path] = checksum

        return files

    def __enter__(self):
        """Run at the start of `with ...:`"""
        self.enter_raw_repl()  # Enter raw REPL by default

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Run at the end of `with ...:`"""
        self.exit_raw_repl()
        self.close()  # Close connection
