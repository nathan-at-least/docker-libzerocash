#!/bin/bash

set -eux

EXTRACTION='extraction'
DESTNAME="$1"
ARCHIVE="$2"

mkdir "$EXTRACTION"
cd "$EXTRACTION"

if echo "$ARCHIVE" | grep -Eq '\.tar\.(gz|bz2)$'
then
    tar -xf "../${ARCHIVE}"
elif echo "$ARCHIVE" | grep -q '\.zip$'
then
    unzip -q "../${ARCHIVE}"
else
    echo "UNKNOWN ARCHIVE FORMAT: $ARCHIVE"
    exit 1
fi

SPLODECOUNT="$(ls | wc -l)"

cd ..

if [ "$SPLODECOUNT" -eq 1 ]
then
    mv -v "${EXTRACTION}"/* "$DESTNAME"
    rmdir "$EXTRACTION"
else
    mv -v "$EXTRACTION" "$DESTNAME"
fi
