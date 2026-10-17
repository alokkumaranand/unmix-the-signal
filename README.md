# Unmix the Signal

Three audio clips (speech, music, ambient noise) are mixed together with a made-up mixing matrix. Then I pull them apart again using ICA that I wrote myself, with no ICA library.

## Run it

```
pip install -r requirements.txt
python run.py
```

It reads every `.wav` in `sources/`, mixes them, separates them, and writes:

- `output/` - the three mixes and the three separated sources (all playable wavs)
- `results/waveforms.png` - original vs mixture vs PCA vs ICA
- `results/metrics.txt` - the scores

## Files

- `ica.py` - centering, PCA whitening (covariance + eigendecomposition) and FastICA
- `run.py` - loads audio, mixes, separates, scores, saves audio and plots
- `writeup.md` - results and the short explanations

## Audio sources

All clips are about 3.9 seconds, mono, 16 kHz. I only trimmed them and scaled the volume.

| File | What it is | Link |
|---|---|---|
| `speech.wav` | CMU ARCTIC, speaker aew, utterance a0001 | http://www.festvox.org/cmu_arctic/ |
| `ambient.wav` | "doing the dishes" background noise from Google's Speech Commands dataset (taken from about 42 s in) | https://research.googleblog.com/2017/08/launching-speech-commands-dataset.html |
| `music.wav` | a short singing clip, resampled from 8 kHz. Its origin is unknown | https://github.com/LCAV/pyroomacoustics/tree/master/examples/input_samples |

The speech and noise clips came from the pyroomacoustics repo's sample folder (linked above). The singing clip's origin isn't documented there, so swap it for a clip you have rights to before sharing this publicly. Any wav files you drop in `sources/` will work, as long as the number of sources matches the 3x3 mixing matrix in `run.py`.

## Result in one line

ICA recovers all three sources almost perfectly (SI-SDR 39 to 49 dB). PCA on its own does not (about -2 to 4 dB). Details in `writeup.md`.
