from pathlib import Path
from os import environ, pathsep

def _remove_python3_from_PATH(path):
    return pathsep.join(x for x in path.split(pathsep) if 'miniconda' not in x and 'venv/bin' not in x)


ENVIRON = {
    'FSLDIR': '/usr/share/fsl/5.0',
    'FSLOUTPUTTYPE': 'NIFTI_GZ',
    'PATH': '/usr/share/fsl/5.0/bin' + pathsep + _remove_python3_from_PATH(environ.get('PATH', '')),
    'LD_LIBRARY_PATH': '/usr/lib/fsl/5.0' + pathsep + environ.get('LD_LIBRARY_PATH', ''),
    }
ENVIRON = {**environ, **ENVIRON}