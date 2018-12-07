BOAVUS
======
Functions and Workflows in Python to analyze electrocorticography (ECoG) and fMRI data.


Features
--------
- Pure Python

Installation
------------
Install won by running:

    pip install boavus

Requirements
------------
- Python 3.6
- bidso
- nipype
- nibabel
- wonambi

Testing
^^^^^^^ 
To run tests, you also need:
- pytest
- pytest-cov

Documentation
^^^^^^^^^^^^^
To generate the documentation, you also need:
- sphinx
- sphinx_rtd_theme

Dependencies
^^^^^^^^^^^^
To run some of the analysis workflow, boavus relies on external programs, which need to be installed separately.
The programs are:
- fsl
- freesurfer

Please, refer to the license for each of these programs.

Docker
------
Because it relies on some dependencies, there is a docker image available at `docker hub<https://hub.docker.com/gpiantoni/boavus>`_.
To run inside docker, do::

   ANALYSIS_DIR=/path/to/analysis/dir
   docker pull gpiantoni/boavus
   docker -i -t -v $ANALYSIS_DIR:/home/neuro -w /home/neuro --user neuro gpiantoni/boavus bash

Then you can run the commands inside docker.

License
-------
The project is licensed under the MIT license.
