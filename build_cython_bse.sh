#!/usr/bin/env bash

if [ -d "build" ]; then
  rm -rf build
fi

python setup.py --quiet build_ext --inplace
stubgen --parse-only --no-import --output . BSE.py
