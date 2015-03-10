#!/bin/bash

set -e

function hash_item_track {
    if [ ! -f hashes/"$1".done ]; then
        echo $1
        (./hash_item.py $1 >hashes/"$1".txt 2>hashes/"$1".err.txt && touch hashes/"$1".done) || return 0
    fi
}

export -f hash_item_track
parallel --env hash_item_track --line-buffer -P5 hash_item_track < "$1"
