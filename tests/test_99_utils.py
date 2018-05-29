from subprocess import run, PIPE
from pytest import raises

from boavus.utils import check_subprocess


def test_subprocess_raises():

    p = run(['sleep', 'a'], stdout=PIPE, stderr=PIPE)
    with raises(RuntimeError):
        check_subprocess(p)
