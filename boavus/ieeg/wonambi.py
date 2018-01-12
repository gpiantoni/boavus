"""Glue code for wonambi"""
from copy import deepcopy
from bidso import iEEG, file_Events
from bidso.utils import replace_underscore
from wonambi import Data
from numpy import memmap, float64, c_, NaN, empty, arange, array


class Dataset(iEEG):
    def __init__(self, filename):
        super().__init__(filename)

    def read_data(self, begsam=None, endsam=None):

        sf = float(self.channels.tsv[0]['sampling_frequency'])
        RecordingDuration = self.json.json['RecordingDuration']
        n_samples = int(sf * RecordingDuration)
        n_channels = len(self.channels.tsv)

        if begsam is None:
            begsam = 0
        if endsam is None:
            endsam = n_samples - 1

        data = memmap(str(self.filename), dtype=float64, mode='c',
                      shape=(n_channels, n_samples), order='F')
        dat = data[:, max((begsam, 0)):min((endsam, n_samples))].astype(float64)

        if begsam < 0:

            pad = empty((dat.shape[0], 0 - begsam))
            pad.fill(NaN)
            dat = c_[pad, dat]

        if endsam >= n_samples:

            pad = empty((dat.shape[0], endsam - n_samples))
            pad.fill(NaN)
            dat = c_[dat, pad]

        time = arange(begsam, endsam) / sf
        channels = array(list(x['name'] for x in self.channels.tsv))

        return Data(dat, s_freq=sf, chan=channels, time=time)

    def read_events(self):
        """this is different from markers. Here you have 'onset', 'duration' and 'trial_type'
        """
        events_file = file_Events(replace_underscore(self.filename, 'events.tsv'))

        events = deepcopy(events_file.tsv)
        for evt in events:
            evt['duration'] = float(evt['duration'])
            evt['onset'] = float(evt['onset'])
        return events
