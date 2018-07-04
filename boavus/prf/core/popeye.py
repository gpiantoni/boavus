"""Interface to popeye
"""
from ctypes import c_int16
from numpy import (array,
                   pi,
                   tan,
                   )
from popeye.utilities import grid_slice
from popeye.visual_stimulus import VisualStimulus
from popeye.og import GaussianFit, GaussianModel


SCREEN_WIDTH = 25
N_PIXELS = 100
VIEWING_DISTANCE = SCREEN_WIDTH / (tan(pi / 360 * N_PIXELS) * 2)


def fit_popeye(bars, dat):

    stimulus = generate_stimulus(bars)
    model = generate_model(stimulus)

    # set search grid
    x_grid = grid_slice(-10, 10, 5)
    y_grid = grid_slice(-10, 10, 5)
    s_grid = grid_slice(0.25, 5.25, 5)

    # set search bounds
    x_bound = (-12.0, 12.0)
    y_bound = (-12.0, 12.0)
    s_bound = (0.001, 12.0)
    b_bound = (1e-8, None)
    m_bound = (None, None)

    # loop over each voxel and set up a GaussianFit object
    grids = (x_grid, y_grid, s_grid,)
    bounds = (x_bound, y_bound, s_bound, b_bound, m_bound)

    # fit the response
    fit = GaussianFit(model, dat, grids, bounds)

    return fit


def generate_stimulus(bars):
    tr_length = 1.0
    scale_factor = 1.0
    dtype = c_int16
    stimulus = VisualStimulus(bars, VIEWING_DISTANCE, SCREEN_WIDTH, scale_factor, tr_length, dtype)

    return stimulus


def nohrf(*args):
    return array([1, ])


def generate_model(stimulus):
    model = GaussianModel(stimulus, nohrf)
    model.hrf_delay = 0
    model.mask_size = 6
    return model
