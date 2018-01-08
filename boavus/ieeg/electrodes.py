from json import dump
from pathlib import Path
from numpy import array, median
from bidso import Electrodes
from bidso.utils import replace_underscore

from wonambi.attr.chan import Channels
from wonambi.attr import Freesurfer

from .elec.project_elec import snap_to_surface


def project_electrodes(elec, freesurfer_path):
    fs = Freesurfer(freesurfer_path / ('sub-' + elec.subject))

    xyz = array([(float(x['x']), float(x['y']), float(x['z'])) for x in elec.electrodes.tsv])

    if elec.coordframe.json['iEEGCoordinateSystem'] == 'RAS':
        # convert from RAS to tkRAS
        xyz -= fs.surface_ras_shift

    chan = Channels(
        [x['name'] for x in elec.electrodes.tsv],
        xyz)

    if median(chan.return_xyz()[:, 0]) > 0:
        surf = fs.read_brain().rh
    else:
        surf = fs.read_brain().lh

    chan = snap_to_surface(surf, chan)

    tsv_electrodes = Path(elec.filename).parent / f'sub-{elec.subject}_ses-{elec.session}_acq-{elec.acquisition}projected_electrodes.tsv'

    with tsv_electrodes.open('w') as f:
        f.write('name\tx\ty\tz\ttype\tsize\tmaterial\n')
        for _chan in chan.chan:
            xyz = "\t".join(f'{x:f}' for x in _chan.xyz)
            one_chans = [x for x in elec.electrodes.tsv if x['name'] == _chan.label][0]
            elec_type = one_chans['type']
            size = one_chans['size']
            material = one_chans['material']
            f.write(f'{_chan.label}\t{xyz}\t{elec_type}\t{size}\t{material}\n')

    elec.coordframe.json['iEEGCoordinateSystem'] = 'tkRAS'
    elec.coordframe.json['iEEGCoordinateProcessingDescripton'] += '; Dijkstra et al.'  # TODO: better description + remove None
    new_json = replace_underscore(tsv_electrodes, 'coordframe.json')
    with new_json.open('w') as f:
        dump(elec.coordframe.json, f, indent=2)


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

    elec.coordframe.json['iEEGCoordinateProcessingDescripton'] += '; Assign brain regions'  # TODO: better description + remove None
    new_json = replace_underscore(tsv_electrodes, 'coordframe.json')
    with new_json.open('w') as f:
        dump(elec.coordframe.json, f, indent=2)
