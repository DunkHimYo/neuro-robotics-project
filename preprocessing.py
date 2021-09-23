import mne
from meegkit import star
from bp import bandpower_from_psd
from mne.time_frequency import psd_array_multitaper
import numpy as np

def preprocessing(frame,sfreq):
    data = mne.evoked.detrend(frame)
    data = mne.filter.filter_data(data=data, l_freq=4, h_freq=50, sfreq=128,verbose=False)
    x = data.T
    y, w, _ = star.star(x,verbose=False)
    y=y.T
    eeg_data = []

    for j in range(0, (y.shape[1])-(256-128), 128):

        psd, freqs = psd_array_multitaper(y[:, j: j + 256], 128, adaptive=True,
                                          normalization='full', verbose=0)
        bp=bandpower_from_psd(psd, freqs, ch_names=list(frame.index),
                                relative=False, bands=[(4, 8, 'Theta'), (8, 12, 'Alpha'),
                                                       (12, 15, 'BetaL'), (16, 20, 'BetaM'),
                                                       (21, 30, 'BetaH'),
                                                       (30, 64, 'Gamma')])
        #print(bp.loc[:, 'Theta':'TotalAbsPow'])
        eeg_data.append(bp.loc[:, 'Theta':'TotalAbsPow'])
    return eeg_data
