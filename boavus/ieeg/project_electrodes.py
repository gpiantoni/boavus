from pathlib import Path
from shutil import copyfile
from numpy import array, median

from wonambi.attr.chan import Channels
from wonambi.attr import Freesurfer

from .elec.project_elec import snap_to_surface
from ..utils import read_tsv, replace_underscore


def project_electrodes(electrodes_file, freesurfer_path):
    chans = read_tsv(electrodes_file.filename)
    chan = Channels(
        [x['name'] for x in chans],
        array([(float(x['x']), float(x['y']), float(x['z'])) for x in chans]))

    fs = Freesurfer(freesurfer_path / ('sub-' + electrodes_file.subject))
    if median(chan.return_xyz()[:, 0]) > 0:
        surf = fs.read_brain().rh
    else:
        surf = fs.read_brain().lh

    chan = snap_to_surface(surf, chan)

    tsv_electrodes = Path(electrodes_file.filename).parent / f'sub-{electrodes_file.subject}_ses-{electrodes_file.session}_acq-{electrodes_file.acquisition}projected_electrodes.tsv'

    with tsv_electrodes.open('w') as f:
        f.write('name\tx\ty\tz\ttype\tsize\tmaterial\n')
        for _chan in chan.chan:
            xyz = "\t".join(f'{x:f}' for x in _chan.xyz)
            one_chans = [x for x in chans if x['name'] == _chan.label][0]
            elec_type = one_chans['type']
            size = one_chans['size']
            material = one_chans['material']
            f.write(f'{_chan.label}\t{xyz}\t{elec_type}\t{size}\t{material}\n')

    old_json = replace_underscore(Path(f.filename), 'coordframe.json')
    new_json = replace_underscore(tsv_electrodes, 'coordframe.json')
    copyfile(old_json, new_json)  # TODO: add info about transformation
