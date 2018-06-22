from numpy import (arange,
                   array,
                   dot,
                   Inf,
                   meshgrid,
                   pi,
                   )
from scipy.optimize import least_squares

from popeye.visual_stimulus import gaussian_2D


def modelfun(pp, dd, X, Y):

    g = gaussian_2D(X, Y, pp[0], pp[1], pp[2], pp[2], 0).flatten()
    g /= 2 * pi * pp[2] ** 2

    return pp[3] * dot(dd, g)


def fun_to_minimize(params, stimulus, X, Y, ydata):
    return modelfun(params, stimulus, X, Y) - ydata


def fit_analyzePRF(stimulus, data):
    res = stimulus.shape[0]

    X, Y = meshgrid(arange(res) + 1, arange(res) + 1)
    seed = array([
        (1 + res) / 2,
        (1 + res) / 2,
        res,
        1,
        ])

    bounds = array([
        [1 - res + 1, 1 - res + 1, 0, -Inf],
        [2 * res - 1, 2 * res - 1, Inf, Inf],
        ])

    stimulus = stimulus.reshape(res ** 2, -1, order='F').T

    result = least_squares(
        fun_to_minimize,
        x0=seed,
        bounds=bounds,
        method='trf',
        args=[stimulus, X, Y, data],
        )
    return result
