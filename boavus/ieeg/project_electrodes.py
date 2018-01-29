from json import dump
from logging import getLogger
from multiprocessing import Pool
from numpy import array, median

from bidso import Electrodes
from bidso.find import find_in_bids, find_root
from bidso.utils import replace_underscore

from wonambi.attr.chan import Channels
from wonambi.attr import Freesurfer

from .elec.project_elec import snap_to_surface

lg = getLogger(__name__)

PARAMETERS = {
    'acquisition': [
        'clinical',
        'experimental',
        ],
    'parallel': True,
    }


def main(bids_dir, freesurfer_dir):
    args = []
    for electrode_path in find_in_bids(bids_dir, generator=True, modality='electrodes', extension='.tsv'):
        elec = Electrodes(electrode_path)
        if elec.acquisition in PARAMETERS['acquisition']:
            fs = Freesurfer(freesurfer_dir / ('sub-' + elec.subject))

            args.append((elec, fs))

    if PARAMETERS['parallel']:
        with Pool(processes=4) as p:
            p.starmap(project_electrodes, args)
    else:
        for one_args in args:
            project_electrodes(*one_args)


def project_electrodes(elec, freesurfer):

    bids_dir = find_root(elec.filename)

    xyz = array(elec.get_xyz())
    if elec.coordframe.json['iEEGCoordinateSystem'] == 'RAS':
        # convert from RAS to tkRAS
        xyz -= freesurfer.surface_ras_shift

    chan = Channels([x['name'] for x in elec.electrodes.tsv], xyz)

    if median(chan.return_xyz()[:, 0]) > 0:
        surf = freesurfer.read_brain().rh
    else:
        surf = freesurfer.read_brain().lh

    anat_dir = find_in_bids(elec.filename, upwards=True, pattern='anat')
    lg.debug(f'Saving surfaces in {anat_dir}')
    chan = snap_to_surface(surf, chan, anat_dir)

    elec.acquisition += 'projected'
    tsv_electrodes = elec.get_filename(bids_dir)

    lg.debug(f'Writing snapped electrodes to {tsv_electrodes}')

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
