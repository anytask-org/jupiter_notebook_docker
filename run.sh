#!/bin/sh

set -x

nohup python3 ./gatekeeper.py &
jupyter notebook
