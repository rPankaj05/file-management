#!/bin/bash

# Define the input file and the number of lines per chunk
input_file="zouk_point.csv"
lines_per_chunk=1000

# Extract the header
header=$(head -n 1 $input_file)

# Split the file, excluding the header, and save chunks with header
tail -n +2 $input_file | split -l $lines_per_chunk - chunk_
for file in chunk_*
do
    (echo "$header" && cat "$file") > tmp_file && mv tmp_file "$file.csv"
done