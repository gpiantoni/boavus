from pathlib import Path
from shutil import rmtree
from nibabel import load as niload

from bidso import file_Core, Task
from bidso.utils import bids_mkdir, replace_underscore, read_tsv, replace_extension

from .misc import run_bet, run_reorient2std


EVENT_VALUE = {
    'move': 1,
    'rest': 0,
    }

DESIGN_TEMPLATE = Path(__file__).resolve().parents[1] / 'data/design_template.fsf'


def prepare_design(analysis_dir, func, anat):

    task = Task(func)
    run_reorient2std(func)  # TODO: this modifies the BIDS

    feat_path = bids_mkdir(analysis_dir, task)

    events_fsl = feat_path / task.events.filename.name
    _write_events(task.events.filename, events_fsl)

    anat_task = file_Core(anat)
    run_reorient2std(anat_task.filename)  # TODO: this modifies the BIDS
    bids_mkdir(analysis_dir, anat_task)

    # TODO: bet in nipype
    bet_nii = run_bet(analysis_dir, anat_task)

    # collect info
    img = niload(str(task.filename))
    n_vols = img.header.get_data_shape()[3]
    tr = img.header['pixdim'][4]  # Not sure it it's reliable

    with DESIGN_TEMPLATE.open('r') as f:
        design = f.read()

    output_dir = feat_path / replace_extension(Path(task.filename).name, '.feat')
    try:
        rmtree(output_dir)
    except:
        pass

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
