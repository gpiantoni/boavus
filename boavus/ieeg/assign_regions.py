from json import dump
from multiprocessing import Pool
from numpy import array

from bidso import Electrodes
from bidso.find import find_in_bids, find_root
from bidso.utils import replace_underscore

from wonambi.attr import Freesurfer


def main(bids_dir, freesurfer_dir, acquisition='clinical', noparallel=False):
    """
    assign electrodes to brain regions',

    Parameters
    ----------
    bids_dir : path

    freesurfer_dir : path

    acquisition : str
        acquisition type of the electrode files
    noparallel : bool
        if it should run serially (i.e. not parallely, mostly for debugging)
    """
    args = []
    for electrode_path in find_in_bids(bids_dir, generator=True, acquisition=acquisition, modality='electrodes', extension='.tsv'):
        elec = Electrodes(electrode_path)
        fs = Freesurfer(freesurfer_dir / ('sub-' + elec.subject))
        args.append((elec, fs))

    if noparallel:
        for arg in args:
            assign_regions(*arg)
    else:
        with Pool(processes=4) as p:
            p.starmap(assign_regions, args)


def assign_regions(elec, freesurfer):
    bids_dir = find_root(elec.filename)
    elec.acquisition += 'regions'
    tsv_electrodes = elec.get_filename(bids_dir)

    with tsv_electrodes.open('w') as f:
        f.write('name\tx\ty\tz\ttype\tsize\tmaterial\tregion\n')  # TODO: region is not in BEP010
        for _tsv in elec.electrodes.tsv:
            xyz = array([float(_tsv['x']), float(_tsv['y']), float(_tsv['z'])])
            region = freesurfer.find_brain_region(xyz, exclude_regions=('White', 'WM', 'Unknown'))[0]
            f.write(f'{_tsv["name"]}\t{_tsv["x"]}\t{_tsv["y"]}\t{_tsv["z"]}\t{_tsv["type"]}\t{_tsv["size"]}\t{_tsv["material"]}\t{region}\n')

    elec.coordframe.json['iEEGCoordinateProcessingDescription'] += '; Assign brain regions'  # TODO: better description + remove None
    new_json = replace_underscore(tsv_electrodes, 'coordsystem.json')
    with new_json.open('w') as f:
        dump(elec.coordframe.json, f, indent=2)

    return Electrodes(tsv_electrodes)
