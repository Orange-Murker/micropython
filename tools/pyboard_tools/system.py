"""
Functions to be run from the PC
"""

import hashlib
import os


def get_file_checksum(path):
    """Return the MD5 checksum of a file, as hex string"""
    with open(path, "rb") as f:
        chunks = f.read()
        return hashlib.md5(chunks).hexdigest()


def split_path_components(path):
    """Split a path into a list of its components"""

    path = os.path.normpath(path)
    return path.split(os.sep)
