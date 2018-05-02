from logging import getLogger
from shutil import rmtree
from numpy import array, median

from bidso import Electrodes
from bidso.find import find_in_bids
from bidso.utils import replace_underscore, read_tsv

from wonambi.attr import Channels, Freesurfer
from wonambi.viz import Viz3

from ..bidso import read_channels

lg = getLogger(__name__)

ELECSURF_DIR = 'electrodes_on_surface'

PARAMETERS = {
    'acquisition': '*ctmr',
    'measure': {
        'modality': '',
        'column': '',
        },
    }


def main(bids_dir, analysis_dir, freesurfer_dir, output_dir):

    img_dir = output_dir / ELECSURF_DIR
    rmtree(img_dir, ignore_errors=True)
    img_dir.mkdir(exist_ok=True, parents=True)

    for electrode_path in find_in_bids(bids_dir, generator=True, acquisition=PARAMETERS['acquisition'], modality='electrodes', extension='.tsv'):
        lg.debug(f'Reading electrodes from {electrode_path}')
        elec = Electrodes(electrode_path)
        fs = Freesurfer(freesurfer_dir / ('sub-' + elec.subject))

        labels = [x['name'] for x in elec.electrodes.tsv]
        if PARAMETERS['measure']['modality'] != '':
            ecog_file = find_in_bids(
                analysis_dir,
                subject=elec.subject,
                modality=PARAMETERS['measure']['modality'],
                extension='.tsv')
            lg.debug(f'Reading {PARAMETERS["measure"]["column"]} from {ecog_file}')
            ecog_tsv = read_tsv(ecog_file)

            labels, vals = read_channels(ecog_tsv, labels, PARAMETERS['measure']['column'])

        else:
            vals = None

        v = plot_electrodes(elec, fs, labels, vals)

        png_file = img_dir / replace_underscore(elec.get_filename(), 'surfaceplot.png')
        lg.debug(f'Saving electrode plot on {png_file}')
        v.save(png_file)
        v.close()


def plot_electrodes(elec, freesurfer, labels=None, values=None):
    xyz = array(elec.get_xyz(labels))

    # convert from RAS to tkRAS
    xyz -= freesurfer.surface_ras_shift

    chan = Channels(labels, xyz)
    if median(chan.return_xyz()[:, 0]) > 0:
        surf = freesurfer.read_brain().rh
    else:
        surf = freesurfer.read_brain().lh
    v = Viz3()
    v.add_surf(surf)
    v.add_chan(chan, values=values)

    return v
