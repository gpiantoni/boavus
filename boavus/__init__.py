from .command import boavus

from pathlib import Path
with (Path(__file__).parent / 'VERSION').open() as f:
    __version__ = f.read().strip()
