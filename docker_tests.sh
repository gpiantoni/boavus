#!/bin/bash

echo $PATH
echo $FSLDIR

recon-all

pip3 install --user -e .
fsl5.0-flirt -version
pip3 install --user pytest pytest-cov coverage

echo $PATH

pytest --version

~/make.py -t
