#!/usr/bin/env python2.7

import os
import hashlib
import platform
import traceback

import locale
locale.setlocale(locale.LC_ALL, '')

if platform.system() == 'Darwin':
	os.environ['LA_LIBRARY_FILEPATH'] = '/usr/local/Cellar/libarchive/3.1.2/lib/libarchive.dylib'
elif platform.system() == 'Linux':
	os.environ['LA_LIBRARY_FILEPATH'] = '/usr/lib/x86_64-linux-gnu/libarchive.so.13'

import libarchive.public

with libarchive.public.file_reader('/dev/stdin') as e:
	try:
		for entry in e:
			if entry.size == 0: continue
			m = hashlib.sha256()
			for b in entry.get_blocks():
				m.update(b)
			print "%s %d %s" % (str(entry), entry.size, m.hexdigest())
	except:
		# libarchive doesn't deal with exceptions properly
		# (it finishes loading the whole file?)
		traceback.print_exc()
		os._exit(1)
