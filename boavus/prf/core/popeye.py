"""Interface to popeye
"""


def fit_popeye(bars, data):
    # set search grid
    x_grid = utils.grid_slice(-10,10,5)
    y_grid = utils.grid_slice(-10,10,5)
    s_grid = utils.grid_slice (0.25,5.25,5)

    # set search bounds
    x_bound = (-12.0,12.0)
    y_bound = (-12.0,12.0)
    s_bound = (0.001,12.0)
    b_bound = (1e-8,None)
    m_bound = (None,None)

    # loop over each voxel and set up a GaussianFit object
    grids = (x_grid, y_grid, s_grid,)
    bounds = (x_bound, y_bound, s_bound, b_bound, m_bound)

    # fit the response
    fit = og.GaussianFit(model, data.data[0][-1, :], grids, bounds)