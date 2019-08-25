#!/usr/bin/env sh

set -o errexit
set -o nounset

cmd="$*"

# Evaluating passed command:
exec $cmd
