"""Pronunciation check without a listener: synthesize app sentences, recognise them with an
offline Bangla speech recogniser (sherpa-onnx streaming zipformer, Vosk small Bangla model),
and report character/word error rates against the intended text.

    python3 roundtrip_eval.py chunks.json 120

Used to choose the respellings in lexicon.json and to confirm that a change helps. ASR errors
also count against the voice, so compare versions on the same sentences rather than reading
the absolute numbers. Native speakers should still listen during the pilot."""
import json, os, random, re, subprocess, sys
import numpy as np, scipy.signal as ss, sherpa_onnx
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normalize import normalize, speakable
M = os.environ.get("NV_MODEL", "vits-coqui-bn-custom_female/")
A = os.environ.get("NV_ASR", "sherpa-onnx-streaming-zipformer-bn-vosk-2026-02-09/")
tts = sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
    vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=M + "model.onnx", tokens=M + "tokens.txt"), num_threads=2)))
rec = sherpa_onnx.OnlineRecognizer.from_transducer(tokens=A + "tokens.txt", encoder=A + "encoder.onnx", decoder=A + "decoder.onnx",
                                                   joiner=A + "joiner.onnx", num_threads=2, sample_rate=16000)
def canon(t):
    t = t.replace("য়", "য়").replace("ড়", "ড়").replace("ঢ়", "ঢ়")
    return re.sub(r"\s+", " ", re.sub(r"[^ঀ-৿ ]|।", " ", t)).strip()
def lev(a, b):
    d = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        p = d[:]; d[0] = i
        for j, y in enumerate(b, 1): d[j] = min(p[j] + 1, d[j - 1] + 1, p[j - 1] + (x != y))
    return d[-1]
def hear(x, sr):
    s = rec.create_stream(); s.accept_waveform(16000, ss.resample_poly(x, 16000, sr).astype(np.float32))
    s.accept_waveform(16000, np.zeros(12800, dtype=np.float32)); s.input_finished()
    while rec.is_ready(s): rec.decode_stream(s)
    return rec.get_result(s)
d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "chunks.json"))
pool = sorted(c for c in d["keys"] if speakable(c) and len(c) > 18)
random.seed(11); S = random.sample(pool, min(len(pool), int(sys.argv[2]) if len(sys.argv) > 2 else 120))
C = E = W = WE = 0
for s in S:
    a = tts.generate(normalize(s), sid=0, speed=0.95)
    ref = canon(normalize(s, respell=False)); hyp = canon(hear(np.asarray(a.samples, dtype=np.float32), a.sample_rate))
    C += len(ref.replace(" ", "")); E += lev(ref.replace(" ", ""), hyp.replace(" ", "")); W += len(ref.split()); WE += lev(ref.split(), hyp.split())
print(f"{len(S)} sentences  CER {E / C * 100:.1f}%  WER {WE / W * 100:.1f}%")
