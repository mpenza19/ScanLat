#!/bin/sh

# Usage:
# bash scanlat.sh input_text_file is_macronized_input
#
# where input_text_file is in the subdirectory input/

# capture workspace path
WORKSPACE=$(pwd)

# set IO and log file paths
INPUT_PATH="${WORKSPACE}/input/${INPUT_FILE}"
RAWPARSE_PATH="${WORKSPACE}/output/${INPUT_FILE%.txt}-rawparse.txt"
NATURALIZED_PATH="${WORKSPACE}/output/${INPUT_FILE%.txt}-naturalized.txt"
SCANNED_PATH="${WORKSPACE}/output/${INPUT_FILE%.txt}-scanned.txt"
LOG_PATH="${WORKSPACE}/output/${INPUT_FILE%.txt}-log.txt"

# capture script paths
PARSE_SCRIPT="${WORKSPACE}/src/parse.py"
POSITIONAL_SCRIPT="${WORKSPACE}/src/positional.py"

# setup output dir
mkdir ${WORKSPACE}/output 2> /dev/null


echo "Input text:     ${INPUT_PATH}"

if [[ "$IS_MACRONIZED_INPUT" != "true" && "$IS_MACRONIZED_INPUT" != "yes" ]]; then
    echo 'Getting natural vowel quantities...'
    python ${PARSE_SCRIPT} ${RAWPARSE_PATH} \
            < ${INPUT_PATH} > ${NATURALIZED_PATH} 2> ${LOG_PATH}

    echo 'Getting positional vowel quantities...'
    python ${POSITIONAL_SCRIPT} \
            < ${NATURALIZED_PATH} > ${SCANNED_PATH} 2>> ${LOG_PATH}

    echo "Done scanning."
    echo "Naturalized text:     ${NATURALIZED_PATH}"

else
    echo 'Input already macronized with natural vowel quantities.'
    echo 'Getting positional vowel quantities...'
    python ${POSITIONAL_SCRIPT} \
            < ${INPUT_PATH} > ${SCANNED_PATH} 2> ${LOG_PATH}

    echo "Done scanning."
fi

echo "Scanned text:     ${SCANNED_PATH}"
echo "Progress/error log:     ${LOG_PATH}"


# Show results
echo "SCANNED OUTPUT"
cat ${SCANNED_PATH}
echo

# Show log
echo "ERROR LOG"
cat ${LOG_PATH}

# Cleanup
rm -r ${WORKSPACE}/src/__pycache__
