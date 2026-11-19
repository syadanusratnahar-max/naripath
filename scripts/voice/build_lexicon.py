"""Find words the voice mispronounces and pick a better respelling for each.
Every word in the app is synthesized alone and recognised with the offline Bangla ASR used in
roundtrip_eval.py. When the recogniser does not hear the intended word, the candidate respellings
from respell.py are tried, and the one heard most clearly is kept if it is clearly better.

    python3 build_lexicon.py chunks.json lexicon.json"""
import json, re, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import roundtrip_eval as rt  # loads the voice and the recogniser (also runs its sentence test once)
from normalize import normalize, speakable
from respell import candidates
import numpy as np
d = json.load(open(sys.argv[1])); out = sys.argv[2]
words = collections.Counter(w for c in d["keys"] if speakable(c) for w in re.findall(r"[ঀ-ৣ০-৿]+", normalize(c, respell=False)))
def score(text, target):
    a = rt.tts.generate(text + "।", sid=0, speed=0.95)
    h = rt.canon(rt.hear(np.asarray(a.samples, dtype=np.float32), a.sample_rate)).replace(" ", "")
    t = rt.canon(target).replace(" ", ""); return rt.lev(t, h) / max(1, len(t))
lex = json.load(open(out)) if os.path.exists(out) else {}
for w, _ in words.most_common():
    if w in lex: continue
    b = score(w, w)
    if b == 0: continue
    best = min(((score(c, w), c) for c in candidates(w)), default=(b, w))
    if best[0] <= 0.34 and best[0] < b - 0.15: lex[w] = best[1]
json.dump(dict(sorted(lex.items())), open(out, "w"), ensure_ascii=False, indent=0)
print(len(lex), "respellings")
