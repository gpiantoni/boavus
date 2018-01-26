from os import setpgrp
from pathlib import Path
from nibabel import load as niload
from time import sleep
from subprocess import Popen, run

from bidso import file_Core, Task
from bidso.utils import bids_mkdir, replace_underscore, read_tsv, replace_extension, remove_extension
from bidso.find import find_in_bids

from .misc import run_bet, run_reorient2std
from ..utils import ENVIRON

PARAMETERS = {}


EVENT_VALUE = {
    'move': 1,
    'rest': 0,
    }

DESIGN_TEMPLATE = Path(__file__).resolve().parents[1] / 'data/design_template.fsf'


def main(bids_dir, feat_dir):

    feat_dir.mkdir(exist_ok=True)

    feats = []
    for fmri_path in bids_dir.rglob('*_bold.nii.gz'):
        task = Task(fmri_path)
        feat_path = run_feat(feat_dir, task)
        feats.append(feat_path)

    # wait for it to end
    while True:
        tsplots = [(x / 'tsplot' / 'tsplot_zstat1.png').exists() for x in feats]
        if all(tsplots):
            break
        sleep(1)


def run_feat(FEAT_OUTPUT, task, dry_run=False):

    run_reorient2std(task.filename)  # TODO: this modifies the BIDS

    subj_design = prepare_design(FEAT_OUTPUT, task)
    cmd = ['feat', str(subj_design)]

    if not dry_run:
        Popen(cmd, env=ENVIRON, preexec_fn=setpgrp)
        # run(cmd, env=ENVIRON)

    feat_path = bids_mkdir(FEAT_OUTPUT, task)
    return feat_path / replace_extension(task.filename.name, '.feat')


def prepare_design(FEAT_OUTPUT, task):
    feat_path = bids_mkdir(FEAT_OUTPUT, task)

    events_fsl = feat_path / task.events.filename.name
    _write_events(task.events.filename, events_fsl)

    anat_path = find_in_bids(task.filename, modality='T1w', extension='.nii.gz', upwards=True)
    anat_task = file_Core(anat_path)
    run_reorient2std(anat_task.filename)  # TODO: this modifies the BIDS
    bids_mkdir(FEAT_OUTPUT, anat_task)

    bet_nii = run_bet(FEAT_OUTPUT, anat_task)

    # collect info
    img = niload(str(task.filename))
    n_vols = img.header.get_data_shape()[3]
    tr = img.header['pixdim'][4]  # Not sure it it's reliable

    with DESIGN_TEMPLATE.open('r') as f:
        design = f.read()

    output_dir = feat_path / remove_extension(Path(task.filename).name)

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
