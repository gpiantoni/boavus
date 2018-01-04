from bidso.utils import replace_underscore, find_root, remove_underscore
from os import environ, pathsep, setpgrp
from pathlib import Path
from nibabel import load as niload
from subprocess import Popen, run


def _remove_python3_from_PATH(path):
    return pathsep.join(x for x in path.split(pathsep) if 'miniconda' not in x and 'venv/bin' not in x)


ENVIRON = {
    'FSLDIR': '/usr/share/fsl/5.0',
    'FSLOUTPUTTYPE': 'NIFTI_GZ',  # depends on COMPRESSED
    'PATH': '/usr/share/fsl/5.0/bin' + pathsep + _remove_python3_from_PATH(environ.get('PATH', '')),
    'LD_LIBRARY_PATH': '/usr/lib/fsl/5.0' + pathsep + environ.get('LD_LIBRARY_PATH', ''),
    }
ENVIRON = {**environ, **ENVIRON}


EVENT_VALUE = {
    'move': 1,
    'rest': 0,
    }

DESIGN_TEMPLATE = Path('/home/giovanni/tools/boavus/boavus/data/design_template.fsf')


def run_feat(FEAT_OUTPUT, task, dry_run=False):

    feat_path = FEAT_OUTPUT / ('sub-' + task.subject)
    feat_path.mkdir(exist_ok=True)
    if task.session is not None:
        feat_path = feat_path / ('ses-' + task.session)
        feat_path.mkdir(exist_ok=True)

    subj_design = prepare_design(feat_path, task)
    cmd = ['fsl5.0-feat', str(subj_design)]

    if not dry_run:
        # Popen(cmd, env=ENVIRON, preexec_fn=setpgrp)
        run(cmd, env=ENVIRON)

    return feat_path / remove_underscore(task.filename.name)


def prepare_design(feat_path, task):
    tsv_events = feat_path / replace_underscore(task.filename.name, 'events.tsv')
    _write_events(task, tsv_events)

    anat_nii = find_anat(task)  # TODO: use BET

    # collect info
    img = niload(str(task.filename))
    n_vols = img.header.get_data_shape()[3]
    tr = img.header['pixdim'][4]  # Not sure it it's reliable

    with DESIGN_TEMPLATE.open('r') as f:
        design = f.read()

    output_dir = feat_path / remove_underscore(task.filename.name)

    design_values = {
        'XXX_OUTPUTDIR': str(output_dir),
        'XXX_NPTS': str(n_vols),
        'XXX_TR': str(tr),
        'XXX_FEAT_FILE': str(task.filename),
        'XXX_HIGHRES_FILE': str(anat_nii),
        'XXX_EV1': 'motor',
        'XXX_TSVFILE': str(tsv_events),
        }

    for pattern, value in design_values.items():
        design = design.replace(pattern, value)

    subj_design = feat_path / replace_underscore(task.filename.name, 'design.fsf')

    with subj_design.open('w') as f:
        f.write(design)

    return subj_design


def find_anat(task):
    """TODO: this could be used in bidso"""
    subj_path = find_root(task.filename)
    return next(subj_path.rglob('anat/*_T1w.nii.gz'))


def _write_events(task, tsv_events):
    with tsv_events.open('w') as f:
        for event in task.events.tsv:
            f.write(f'{event["onset"]}\t{event["duration"]}\t{EVENT_VALUE[event["trial_type"]]}\n')
