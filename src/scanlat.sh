#!/bin/sh

# Usage:
# bash scanlat.sh input_text_file is_macronized_input
#
# where input_text_file is in the subdirectory ../input

mkdir ../output 2> ../mkdir_error
rm ../mkdir_error

echo 'Input text:             ' ../input/$1 '
'

if [[ $2 == "" ]]; then
    echo 'Getting natural vowel quantities...'
    python parse.py <../input/$1 >../output/naturalized_$1 2>../output/log_$1

    echo 'Getting positional vowel quantities...'
    python positional.py <../output/naturalized_$1 >../output/scanned_$1 2>>../output/log_$1

    echo '
Done scanning.

Naturalized text:       ' ../output/naturalized_$1

else
    echo 'Input already macronized with natural vowel quantities.'
    echo 'Getting positional vowel quantities...'
    python positional.py <../input/$1 >../output/scanned_$1 2>../output/log_$1
    echo '
Done scanning.
'
fi

echo 'Scanned text:           ' ../output/scanned_$1 '
Progress/error log:     ' ../output/log_$1

rm -r __pycache__
