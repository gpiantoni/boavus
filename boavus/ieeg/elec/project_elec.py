from logging import getLogger
from pathlib import Path
from subprocess import run, DEVNULL
from os import environ
from tempfile import mkdtemp

from wonambi.attr import Channels

lg = getLogger(__name__)


SNAP_PATH = str(Path(__file__).resolve().parent / 'matlab')


MATLAB_CMD = ['matlab', '-nojvm', '-nodisplay', '-nosplash', '-r']


def snap_to_surface(surf, chan, surf_path=None):
    """Snap to surface, using Dijkstra matlab scripts.

    Parameters
    ----------
    surf : instance of Surf

    chan : instance of Chan

    surf_path : Path
        where to store surface filled / smoothed files

    Returns
    -------
    instance of Chan
        channels snapped to surface

    Notes
    -----
    if you pass surf_path, it stores the intermediate steps in
    that folder, but the intermediate steps for the channels
    are always stored in a temp folder.
    """
    FREESURFER_MATLAB = environ['FREESURFER_HOME'] + '/matlab'

    tmp_path = Path(mkdtemp())
    if surf_path is None:
        surf_path = tmp_path

    pial = Path(surf.surf_file)
    filled = surf_path / (pial.name + '_filled.mgz')
    outer = surf_path / (pial.name + '_outer')
    smooth = surf_path / (pial.name + '_outer_smooth')

    chan_path = tmp_path / 'chan.csv'
    chan_snapped_path = tmp_path / 'chan_snapped.csv'
    chan.export(str(chan_path))

    lg.debug(f'Reading surface from {pial}')
    if not filled.exists():
        run(['mris_fill', '-c', '-r', '1', str(pial), str(filled)],
            stdout=DEVNULL, stderr=DEVNULL)

    if not outer.exists():
        cmd = ["make_outer_surface('" + str(filled) + "', 15, '" + str(outer) + "'); exit", ]
        run(MATLAB_CMD + cmd, cwd=FREESURFER_MATLAB,
            stdout=DEVNULL, stderr=DEVNULL)

    if not smooth.exists():
        run(['mris_smooth', '-nw', '-n', '60', str(outer), str(smooth)],
            stdout=DEVNULL, stderr=DEVNULL)
        lg.debug(f'Writing smooth surface to {smooth}')

    cmd = ["snap_to_surface('" + str(smooth) + "', '" + str(chan_path) + "'); exit", ]
    run(MATLAB_CMD + cmd, cwd=SNAP_PATH,
        stdout=DEVNULL, stderr=DEVNULL)

    chan = Channels(str(chan_snapped_path))
    return chan
