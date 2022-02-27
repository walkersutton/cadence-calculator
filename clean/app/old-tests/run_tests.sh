#!/bin/bash

cd "${0%/*}"

for test_file in $(ls test_*); do
    echo running $test_file...
    python $test_file
done
