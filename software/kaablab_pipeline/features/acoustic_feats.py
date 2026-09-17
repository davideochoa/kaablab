"""Extracción acústica: 13 MFCC + ZCR + centroide + rolloff espectral (NumPy/SciPy)."""
import numpy as np
from scipy.fft import rfft, rfftfreq, dct
from .. import config as C
from ..preprocessing.audio_prep import frame_signal, rms_gate

def _hz_to_mel(f): return 2595.0 * np.log10(1.0 + f / 700.0)
def _mel_to_hz(m): return 700.0 * (10.0 ** (m / 2595.0) - 1.0)

def _mel_filterbank(n_mels, n_fft, fs):
    lo, hi = _hz_to_mel(0), _hz_to_mel(fs / 2)
    pts = _mel_to_hz(np.linspace(lo, hi, n_mels + 2))
    bins = np.floor((n_fft + 1) * pts / fs).astype(int)
    fb = np.zeros((n_mels, n_fft // 2 + 1))
    for m in range(1, n_mels + 1):
        l, c, r = bins[m - 1], bins[m], bins[m + 1]
        for k in range(l, c):
            if c != l: fb[m - 1, k] = (k - l) / (c - l)
        for k in range(c, r):
            if r != c: fb[m - 1, k] = (r - k) / (r - c)
    return fb

_FB = _mel_filterbank(C.N_MELS, C.N_FFT, C.FS_AUDIO)
_FREQS = rfftfreq(C.N_FFT, 1.0 / C.FS_AUDIO)

def extract_acoustic(sig):
    """Devuelve dict con mfcc_0..12, zcr, centroid, rolloff. sig ya pre-enfatizada."""
    frames = frame_signal(sig)
    frames = rms_gate(frames)
    win = np.hamming(frames.shape[1])
    spec = np.abs(rfft(frames * win, n=C.N_FFT, axis=1)) ** 2
    mel = spec @ _FB.T
    logmel = np.log(mel + 1e-10)
    mfcc = dct(logmel, type=2, axis=1, norm="ortho")[:, :C.N_MFCC]
    mfcc_mean = mfcc.mean(axis=0)
    psum = spec.sum(axis=1) + 1e-10
    centroid = (spec @ _FREQS) / psum
    cum = np.cumsum(spec, axis=1)
    roll = np.array([_FREQS[np.searchsorted(cum[i], 0.85 * cum[i, -1])] for i in range(spec.shape[0])])
    zcr = np.mean(np.abs(np.diff(np.sign(sig)))) / 2.0
    feats = {f"mfcc_{i}": float(mfcc_mean[i]) for i in range(C.N_MFCC)}
    feats.update(zcr=float(zcr), centroid=float(centroid.mean()), rolloff=float(roll.mean()))
    return feats
