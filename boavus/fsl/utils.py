from os import environ, pathsep

def _remove_python3_from_PATH(path):
    return pathsep.join(x for x in path.split(pathsep) if 'miniconda' not in x and 'venv/bin' not in x)


ENVIRON = {
    'FSLDIR': '/usr/share/fsl/5.0',
    'FSLOUTPUTTYPE': 'NIFTI_GZ',  # depends on COMPRESSED
    'PATH': '/usr/share/fsl/5.0/bin' + pathsep + _remove_python3_from_PATH(environ.get('PATH', '')),
    'LD_LIBRARY_PATH': '/usr/lib/fsl/5.0' + pathsep + environ.get('LD_LIBRARY_PATH', ''),
    }
ENVIRON = {**environ, **ENVIRON}


def mkdir_task(base_path, task):

    feat_path = base_path / ('sub-' + task.subject)
    feat_path.mkdir(exist_ok=True)
    if task.session is not None:
        feat_path = feat_path / ('ses-' + task.session)
        feat_path.mkdir(exist_ok=True)

    feat_path = feat_path / task.modality
    feat_path.mkdir(exist_ok=True)

    return feat_path
