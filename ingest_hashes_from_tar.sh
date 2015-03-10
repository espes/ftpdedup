#!/bin/bash

set -e

gtar xaf "$1" --to-command=cat | python ingest_hashes.py -
