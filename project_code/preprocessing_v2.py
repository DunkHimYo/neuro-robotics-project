import mne
from meegkit import star
from meegkit.asr import ASR
from meegkit.utils.matrix import sliding_window
import numpy as np

def preprocessing(frame,sfreq):
    data = mne.evoked.detrend(frame)
    data = mne.filter.filter_data(data=data, l_freq=4, h_freq=50, sfreq=128,verbose=False)
    x = data.T
    y, w, _ = star.star(x,verbose=False)

    raw = y.T
    asr = ASR(method='euclid')

    train_idx = np.arange(0 * sfreq, 10 * sfreq, dtype=int)
    _, sample_mask = asr.fit(raw[:, train_idx])
    X = sliding_window(raw, window=int(sfreq), step=int(sfreq))
    Y = np.zeros_like(X)
    for i in range(X.shape[1]):
        Y[:, i, :] = asr.transform(X[:, i, :])
    Y=Y.transpose(1,2,0)

    return Y
