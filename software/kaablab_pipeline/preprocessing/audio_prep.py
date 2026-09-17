"""Etapa 4: pre-énfasis y troceado; gate de energía RMS (Etapa 5 parcial)."""
import numpy as np
from .. import config as C

def pre_emphasis(sig, a=None):
    a = C.PREEMPH if a is None else a
    return np.append(sig[0], sig[1:] - a * sig[:-1])

def frame_signal(sig, frame_len=None, hop=None):
    frame_len = frame_len or C.N_FFT
    hop = hop or C.HOP
    if len(sig) < frame_len:
        sig = np.pad(sig, (0, frame_len - len(sig)))
    n_frames = 1 + (len(sig) - frame_len) // hop
    idx = np.arange(frame_len)[None, :] + hop * np.arange(n_frames)[:, None]
    return sig[idx]

def rms_gate(frames, pctl=None):
    """Conserva tramas con energía RMS por encima del percentil dado (descarta silencios)."""
    pctl = C.RMS_GATE_PCTL if pctl is None else pctl
    rms = np.sqrt(np.mean(frames ** 2, axis=1) + 1e-12)
    thr = np.percentile(rms, pctl)
    keep = rms >= thr
    return frames[keep] if keep.any() else frames
