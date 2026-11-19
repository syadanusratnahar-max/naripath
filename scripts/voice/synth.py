"""Synthesize every Bangla sentence the app reads aloud (incremental: cached clips are reused).
Voice: Coqui TTS "bn/custom/vits-female" by @mobassir94 (Apache 2.0), run with sherpa-onnx."""
import json, os, sys, subprocess, time, hashlib, numpy as np
import sherpa_onnx
sys.path.insert(0, os.path.dirname(__file__))
from normalize import normalize, speakable
M = os.environ.get("NV_MODEL", "vits-coqui-bn-custom_female/")
CACHE = os.environ.get("NV_CACHE", "voice-cache")
os.makedirs(CACHE, exist_ok=True)
d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("NV_CHUNKS","chunks.json")))
keys = d["keys"]
def clip_id(text):  # recordings are cached by what is actually spoken, so pronunciation fixes re-record only what changed
    return hashlib.sha1(normalize(text).encode("utf-8")).hexdigest()[:16]
todo = {}
for c in keys:
    if speakable(c) and normalize(c):
        cid = clip_id(c)
        if not os.path.exists(f"{CACHE}/{cid}.opus"): todo[cid] = c
todo = [(c, cid) for cid, c in todo.items()]
print("to synthesize:", len(todo), "of", len(keys), flush=True)
if not todo: sys.exit(0)
tts = sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
    vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=M + "model.onnx", tokens=M + "tokens.txt"), num_threads=2)))
t0 = time.time(); tot = 0
for i, (c, k) in enumerate(todo):
    a = tts.generate(normalize(c), sid=0, speed=0.95)
    x = np.asarray(a.samples, dtype=np.float32)
    # trim long silence, add a short natural pause at the end
    nz = np.where(np.abs(x) > 0.01)[0]
    if len(nz): x = x[max(0, nz[0] - 800): nz[-1] + 1600]
    x = np.concatenate([x, np.zeros(int(a.sample_rate * 0.18), dtype=np.float32)])
    tot += len(x) / a.sample_rate
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()
    out = subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "s16le", "-ar", str(a.sample_rate), "-ac", "1", "-i", "-",
                          "-ar", "24000", "-c:a", "libopus", "-b:a", "20k", "-application", "voip", "-map_metadata", "-1",
                          "-fflags", "+bitexact", "-f", "ogg", "-"], input=pcm, capture_output=True).stdout
    open(f"{CACHE}/{k}.opus.tmp", "wb").write(out); os.replace(f"{CACHE}/{k}.opus.tmp", f"{CACHE}/{k}.opus")
    if i % 50 == 0: print(f"{i}/{len(todo)} audio {tot/60:.1f} min, elapsed {(time.time()-t0)/60:.1f} min", flush=True)
print("done", len(todo), f"audio {tot/60:.1f} min in {(time.time()-t0)/60:.1f} min", flush=True)
