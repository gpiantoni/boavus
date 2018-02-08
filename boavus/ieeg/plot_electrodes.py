from logging import getLogger
from numpy import array, median
from bidso import Electrodes
from bidso.find import find_in_bids
from bidso.utils import replace_underscore
from wonambi.attr import Channels, Freesurfer
from wonambi.viz import Viz3

lg = getLogger(__name__)

PARAMETERS = {
    'acquisition': '*ctmr',
    }


def main(bids_dir, freesurfer_dir, output_dir):

    for electrode_path in find_in_bids(bids_dir, generator=True, acquisition=PARAMETERS['acquisition'], modality='electrodes', extension='.tsv'):
        elec = Electrodes(electrode_path)
        fs = Freesurfer(freesurfer_dir / ('sub-' + elec.subject))
        v = plot_electrodes(elec, fs)

        png_file = replace_underscore(elec.get_filename(output_dir), 'surfaceplot.png')
        png_file.parent.mkdir(exist_ok=True, parents=True)
        lg.debug(f'Saving electrode plot on {png_file}')
        v.save(png_file)
        v.close()


def plot_electrodes(elec, freesurfer):
    labels = [x['name'] for x in elec.electrodes.tsv]
    xyz = array(elec.get_xyz())

    if elec.coordframe.json['iEEGCoordinateSystem'] == 'RAS':
        # convert from RAS to tkRAS
        xyz -= freesurfer.surface_ras_shift

    chan = Channels(labels, xyz)
    if median(chan.return_xyz()[:, 0]) > 0:
        surf = freesurfer.read_brain().rh
    else:
        surf = freesurfer.read_brain().lh
    v = Viz3()
    v.add_surf(surf)
    v.add_chan(chan)

    return v
