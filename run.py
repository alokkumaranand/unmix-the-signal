import glob
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import resample_poly
from scipy.stats import kurtosis
from scipy.optimize import linear_sum_assignment
from ica import center, whiten, fastica

SR = 16000
A = np.array([[0.65, 0.25, 0.10],
              [0.20, 0.60, 0.35],
              [0.30, 0.15, 0.75]])

lines = []


def say(text=""):
    print(text)
    lines.append(text)


def load_sources():
    names, signals = [], []
    for path in sorted(glob.glob("sources/*.wav")):
        sr, x = wavfile.read(path)
        x = x.astype(np.float64) / 32768
        if x.ndim > 1:
            x = x.mean(axis=1)
        if sr != SR:
            x = resample_poly(x, SR, sr)
        names.append(os.path.splitext(os.path.basename(path))[0])
        signals.append(x)
    n = min(len(x) for x in signals)
    S = np.array([x[:n] for x in signals])
    S = (S - S.mean(axis=1, keepdims=True)) / S.std(axis=1, keepdims=True)
    return names, S


def match(S, Y):
    k = len(S)
    C = np.corrcoef(S, Y)[:k, k:]
    rows, cols = linear_sum_assignment(-np.abs(C))
    return cols, C[rows, cols]


def si_sdr(s, y):
    target = (y @ s) / (s @ s) * s
    return 10 * np.log10((target @ target) / ((y - target) @ (y - target)))


def save_wav(path, x):
    x = x / np.abs(x).max() * 0.9
    wavfile.write(path, SR, (x * 32767).astype(np.int16))


names, S = load_sources()
k = len(names)
X = A @ S
Xc, _ = center(X)
Z, _ = whiten(Xc)
W = fastica(Z)
Y = W @ Z

ica_idx, ica_corr = match(S, Y)
pca_idx, pca_corr = match(S, Z)

os.makedirs("output", exist_ok=True)
os.makedirs("results", exist_ok=True)

for i in range(k):
    save_wav(f"output/mix_{i + 1}.wav", X[i])
    y = Y[ica_idx[i]] * np.sign(ica_corr[i])
    save_wav(f"output/separated_{names[i]}.wav", y)

say("Metrics (higher SI-SDR is better, correlation is absolute)")
say(f"{'source':<10}{'PCA corr':>10}{'PCA SDR':>10}{'ICA corr':>10}{'ICA SDR':>10}")
for i in range(k):
    say(f"{names[i]:<10}"
        f"{abs(pca_corr[i]):>10.3f}{si_sdr(S[i], Z[pca_idx[i]]):>10.1f}"
        f"{abs(ica_corr[i]):>10.3f}{si_sdr(S[i], Y[ica_idx[i]]):>10.1f}")

say()
say("Kurtosis (0 means Gaussian-like)")
say(f"{'source':<10}{'original':>10}")
for i in range(k):
    say(f"{names[i]:<10}{kurtosis(S[i]):>10.2f}")
say(f"mixtures   {', '.join(f'{kurtosis(x):.2f}' for x in X)}")
say(f"ICA output {', '.join(f'{kurtosis(Y[j]):.2f}' for j in ica_idx)}")

with open("results/metrics.txt", "w") as f:
    f.write("\n".join(lines) + "\n")

t = np.arange(S.shape[1]) / SR
rows = [("original", [S[i] for i in range(k)]),
        ("mixture", [X[i] for i in range(k)]),
        ("PCA", [Z[pca_idx[i]] for i in range(k)]),
        ("ICA", [Y[ica_idx[i]] * np.sign(ica_corr[i]) for i in range(k)])]
fig, axes = plt.subplots(len(rows), k, figsize=(12, 7), sharex=True)
for r, (label, sigs) in enumerate(rows):
    for c in range(k):
        ax = axes[r, c]
        ax.plot(t, sigs[c], lw=0.4)
        ax.set_yticks([])
        if c == 0:
            ax.set_ylabel(label)
        if r == 0:
            ax.set_title(names[c])
        if r == len(rows) - 1:
            ax.set_xlabel("seconds")
fig.tight_layout()
fig.savefig("results/waveforms.png", dpi=120)
