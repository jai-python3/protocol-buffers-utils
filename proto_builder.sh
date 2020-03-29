#!/usr/bin/env bash
DIRNAME=$(dirname "$0")
source $DIRNAME/venv/bin/activate
python $DIRNAME/proto_builder.py "$@"