#!/bin/bash

# source this file to put blamethrower in your path and PYTHONPATH.
dir="$(dirname "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")")"
export PATH=$PATH:"$dir/bin"
export PYTHONPATH=$PYTHONPATH:"$dir"
