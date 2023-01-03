#!/usr/bin/env powershell

if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}

python setup.py --quiet build_ext --inplace
