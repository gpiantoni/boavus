from os import setpgrp
from pathlib import Path
from nibabel import load as niload
from subprocess import Popen, run

from bidso import file_Core
from bidso.utils import replace_underscore, find_root, remove_underscore

from .bet import run_bet
from .utils import ENVIRON, mkdir_task


EVENT_VALUE = {
    'move': 1,
    'rest': 0,
    }

DESIGN_TEMPLATE = Path('/home/giovanni/tools/boavus/boavus/data/design_template.fsf')


def run_feat(FEAT_OUTPUT, task, dry_run=False):

    subj_design = prepare_design(FEAT_OUTPUT, task)
    cmd = ['fsl5.0-feat', str(subj_design)]

    if not dry_run:
        # Popen(cmd, env=ENVIRON, preexec_fn=setpgrp)
        run(cmd, env=ENVIRON)

    feat_path = mkdir_task(FEAT_OUTPUT, task)
    return feat_path / remove_underscore(task.filename.name)


def prepare_design(FEAT_OUTPUT, task):
    feat_path = mkdir_task(FEAT_OUTPUT, task)

    tsv_events = feat_path / replace_underscore(task.filename.name, 'events.tsv')
    _write_events(task, tsv_events)

    anat_nii = find_anat(task)
    bet_nii = run_bet(FEAT_OUTPUT, file_Core(anat_nii))

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
        'XXX_HIGHRES_FILE': str(bet_nii),
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
