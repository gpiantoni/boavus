"""Glue code for wonambi"""
from copy import deepcopy
from numpy import array
from bidso import iEEG, file_Events
from bidso.utils import read_tsv, replace_underscore
from wonambi import Dataset as wDataset
from wonambi.attr import Channels


class Dataset(wDataset):
    def __init__(self, filename):
        super().__init__(filename)

        # find a more elegant way of doing this, probably with iEEG
        self.electrode_file = next(self.filename.parents[1].rglob('*projectedregions*.tsv'))

        _read_channels(self)

    def read_data(self, **kwargs):
        data = super().read_data(**kwargs)

        data.attr['chan'] = _read_electrodes(self.electrode_file)
        return data

    def read_events(self):
        """this is different from markers. Here you have 'onset', 'duration' and 'trial_type'
        """
        events_file = file_Events(replace_underscore(self.filename, 'events.tsv'))

        events = deepcopy(events_file.tsv)
        for evt in events:
            evt['duration'] = float(evt['duration'])
            evt['onset'] = float(evt['onset'])
        return events


def _read_channels(d):
    task = iEEG(d.filename)  # TODO: this is backwards: the iEEG class should be the base

    labels = [x['name'] for x in task.channels.tsv]
    new_labels = []
    for i, old in enumerate(d.header['chan_name']):

        if i < len(labels) and labels[i] != '':
            new_labels.append(labels[i])
        else:
            new_labels.append(old)

    d.header['chan_name'] = new_labels


def _read_electrodes(electrode_file):
    """The correct term is Electrodes, not Channels, in this case"""
    chans = read_tsv(electrode_file)
    chan = Channels(
        [x['name'] for x in chans],
        array([(float(x['x']), float(x['y']), float(x['z'])) for x in chans]))
    return chan
