#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
pushd .
cd $DIR
cat app.py | grep -Pv "^\s*#" > app.bak
mv app.bak app.py
cat handlers.py | grep -Pv "^\s*#" > handlers.bak
mv handlers.bak handlers.py
popd
