from json import dump
from logging import getLogger
from multiprocessing import Pool
from numpy import array

from bidso import Electrodes
from bidso.find import find_in_bids, find_root
from bidso.utils import replace_underscore

from wonambi.attr import Freesurfer

from .elec.annealing import snap_elec_to_surf
from ..mri.surface import fill_surface

lg = getLogger(__name__)


def project_electrodes(elec, freesurfer, analysis_dir):

    elec.acquisition += 'projected'
    bids_root = find_root(elec.filename)
    tsv_electrodes = elec.get_filename(bids_root)

    elec_realigned = {}
    HEMI = {
        'L': 'lh',
        'R': 'rh',
    }

    groups = {x['group'] for x in elec.electrodes.tsv}
    for group in groups:
        print(group)
        anat_dir = analysis_dir / ('sub-' + elec.subject) / 'anat'
        anat_dir.mkdir(exist_ok=True, parents=True)
        labels = [x['name'] for x in elec.electrodes.tsv if x['group'] == group]
        hemi = [x['hemisphere'] for x in elec.electrodes.tsv if x['group'] == group][0]
        elec_type = [x['type'] for x in elec.electrodes.tsv if x['group'] == group][0]
        if not elec_type == 'surface':
            print(f'not realigning {group} because its type is {elec_type}')
            for _elec in elec.electrodes_tsv:
                if _elec['group'] == group:
                    elec_realigned[_elec['label']] = (float(_elec['x']), float(_elec['y']), float(_elec['z']))

        anat_file = anat_dir / (HEMI[hemi] + '.smooth')
        if not anat_file.exists():
            surf = getattr(freesurfer.read_brain('pial'), HEMI[hemi])
            fill_surface(surf.surf_file, anat_file)

        xyz = array([(float(x['x']), float(x['y']), float(x['z'])) for x in elec.electrodes.tsv if x['group'] == group])
        xyz -= freesurfer.surface_ras_shift
        xyz_realigned = snap_elec_to_surf(xyz, anat_file)

        for label, xyz_ in zip(labels, xyz_realigned):
            elec_realigned[label] = xyz_ + freesurfer.surface_ras_shift

    with tsv_electrodes.open('w') as f:
        f.write('name\tgroup\tx\ty\tz\tsize\ttype\tmaterial\themisphere\n')
        for _elec in elec.electrodes.tsv:
            label = _elec['name']
            xyz = "\t".join(f'{x:f}' for x in elec_realigned[label])
            one_chans = [x for x in elec.electrodes.tsv if x['name'] == label][0]
            group = one_chans['group']
            elec_type = one_chans['type']
            size = one_chans['size']
            material = one_chans['material']
            hemisphere = one_chans['hemisphere']
            f.write(f'{label}\t{group}\t{xyz}\t{size}\t{elec_type}\t{material}\t{hemisphere}\n')

    elec.coordframe.json['iEEGCoordinateProcessingDescription'] += '; Dijkstra et al.'  # TODO: better description + remove None
    new_json = replace_underscore(tsv_electrodes, 'coordsystem.json')
    with new_json.open('w') as f:
        dump(elec.coordframe.json, f, indent=2)

    return Electrodes(tsv_electrodes)
