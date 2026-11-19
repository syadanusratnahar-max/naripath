"""Turn on-screen Bangla text into something the voice model can say.
The model only knows Bangla letters and a few punctuation marks, so numbers,
helplines, dates, percentages and symbols are written out as words."""
import re, json, os
from respell import ya_variant, decompose
# Pronunciation lexicon: respellings chosen by a speech-recognition round trip (see README).
LEX = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lexicon.json"), encoding="utf-8"))

W = ("শূন্য এক দুই তিন চার পাঁচ ছয় সাত আট নয় দশ এগারো বারো তেরো চৌদ্দ পনেরো ষোলো সতেরো আঠারো উনিশ "
     "বিশ একুশ বাইশ তেইশ চব্বিশ পঁচিশ ছাব্বিশ সাতাশ আটাশ ঊনত্রিশ ত্রিশ একত্রিশ বত্রিশ তেত্রিশ চৌত্রিশ পঁয়ত্রিশ ছত্রিশ সাঁইত্রিশ আটত্রিশ ঊনচল্লিশ "
     "চল্লিশ একচল্লিশ বিয়াল্লিশ তেতাল্লিশ চুয়াল্লিশ পঁয়তাল্লিশ ছেচল্লিশ সাতচল্লিশ আটচল্লিশ ঊনপঞ্চাশ পঞ্চাশ একান্ন বাহান্ন তিপ্পান্ন চুয়ান্ন পঞ্চান্ন ছাপ্পান্ন সাতান্ন আটান্ন ঊনষাট "
     "ষাট একষট্টি বাষট্টি তেষট্টি চৌষট্টি পঁয়ষট্টি ছেষট্টি সাতষট্টি আটষট্টি ঊনসত্তর সত্তর একাত্তর বাহাত্তর তিয়াত্তর চুয়াত্তর পঁচাত্তর ছিয়াত্তর সাতাত্তর আটাত্তর ঊনআশি "
     "আশি একাশি বিরাশি তিরাশি চুরাশি পঁচাশি ছিয়াশি সাতাশি অষ্টাশি ঊননব্বই নব্বই একানব্বই বিরানব্বই তিরানব্বই চুরানব্বই পঁচানব্বই ছিয়ানব্বই সাতানব্বই আটানব্বই নিরানব্বই").split()
assert len(W) == 100
HUND = ["", "একশো", "দুইশো", "তিনশো", "চারশো", "পাঁচশো", "ছয়শো", "সাতশো", "আটশো", "নয়শো"]
DIG = "শূন্য এক দুই তিন চার পাঁচ ছয় সাত আট নয়".split()
BN2EN = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
HELPLINES = {"999", "109", "333", "1090", "1098", "16135", "16263", "16699", "16430", "10921", "16123", "16256", "16000"}
MONTHS = {"জানু": "জানুয়ারি", "ফেব": "ফেব্রুয়ারি", "এপ্রি": "এপ্রিল", "জুল": "জুলাই", "আগ": "আগস্ট", "সেপ": "সেপ্টেম্বর",
          "অক্টো": "অক্টোবর", "নভে": "নভেম্বর", "ডিসে": "ডিসেম্বর"}


def words(n: int) -> str:
    if n < 100:
        return W[n]
    if n < 1000:
        h, r = divmod(n, 100)
        return HUND[h] + (" " + W[r] if r else "")
    if 1900 <= n <= 1999:  # years like ১৯৯০ are read as "উনিশশো নব্বই"
        r = n - 1900
        return "উনিশশো" + (" " + W[r] if r else "")
    if n < 100000:
        t, r = divmod(n, 1000)
        return words(t) + " হাজার" + (" " + words(r) if r else "")
    if n < 10000000:
        l, r = divmod(n, 100000)
        return words(l) + " লাখ" + (" " + words(r) if r else "")
    c, r = divmod(n, 10000000)
    return words(c) + " কোটি" + (" " + words(r) if r else "")


def digits(s: str) -> str:
    # phone numbers are read digit by digit with a short pause, as people read them aloud
    return ", ".join(DIG[int(d)] for d in s)


