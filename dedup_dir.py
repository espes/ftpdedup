#!/usr/bin/env python2.7

import os
import sys
import json
import httplib
import platform
import subprocess
from collections import defaultdict

if platform.system() == 'Darwin':
    SHA256SUM_CMD = "gsha256sum"
else:
    SHA256SUM_CMD = "sha256sum"

DEDUP_SERVER = "localhost:8080"

def dedup_dir(path, dry_run=False):
    assert os.path.isdir(path)

    print "Hashing all files in %s..." % path
    p = subprocess.Popen(
        ["find", path, "-type", "f", "-exec", SHA256SUM_CMD, "{}", ";"],
        stdout=subprocess.PIPE)

    dedup_hashes = defaultdict(list)
    for line in iter(p.stdout.readline, ''):
        hash_, path = line[:-1].split("  ", 1)
        hash_raw = hash_.decode("hex")
        assert len(hash_raw) == 32
        assert os.path.isfile(path)
        
        # Don't bother deduplicating small files
        if os.path.getsize(path) >= 256:
            dedup_hashes[hash_raw].append(path)

    assert p.wait() == 0

    print "Sending %d hashes to deduplication server..." % len(dedup_hashes)
    con = httplib.HTTPConnection(DEDUP_SERVER)
    con.request("POST", "/dedup", ''.join(dedup_hashes.iterkeys()))
    res = con.getresponse()

    dedup = json.load(res)
    
    if not dry_run:
        print "Deleting duplicate files..."
    
    duplicates = 0
    for k, v in dedup.iteritems():
        k = k.decode("hex")
        for path in dedup_hashes[k]:
            if dry_run:
                print "Duplicate: %s" % path
            else:
                print "Deleting " + path
                os.remove(path)

            dedup_path = path + ".archiveteam-dedup"
            print "Creating %s" % dedup_path
            with open(dedup_path, "w") as f:
                json.dump(v, f)

            duplicates += 1

    print "Deduplicated %d files" % duplicates


def main():
    if len(sys.argv) == 2:
        path = sys.argv[1]
        dry_run = False
    elif len(sys.argv) == 3 and sys.argv[1] == "-t":
        path = sys.argv[2]
        dry_run = True
    else:
        print "usage: %s [-t] dir" % sys.argv[0]
        sys.exit(1)

    dedup_dir(path, dry_run)

if __name__ == "__main__":
    main()
