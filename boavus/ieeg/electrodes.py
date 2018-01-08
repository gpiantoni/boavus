from pathlib import Path
from shutil import copyfile
from numpy import array, median
from bidso import Electrodes
from bidso.utils import read_tsv, replace_underscore

from wonambi.attr.chan import Channels
from wonambi.attr import Freesurfer

from .elec.project_elec import snap_to_surface


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

    old_json = replace_underscore(Path(electrodes_file.filename), 'coordframe.json')
    new_json = replace_underscore(tsv_electrodes, 'coordframe.json')
    copyfile(old_json, new_json)  # TODO: add info about transformation


def assign_regions(electrode_path, freesurfer_path):
    elec = Electrodes(electrode_path)
    tsv_electrodes = Path(elec.electrodes.filename).parent / f'sub-{elec.subject}_ses-{elec.session}_acq-{elec.acq}regions_electrodes.tsv'

    freesurfer = Freesurfer(freesurfer_path / f'sub-{elec.subject}')

    with tsv_electrodes.open('w') as f:
        f.write('name\tx\ty\tz\ttype\tsize\tmaterial\tregion\n')  # TODO: region is not in BEP010
        for _tsv in elec.electrodes.tsv:
            xyz = array([float(_tsv['x']), float(_tsv['y']), float(_tsv['z'])])
            region = freesurfer.find_brain_region(xyz, exclude_regions=('White', 'WM', 'Unknown'))[0]
            f.write(f'{_tsv["name"]}\t{_tsv["x"]}\t{_tsv["y"]}\t{_tsv["z"]}\t{_tsv["type"]}\t{_tsv["size"]}\t{_tsv["material"]}\t{region}\n')

    old_json = replace_underscore(Path(elec.filename), 'coordframe.json')
    new_json = replace_underscore(tsv_electrodes, 'coordframe.json')
    copyfile(old_json, new_json)  # TODO: add info about transformation
