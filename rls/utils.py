# coding: utf-8

import hashlib
import os


def hash_file(path, progress_hook=None, block_size=65535):
    with open(path, 'rb') as f:
        size = os.path.getsize(f.name)
        hasher = hashlib.md5()

        for block in iter(lambda: f.read(block_size), b''):
            hasher.update(block)
            if progress_hook:
                progress_hook(size, f.tell())
    return hasher.hexdigest()
