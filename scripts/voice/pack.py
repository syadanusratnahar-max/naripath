"""Bundle recorded sentences into one file per area of the app, plus a small index.
A phone only downloads the bundle for the page it is listening to."""
import json, os, sys, hashlib, collections
CACHE = os.environ.get("NV_CACHE", "voice-cache")
OUT = sys.argv[2] if len(sys.argv) > 2 else "audio/bn"
d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("NV_CHUNKS","chunks.json")))
keys = d["keys"]
def group(page):
    if page.startswith("period"): return "period"
    if page.startswith("r-") or page.startswith("g-"): return page  # one small bundle per service or guide
    if page in ("explore", "district"): return "services"
    if page == "learn": return "learn"
    if page in ("settings", "about", "gaps"): return "settings"
    if page in ("navigator", "check", "path", "apps"): return "plan"
    if page in ("allowances", "migrate", "mother", "disaster", "map", "home"): return page
    return "extra"
where = collections.defaultdict(list)
for page, chunks in d["pages"]:
    g = "home" if page == "_extra" else group(page)
    for c in chunks:
        if g not in where[c]: where[c].append(g)
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT): os.remove(os.path.join(OUT, f))
packs = collections.defaultdict(list)
for c, gs in where.items():
    k = keys[c]
    if not os.path.exists(f"{CACHE}/{k}.opus"): continue
    packs["common" if len(gs) >= 3 else gs[0]].append(k)
index = {"v": 0, "voice": "Coqui TTS bn/custom/vits-female by @mobassir94 (Apache-2.0)", "packs": {}, "clips": {}}
allh = hashlib.sha1()
for pid, ks in sorted(packs.items()):
    blob = bytearray(); seen = set()
    for k in sorted(ks):
        if k in seen: continue
        seen.add(k); b = open(f"{CACHE}/{k}.opus", "rb").read()
        index["clips"][k] = [pid, len(blob), len(b)]; blob += b
    h = hashlib.sha1(blob).hexdigest()[:10]; allh.update(h.encode())
    fn = f"{pid}-{h}.ogg"; open(os.path.join(OUT, fn), "wb").write(blob)
    index["packs"][pid] = {"f": fn, "b": len(blob)}
index["v"] = int(allh.hexdigest()[:7], 16)
json.dump(index, open(os.path.join(OUT, "index.json"), "w"), separators=(",", ":"))
print({p: (len(v), round(index["packs"][p]["b"]/1024)) for p, v in packs.items() if p in index["packs"]}, "total KB", round(sum(p["b"] for p in index["packs"].values())/1024), "clips", len(index["clips"]))
