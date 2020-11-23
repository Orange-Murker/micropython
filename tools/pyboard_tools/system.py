"""
Functions to be run from the PC
"""

import hashlib


def get_file_checksum(path):
    with open(path, "rb") as f:
        chunks = f.read()
        return hashlib.md5(chunks).hexdigest()
