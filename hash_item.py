#!/usr/bin/env python2.7

import sys
import json
import pprint
import urllib
import platform
import subprocess

if platform.system() == 'Darwin':
	TAR_CMD = "gtar"
	SHA256SUM_CMD = "gsha256sum"
else:
	TAR_CMD = "tar"
	SHA256SUM_CMD = "sha256sum"

def process_hashes(p):
	for line in iter(p.stdout.readline, ''):
		filename, size, hash_ = line[:-1].rsplit(' ', 2)
		yield filename, size, hash_

	r = p.wait()
	if r != 0:
		raise Exception

def tar_hasher(f, extra_flags=""):
	hash_command = 'bash -c "echo -n \\"\\$TAR_REALNAME \\$TAR_SIZE \\"; %s | sed \\"s/  -$//\\""' % SHA256SUM_CMD
	p = subprocess.Popen([TAR_CMD, "xf"+extra_flags, "-", "--to-command", hash_command],
		stdin=f, stdout=subprocess.PIPE)

	for v in process_hashes(p): yield v

def libarchive_hasher(f):
	# run python-libarchive in a separate process because I don't trust it.
	# without the cat on linux libarchive thinks it's seekable...
	p = subprocess.Popen(["cat | python -u libarchive_hasher.py"], shell=True,
		stdin=f, stdout=subprocess.PIPE)

	for v in process_hashes(p): yield v

TAR_EXTS = [
	'.tar.gz',
	'.tar.bz2',
	'.tar.xz',
	'.tgz',
	'.tar',
]

TAR_FLAGS = {
	'.tar.gz': 'z',
	'.tar.bz2': 'j',
	'.tar.xz': 'J',
	'.tgz': 'z',
	'.tar': '',
}

ARCHIVE_EXTS = TAR_EXTS + [
	'.zip',
	#'.7z', #7z needs to be seekable? -_-
]

def hash_item_file(item, name):
	url = "http://archive.org/download/%s/%s" % (item, name)
	url_f = urllib.urlopen(url)
	
	tar_ext = filter(name.lower().endswith, TAR_EXTS)
	if tar_ext:
		itr = tar_hasher(url_f, TAR_FLAGS[tar_ext[0]])
	else:
		itr = libarchive_hasher(url_f)

	for filename, size, hash_ in itr:
		print repr([item, name, filename, size, hash_])

def hash_item(item):
	metadata_f = urllib.urlopen("http://archive.org/metadata/%s" % item)
	metadata = json.load(metadata_f)

	archive_files = []
	for f in metadata['files']:
		for ext in ARCHIVE_EXTS:
			if f['name'].lower().endswith(ext):
				archive_files.append(f['name'])

	for name in archive_files:
		hash_item_file(item, name)

def main():
	hash_item(sys.argv[1])
	
if __name__ == "__main__":
	main()