"""
Contains functions to be executed on the pyboard (never locally!).
These functions are intended to be transmitted line-by-line, using source
inspection.
"""


def uos_mkdir_safe(directory):
    """Safely create a directory

    Based on uos.mkdir(), only the error about the folder already existing
    is caught.
    """
    import uos
    import errno

    try:
        uos.mkdir(directory)
    except OSError as err:
        if err.args[0] != errno.EEXIST:
            raise err  # Ignore any other errors


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


def uos_file_checksums():
    """Print a list of all files and their checksums"""

    import uos
    import uhashlib
    import ubinascii

    def get_checksum(path):
        with open(path, 'rb') as f:
            chunks = f.read()
            digest = uhashlib.md5(chunks).digest()  # <class 'bytes'>
            digest_hex = ubinascii.hexlify(digest)  # <class 'bytes'> (still)
            return digest_hex.decode()  # Return as string

    def list_dir(directory):
        for name, is_folder, inode, size in uos.ilistdir(directory):

            path = directory + '/' + name

            if is_folder == 0x4000:
                list_dir(path)
            else:
                if name in ['pybcdc.inf', 'README.txt']:
                    continue  # Skip system files
                checksum = get_checksum(path)
                print(path + ":" + checksum)

    list_dir('.')
