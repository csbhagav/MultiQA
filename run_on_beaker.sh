#!/usr/bin/env bash

set -e
set -x

SHA=`git rev-parse HEAD`
IMAGE_NAME="mrqa-train-${SHA}"
EXPT_FILE=mrqa.yml

export IMAGE_NAME=${IMAGE_NAME}

docker build -t ${IMAGE_NAME} .
bp=$(beaker image create --quiet ${IMAGE_NAME})

echo ${bp}
export TRAIN_DATASETS=drop
export TEST_DATASETS=drop

expt=$(beaker experiment create --file ${EXPT_FILE} --quiet)