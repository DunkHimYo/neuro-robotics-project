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
    eeg_data = []
    
    raw = y.T
    asr = ASR(method='euclid')

    train_idx = np.arange(0 * sfreq, 10 * sfreq, dtype=int)
    _, sample_mask = asr.fit(raw[:, train_idx])
    X = sliding_window(raw, window=int(sfreq), step=int(sfreq))
    Y = np.zeros_like(X)
    
    for i in range(X.shape[1]):
        Y[:, i, :] = asr.transform(X[:, i, :])
        psd, freqs = psd_array_multitaper(Y[:,i,:], 128, adaptive=True,
                                          normalization='full', verbose=0)
        
        bp=bandpower_from_psd(psd, freqs, ch_names=list(frame.index),
                                relative=False, bands=[(4, 8, 'Theta'), (8, 12, 'Alpha'),
                                                       (12, 15, 'BetaL'), (16, 20, 'BetaM'),
                                                       (21, 30, 'BetaH'),
                                                       (30, 64, 'Gamma')])

       
        eeg_data.append(bp.loc[:, 'Theta':'TotalAbsPow'])
        
    return eeg_dat
