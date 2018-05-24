#!/bin/sh

# Usage:
# bash scansion.sh input_text_file is_macronized_input

mkdir output 2> mkdir_error
rm mkdir_error

if [[ $2 == "" ]]; then
    echo 'Getting natural vowel quantities.'
    python2 parse.py <$1 >output/natural_text_$1 2>output/log_$1

    echo 'Getting positional vowel quantities.'
    python2 positional.py <output/natural_text_$1 >output/scanned_$1 2>>output/log_$1
else
    echo 'Input already macronized with natural vowel quantities.'
    echo 'Getting positional vowel quantities.'
    python2 positional.py <$1 >output/scanned_$1 2>output/log_$1
fi

echo 'Done.
Scanned text:      ' output/scanned_$1 '
Progress/error log: ' output/log_$1