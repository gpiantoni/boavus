from ctypes import c_int16
from wonambi import Data
from wonambi.utils.simulate import _make_chan_name
from datetime import datetime
from numpy import (append,
                   arange,
                   array,
                   insert,
                   pi,
                   save,
                   sin,
                   )
from numpy.random import seed, random
from bidso.find import find_root
from bidso.utils import replace_underscore

from popeye.visual_stimulus import VisualStimulus, simulate_bar_stimulus
from popeye.og import GaussianModel


S_FREQ = 500
N_CHAN = 10
DUR = 1
STIM_FILE = 'prf.npy'


def simulate_prf(filename):

    stimulus, bar = generate_stimulus()
    model = generate_model(stimulus)
    dat = generate_population_data(model)

    chan = _make_chan_name(n_chan=N_CHAN)
    data = Data(data=dat, s_freq=S_FREQ, chan=chan, time=arange(dat[0].shape[0]) / S_FREQ)

    data.start_time = datetime.now()
    data.export(filename, 'bids')

    create_prf_events(replace_underscore(filename, 'events.tsv'), bar.shape[2])

    bids_dir = find_root(filename)
    stimuli_dir = bids_dir / 'stimuli'
    stimuli_dir.mkdir(exist_ok=True, parents=True)
    bar_file = stimuli_dir / STIM_FILE
    save(bar_file, bar)


def generate_stimulus():
    viewing_distance = 38
    screen_width = 25
    thetas = arange(0, 360, 90)
    thetas = insert(thetas, 0, -1)
    thetas = append(thetas, -1)
    num_blank_steps = 30
    num_bar_steps = 30
    ecc = 12
    tr_length = 1.0
    scale_factor = 1.0
    pixels_across = 100
    pixels_down = 100
    dtype = c_int16
    bar = simulate_bar_stimulus(pixels_across, pixels_down, viewing_distance,
                                screen_width, thetas, num_bar_steps, num_blank_steps, ecc)

    stimulus = VisualStimulus(bar, viewing_distance, screen_width, scale_factor, tr_length, dtype)

    return stimulus, bar


def nohrf(*args):
    return array([1, ])


def generate_model(stimulus):
    model = GaussianModel(stimulus, nohrf)
    model.hrf_delay = 0
    model.mask_size = 6
    return model


def generate_population_data(model):
    seed(1)
    # generate a random pRF estimate
    X = random((N_CHAN, )) * 10 - 5
    Y = random((N_CHAN, )) * 10 - 5
    SIGMA = random((N_CHAN, )) * 10 - 5
    BETA = random((N_CHAN, ))
    BASELINE = random((N_CHAN, ))

    FREQ = 70
    t = arange(S_FREQ * DUR) / S_FREQ

    dat = []
    for i in range(N_CHAN):
        i_dat = model.generate_prediction(X[i], Y[i], SIGMA[i], BETA[i], BASELINE[i])
        i_dat -= i_dat.min()

        x = i_dat[:, None] * sin(2 * pi * t * FREQ)
        dat.append(x.flatten())

    return array(dat)


def create_prf_events(tsv_file, n_events):

    with tsv_file.open('w') as f:
        f.write('onset\tduration\ttrial_type\tstim_file\tstim_file_index\n')
        for i in range(n_events):
            f.write(f'{i * DUR}\t{DUR:f}\t{i + 1:d}\t{STIM_FILE}\t{i + 1:d}\n')
