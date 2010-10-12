#!/usr/bin/env python
from tempfile import mkstemp
from urllib import urlretrieve
from os import unlink
from hashlib import md5

import parse_files
from tarfile import open as tarfile_open, TAR_GZIPPED

def download_and_parse(url, expected_checksum):
    handle, filename = mkstemp(prefix="fuss_",suffix=".tgz")
    urlretrieve(url, filename)
    f = open(filename, "r")
    contents = f.read()
    f.close()
    checksum = md5()
    checksum.update(contents)
    download_checksum = checksum.hexdigest()
    assert(download_checksum == expected_checksum)
    parse_files.FOREIGN_MUD_TARFILE = tarfile_open(filename)
    doc = parse_files.parse_mud_root_to_dom()
    unlink(filename)
    return doc
