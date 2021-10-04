import numpy as np
import mne
from scipy import signal
import pandas as pd
from scipy.integrate import simps

def bandpower_from_psd(psd, freqs, ch_names=None, bands=[(0.5, 4, 'Delta'),
                       (4, 8, 'Theta'), (8, 12, 'Alpha'), (12, 16, 'Sigma'),
                       (16, 30, 'Beta'), (30, 40, 'Gamma')], relative=True):

    # Type checks
    assert isinstance(bands, list), 'bands must be a list of tuple(s)'
    assert isinstance(relative, bool), 'relative must be a boolean'

    # Safety checks
    freqs = np.asarray(freqs)
    assert freqs.ndim == 1
    psd = np.atleast_2d(psd)
    assert psd.ndim == 2, 'PSD must be of shape (n_channels, n_freqs).'
    all_freqs = np.hstack([[b[0], b[1]] for b in bands])
    fmin, fmax = min(all_freqs), max(all_freqs)
    idx_good_freq = np.logical_and(freqs >= fmin, freqs <= fmax)
    freqs = freqs[idx_good_freq]
    res = freqs[1] - freqs[0]
    nchan = psd.shape[0]
    assert nchan < psd.shape[1], 'PSD must be of shape (n_channels, n_freqs).'
    if ch_names is not None:
        ch_names = np.atleast_1d(np.asarray(ch_names, dtype=str))
        assert ch_names.ndim == 1, 'ch_names must be 1D.'
        assert len(ch_names) == nchan, 'ch_names must match psd.shape[0].'
    else:
        ch_names = ['CHAN' + str(i).zfill(3) for i in range(nchan)]
    bp = np.zeros((nchan, len(bands)), dtype=np.float)
    psd = psd[:, idx_good_freq]
    total_power = simps(psd, dx=res)
    total_power = total_power[..., np.newaxis]

    # Check if there are negative values in PSD
    if (psd < 0).any():
        msg = (
            "There are negative values in PSD. This will result in incorrect "
            "bandpower values. We highly recommend working with an "
            "all-positive PSD. For more details, please refer to: "
            "https://github.com/raphaelvallat/yasa/issues/29")

    # Enumerate over the frequency bands
    labels = []
    for i, band in enumerate(bands):
        b0, b1, la = band
        labels.append(la)
        idx_band = np.logical_and(freqs >= b0, freqs <= b1)
        bp[:, i] = simps(psd[:, idx_band], dx=res)

    if relative:
        bp /= total_power

    # Convert to DataFrame
    bp = pd.DataFrame(bp, columns=labels)
    bp['TotalAbsPow'] = np.squeeze(total_power)
    bp['FreqRes'] = res
    # bp['WindowSec'] = 1 / res
    bp['Relative'] = relative
    bp['Chan'] = ch_names
    bp = bp.set_index('Chan').reset_index()
    # Add hidden attributes
    bp.bands_ = str(bands)
    return bp


def bandpower(data, sf=None, ch_names=None, hypno=None, include=(2, 3),
              win_sec=4, relative=True, bandpass=False,
              bands=[(0.5, 4, 'Delta'), (4, 8, 'Theta'), (8, 12, 'Alpha'),
                     (12, 16, 'Sigma'), (16, 30, 'Beta'), (30, 40, 'Gamma')],
              kwargs_welch=dict(average='median', window='hamming')):

    assert isinstance(bands, list), 'bands must be a list of tuple(s)'
    assert isinstance(relative, bool), 'relative must be a boolean'
    assert isinstance(bandpass, bool), 'bandpass must be a boolean'

    # Check if input data is a MNE Raw object
    if isinstance(data, mne.io.BaseRaw):
        sf = data.info['sfreq']  # Extract sampling frequency
        ch_names = data.ch_names  # Extract channel names
        data = data.get_data() * 1e6  # Convert from V to uV
        _, npts = data.shape
    else:
        # Safety checks
        assert isinstance(data, np.ndarray), 'Data must be a numpy array.'
        data = np.atleast_2d(data)
        assert data.ndim == 2, 'Data must be of shape (nchan, n_samples).'
        nchan, npts = data.shape
        # assert nchan < npts, 'Data must be of shape (nchan, n_samples).'
        assert sf is not None, 'sf must be specified if passing a numpy array.'
        assert isinstance(sf, (int, float))
        if ch_names is None:
            ch_names = ['CHAN' + str(i).zfill(3) for i in range(nchan)]
        else:
            ch_names = np.atleast_1d(np.asarray(ch_names, dtype=str))
            assert ch_names.ndim == 1, 'ch_names must be 1D.'
            assert len(ch_names) == nchan, 'ch_names must match data.shape[0].'

    if bandpass:
        # Apply FIR bandpass filter
        all_freqs = np.hstack([[b[0], b[1]] for b in bands])
        fmin, fmax = min(all_freqs), max(all_freqs)
        data = mne.filter.filter_data(data.astype('float64'), sf, fmin, fmax,
                                      verbose=0)

    win = int(win_sec * sf)  # nperseg

    if hypno is None:
        # Calculate the PSD over the whole data
        freqs, psd = signal.welch(data, sf, nperseg=win, **kwargs_welch)
        return bandpower_from_psd(psd, freqs, ch_names, bands=bands,
                                  relative=relative).set_index('Chan')
    else:
        # Per each sleep stage defined in ``include``.
        hypno = np.asarray(hypno)
        assert include is not None, 'include cannot be None if hypno is given'
        include = np.atleast_1d(np.asarray(include))
        assert hypno.ndim == 1, 'Hypno must be a 1D array.'
        assert hypno.size == npts, 'Hypno must have same size as data.shape[1]'
        assert include.size >= 1, '`include` must have at least one element.'
        assert hypno.dtype.kind == include.dtype.kind, ('hypno and include '
                                                        'must have same dtype')
        assert np.in1d(hypno, include).any(), ('None of the stages '
                                               'specified in `include` '
                                               'are present in hypno.')
        # Initialize empty dataframe and loop over stages
        df_bp = pd.DataFrame([])
        for stage in include:
            if stage not in hypno:
                continue
            data_stage = data[:, hypno == stage]
            freqs, psd = signal.welch(data_stage, sf, nperseg=win,
                                      **kwargs_welch)
            bp_stage = bandpower_from_psd(psd, freqs, ch_names, bands=bands,
                                          relative=relative)
            bp_stage['Stage'] = stag
            df_bp = df_bp.append(bp_stage)
        return df_bp.set_index(['Stage', 'Chan'])
