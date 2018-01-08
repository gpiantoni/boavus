"""Glue code for wonambi"""
from numpy import array
from bidso import iEEG
from bidso.utils import read_tsv
from wonambi import Dataset as wDataset
from wonambi.attr import Channels


class Dataset(wDataset):
    def __init__(self, filename):
        super().__init__(filename)

        _read_channels(self)

    def read_data(self, **kwargs):
        data = super().read_data(**kwargs)

        electrode_file = next(self.filename.parents[1].rglob('*projected*.tsv'))

        data.attr['chan'] = _read_electrodes(electrode_file)
        return data


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
