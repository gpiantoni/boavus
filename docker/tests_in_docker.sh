#!/bin/bash

id

echo $PATH

pip3 install --user -e .[test]
fsl5.0-flirt -version

~/make.py --tests
