from os import setpgrp
from pathlib import Path
from nibabel import load as niload
from subprocess import Popen, run

from bidso.utils import mkdir_task, replace_underscore, remove_underscore, read_tsv

from .bet import run_bet
from ..utils import ENVIRON


EVENT_VALUE = {
    'move': 1,
    'rest': 0,
    }

DESIGN_TEMPLATE = Path('/home/giovanni/tools/boavus/boavus/data/design_template.fsf')


def run_feat(FEAT_OUTPUT, layout, task, dry_run=False):

    subj_design = prepare_design(FEAT_OUTPUT, layout, task)
    cmd = ['fsl5.0-feat', str(subj_design)]

    if not dry_run:
        Popen(cmd, env=ENVIRON, preexec_fn=setpgrp)
        # run(cmd, env=ENVIRON)

    feat_path = mkdir_task(FEAT_OUTPUT, task)
    return feat_path / remove_underscore(Path(task.filename).name)


def prepare_design(FEAT_OUTPUT, layout, task):
    feat_path = mkdir_task(FEAT_OUTPUT, task)

    events_bids = layout.get_events(task.filename)
    events_fsl = feat_path / replace_underscore(Path(task.filename).name, 'events.tsv')
    _write_events(events_bids, events_fsl)

    anat_task = find_anat(layout, task)
    bet_nii = run_bet(FEAT_OUTPUT, anat_task)

    # collect info
    img = niload(str(task.filename))
    n_vols = img.header.get_data_shape()[3]
    tr = img.header['pixdim'][4]  # Not sure it it's reliable

    with DESIGN_TEMPLATE.open('r') as f:
        design = f.read()

    output_dir = feat_path / remove_underscore(Path(task.filename).name)

    design_values = {
        'XXX_OUTPUTDIR': str(output_dir),
        'XXX_NPTS': str(n_vols),
        'XXX_TR': str(tr),
        'XXX_FEAT_FILE': str(task.filename),
        'XXX_HIGHRES_FILE': str(bet_nii),
        'XXX_EV1': 'motor',
        'XXX_TSVFILE': str(events_fsl),
        }

    for pattern, value in design_values.items():
        design = design.replace(pattern, value)

    subj_design = feat_path / replace_underscore(Path(task.filename).name, 'design.fsf')

    with subj_design.open('w') as f:
        f.write(design)

    return subj_design


def find_anat(layout, task):
    return layout.get(extensions='.nii.gz', modality='anat', subject=task.subject)[0]


def _write_events(events_input, events_output):
    tsv = read_tsv(events_input)
    with events_output.open('w') as f:
        for event in tsv:
            f.write(f'{event["onset"]}\t{event["duration"]}\t{EVENT_VALUE[event["trial_type"]]}\n')


def coreg_feat2freesurfer(feat_file, FREESURFER_PATH):
    """This needs to be improved with object-oriented feat"""
    cmd = ['reg-feat2anat', '--feat', str(feat_file), '--subject', feat_file.name.split('_')[0]]
    run(cmd,
        env={**ENVIRON, 'SUBJECTS_DIR': str(FREESURFER_PATH)},
        cwd=str(feat_file.parent))
