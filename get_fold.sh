#!/usr/bin/env bash

find ./*.zip || rm ./*.zip
cd paysimplus/outputs/
folder=$(awk -F',' 'END { print $1 }' summary.csv)
name="result_$folder.zip"

# Zip
zip -r "$name" "$folder"
mv "$name" ../../
cd ../../
