#!/bin/bash

set -e

cd "$(git rev-parse --show-toplevel)"
git fetch -p
git reset --hard origin/master
pip install -r requirements.txt
(
    cd scripts
    ./install-services.sh
)
