"""Glue code for wonambi"""
from copy import deepcopy
from bidso import iEEG, file_Tsv
from bidso.utils import replace_underscore
from wonambi import ChanTime
from numpy import memmap, float64, c_, NaN, empty, arange, asarray


class Dataset(iEEG):
    def __init__(self, filename, electrodes='*'):
        super().__init__(filename, electrodes)

    def read_data(self, chan=None, begsam=None, endsam=None):

        all_chan_names = [x['name'] for x in self.channels.tsv]
        if chan is None:
            chan = all_chan_names
        if not (isinstance(chan, list) or isinstance(chan, tuple)):
            raise TypeError('Parameter "chan" should be a list')
        idx_chan = [all_chan_names.index(x) for x in chan]

        sf = float(self.channels.tsv[0]['sampling_frequency'])
        RecordingDuration = self.json.json['RecordingDuration']
        n_samples = int(sf * RecordingDuration)
        n_channels = len(self.channels.tsv)

        if not isinstance(begsam, list):
            begsam = [begsam]
        if not isinstance(endsam, list):
            endsam = [endsam]

        n_trl = len(begsam)

        data = ChanTime()
        data.s_freq = sf
        data.axis['chan'] = empty(n_trl, dtype='O')
        data.axis['time'] = empty(n_trl, dtype='O')
        data.data = empty(n_trl, dtype='O')

        for i, one_begsam, one_endsam in zip(range(n_trl), begsam, endsam):
            data.axis['chan'][i] = asarray(chan, dtype='U')
            data.axis['time'][i] = arange(one_begsam, one_endsam) / sf
            data.data[i] = _read_dat(self.filename, (n_channels, n_samples),
                                     idx_chan, one_begsam, one_endsam)

        return data

    def read_events(self):
        """this is different from markers. Here you have 'onset', 'duration' and 'trial_type'
        """
        events_file = file_Tsv(replace_underscore(self.filename, 'events.tsv'))

        events = deepcopy(events_file.tsv)
        for evt in events:
            evt['duration'] = float(evt['duration'])
            evt['onset'] = float(evt['onset'])
        return events


def _read_dat(filename, dat_shape, idx_chan, begsam, endsam):
    n_samples = dat_shape[1]

    if begsam is None:
        begsam = 0
    if endsam is None:
        endsam = n_samples - 1

    data = memmap(str(filename), dtype=float64, mode='c',
                  shape=dat_shape, order='F')
    dat = data[:, max((begsam, 0)):min((endsam, n_samples))].astype(float64)

    if begsam < 0:

        pad = empty((dat.shape[0], 0 - begsam))
        pad.fill(NaN)
        dat = c_[pad, dat]

    if endsam >= n_samples:

        pad = empty((dat.shape[0], endsam - n_samples))
        pad.fill(NaN)
        dat = c_[dat, pad]

    return dat
