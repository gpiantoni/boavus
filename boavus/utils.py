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


def mkdir_task(base_path, task):

    feat_path = base_path / ('sub-' + task.subject)
    feat_path.mkdir(exist_ok=True)
    if hasattr(task, 'session'):
        feat_path = feat_path / ('ses-' + task.session)
        feat_path.mkdir(exist_ok=True)

    feat_path = feat_path / task.modality
    feat_path.mkdir(exist_ok=True)

    return feat_path


def replace_extension(filename, suffix):
    if isinstance(filename, str):
        return filename.split('.')[0] + suffix
    else:
        return filename.parent / (filename.name.split('.')[0] + suffix)


def add_underscore(filename, suffix):
    if isinstance(filename, str):
        return filename + '_' + suffix
    else:
        return filename.parent / (filename.name + '_' + suffix)


def replace_underscore(filename, suffix):
    if isinstance(filename, str):
        return '_'.join(filename.split('_')[:-1] + [suffix, ])
    else:
        return filename.parent / ('_'.join(filename.name.split('_')[:-1] + [suffix, ]))


def remove_underscore(filename):
    if isinstance(filename, str):
        return '_'.join(filename.split('_')[:-1])
    else:
        return filename.parent / ('_'.join(filename.name.split('_')[:-1]))


def read_tsv(filename):
    filename = Path(filename)
    with filename.open() as f:
        hdr = f.readline()
        tsv = []
        for l in f:
            d = {k.strip(): v.strip() for k, v in zip(hdr.split('\t'), l.split('\t'))}
            tsv.append(d)
    return tsv