def pronounce(t: str) -> str:
    """Respell words the voice would mispronounce. অন্তঃস্থ য় is a glide or vowel, never /dʒ/:
    first the tested lexicon, then the general য় rules (য়ে → এ, final -ীয় → -ীও, হয় → হই ...)."""
    def fix(m):
        w = m.group(0)
        return LEX.get(w) or LEX.get(decompose(w)) or ya_variant(decompose(w), "A")
    return re.sub(r"[\u0980-\u09e3\u09e6-\u09ff\u200c]+", fix, t)


def num_token(raw: str) -> str:
    s = raw.translate(BN2EN).replace(",", "")
    if s in HELPLINES or (len(s) >= 10 and s.startswith("0")):
        return digits(s)
    if "." in s:
        a, b = s.split(".", 1)
        return words(int(a or 0)) + " দশমিক " + digits(b)
    if len(s) > 9:
        return digits(s)
    return words(int(s))


NUM = r"[0-9০-৯](?:[0-9০-৯,]*[0-9০-৯])?(?:\.[0-9০-৯]+)?"


def normalize(t: str, respell: bool = True) -> str:
    t = t.replace("‍", "")
    # dates like "১৮ নভে, ২০২৬"
    for k, v in MONTHS.items():
        t = re.sub(r"(?<=[0-9০-৯] )" + k + r"(?=[,\s]|$)", v, t)
    t = t.replace("·", ",")
    t = re.sub(r"[“”\"'‘’()\[\]→⋮•🌊✓✕★✗|]", " ", t)
    # fractions a/b → "b-টির মধ্যে a"
    t = re.sub(r"(" + NUM + r")\s*/\s*(" + NUM + r")", lambda m: num_token(m.group(2)) + "টির মধ্যে " + num_token(m.group(1)), t)
    # ranges ২–৭, ২০২৫–২০২৬
    t = re.sub(r"(" + NUM + r")\s*[–—-]\s*(" + NUM + r")", lambda m: num_token(m.group(1)) + " থেকে " + num_token(m.group(2)), t)
    t = re.sub(r"(" + NUM + r")\s*%", lambda m: num_token(m.group(1)) + " শতাংশ", t)
    t = re.sub(r"(" + NUM + r")\s*\+", lambda m: num_token(m.group(1)) + " বা তার বেশি", t)
    t = re.sub(NUM, lambda m: num_token(m.group(0)), t)
    t = t.replace("৳", " টাকা ")
    t = re.sub(r"[A-Za-z][A-Za-z0-9._@/-]*", " ", t)  # Latin words: the model cannot say them
    t = t.replace(":", ",").replace(";", ",").replace("/", " ").replace("@", " ").replace("–", ", ").replace("—", ", ")
    t = re.sub(r"\s+", " ", t).strip(" ,-")
    t = re.sub(r"\s+([,।?!.])", r"\1", t)
    if respell:
        t = pronounce(t)
    if t and t[-1] not in "।?!.":
        t += "।"
    return t


def speakable(orig: str) -> bool:
    letters = re.findall(r"[A-Za-z]", orig)
    bn = re.findall(r"[ঀ-৿]", orig)
    return len(bn) >= 2 and len(letters) <= 0.25 * (len(letters) + len(bn))


if __name__ == "__main__":
    for s in ["স্বাস্থ্য বাতায়ন ১৬২৬৩ ফোনে", "প্রতি পরিবারে মাসে ২,৫০০ টাকা", "৭৩% অবিবাহিত কিশোরী", "২০২৫–২০২৬ সালে",
              "০/৭ শেষ", "সর্বশেষ যাচাই: ১৮ নভে, ২০২৬", "নারী ৬২+, পুরুষ ৬৫+", "কল করুন 109", "১৯৯০ সালে", "১.৫ লাখ", "০১৩২০০০০৮৮৮",
              "মাসে ৭০০ টাকা · ৯০ বছরের বেশি হলে ১,০০০ টাকা", "আইফোনে Share চেপে Add to Home Screen চাপুন।", "১২০ দিনের", "৩৫২টি"]:
        print(speakable(s), "|", normalize(s))
