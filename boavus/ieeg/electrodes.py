from json import dump
from pathlib import Path
from multiprocessing import Pool
from numpy import array, median
from bidso import Electrodes
from bidso.find import find_in_bids
from bidso.utils import replace_underscore

from wonambi.attr.chan import Channels
from wonambi.attr import Freesurfer

from .elec.project_elec import snap_to_surface


def run_ieeg_electrodes(bids_dir, freesurfer_dir):
    args = []
    for electrode_path in find_in_bids(bids_dir, generator=True, modality='electrodes', extension='.tsv'):
        elec = Electrodes(electrode_path)
        if elec.acquisition in ('clinical', 'experimental'):
            fs = Freesurfer(freesurfer_dir / ('sub-' + elec.subject))
            args.append((elec, fs))

    with Pool(processes=4) as p:
        p.starmap(_parallel_elec, args)


def _parallel_elec(elec, fs):
    elec_proj = project_electrodes(elec, fs)
    assign_regions(elec_proj, fs)


def project_electrodes(elec, freesurfer):

    xyz = array(elec.get_xyz())
    if elec.coordframe.json['iEEGCoordinateSystem'] == 'RAS':
        # convert from RAS to tkRAS
        xyz -= freesurfer.surface_ras_shift

    chan = Channels([x['name'] for x in elec.electrodes.tsv], xyz)

    if median(chan.return_xyz()[:, 0]) > 0:
        surf = freesurfer.read_brain().rh
    else:
        surf = freesurfer.read_brain().lh

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

    return Electrodes(tsv_electrodes)


def assign_regions(elec, freesurfer):
    tsv_electrodes = Path(elec.electrodes.filename).parent / f'sub-{elec.subject}_ses-{elec.session}_acq-{elec.acquisition}regions_electrodes.tsv'

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

    return Electrodes(tsv_electrodes)
