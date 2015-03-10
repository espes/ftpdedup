#!/usr/bin/env python2.7

import sys
import time
import json
import fileinput
from ast import literal_eval

import leveldb

def ingest_hashes(db, f):
	num_files = 0
	skipped_files = 0
	
	last_time = time.time()

	for l in f:
		file_info_list = literal_eval(l)
		file_size = None
		if len(file_info_list) == 4:
			item, item_file, archive_file, hash_ = file_info_list
		elif len(file_info_list) == 5:
			item, item_file, archive_file, file_size, hash_ = file_info_list
		else:
			assert False

		if file_size is not None:
			file_size = int(file_size)
		hash_raw = hash_.decode("hex")

		if num_files % 10000 == 0:
			t = time.time()
			print num_files, t-last_time
			last_time = t

		num_files += 1

		try:
			archive_file = archive_file.decode("latin1")
		except UnicodeEncodeError:
			pass

		try:
			existing_v = db.Get(hash_raw)
			skipped_files += 1
		except KeyError:
			db.Put(hash_raw,
				json.dumps(
					[item, item_file, archive_file, file_size]))

	print "done", num_files, skipped_files
		

def main():
	db = leveldb.LevelDB(sys.argv[1])
	ingest_hashes(db, fileinput.input())


if __name__ == "__main__":
	main()
