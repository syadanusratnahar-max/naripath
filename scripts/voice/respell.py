"""Candidate phonetic respellings for Bangla words the voice may mispronounce.
Based on standard Bangla pronunciation: অন্তঃস্থ য় is a glide or vowel (never /dʒ/),
ক্ষ = /kkʰ/ (/kʰ/ at word start), জ্ঞ = /gg/ (/gæ/ at word start), and য-ফলা is
/æ/ after a word-initial consonant but doubles the consonant inside a word."""
import re
NUK="়"; YA="য"+NUK
SIGN2IND={"া":"আ","ি":"ই","ী":"ঈ","ু":"উ","ূ":"ঊ","ে":"এ","ৈ":"ঐ","ো":"ও","ৌ":"ঔ"}
SIGNS="".join(SIGN2IND); HAS="্"
CONS="কখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহ"
def decompose(w): return w.replace("য়",YA).replace("ড়","ড"+NUK).replace("ঢ়","ঢ"+NUK)
def precompose(w): return w.replace(YA,"য়").replace("ড"+NUK,"ড়").replace("ঢ"+NUK,"ঢ়")
def ya_variant(w,style):
    out=[]; i=0
    while i<len(w):
        if w.startswith(YA,i):
            prev=w[i-1] if i else ""; nxt=w[i+2] if i+2<len(w) else ""
            if nxt in SIGN2IND:
                ind=SIGN2IND[nxt]
                out.append(("ই"+ind) if style=="B" and nxt in "াো" and prev not in "িী" else ind); i+=3; continue
            if nxt==HAS: out.append("ই"); i+=3; continue
            final = (i+2==len(w))
            if final:
                if style=="E": out.append("এ")
                elif prev in "িী": out.append("ও" if style!="B" else "অ")
                elif prev in "েৈ": out.append("এ" if style!="B" else "ই")
                elif style=="D": out.append("অ")
                else: out.append("ই")
            else:
                out.append({"A":"অ","B":"ইঅ","D":"ও","E":"অ"}[style])
            i+=2; continue
        out.append(w[i]); i+=1
    return "".join(out)
def candidates(word):
    w=decompose(word); c=[]
    if YA in w:
        for st in "ABDE": c.append(ya_variant(w,st))
    if "ক্ষ" in w:
        c.append(re.sub(r"^ক্ষ","খ",w).replace("ক্ষ","ক্খ"))
    if "জ্ঞ" in w:
        c.append(re.sub(r"^জ্ঞ","গ্য",w).replace("জ্ঞ","গ্গ"))
    if HAS+"য" in w and YA not in w[w.find(HAS+"য")+1:w.find(HAS+"য")+3]:
        v=w
        v=re.sub(r"^(["+CONS+"])"+HAS+"য(?!["+SIGNS+"])",r"\1"+HAS+"যা",v)          # initial: ব্যবস্থা → ব্যাবস্থা
        v=re.sub(r"(?<=[^\s])(["+CONS+"])"+HAS+"য(?=["+SIGNS+"])",r"\1"+HAS+r"\1",v)   # medial before vowel: বিদ্যা → বিদ্দা
        v=re.sub(r"(?<=.)(["+CONS+"])"+HAS+"য$",r"\1"+HAS+r"\1ো",v)                    # final: স্বাস্থ্য → স্বাস্থ্থো
        if v!=w: c.append(v)
    if NUK in w: c.append(precompose(w))
    seen=[]; [seen.append(x) for x in c if x!=w and x not in seen]
    return seen
if __name__=="__main__":
    for w in ["হয়","নয়","জাতীয়","দিয়ে","প্রয়োজন","সহায়তা","বায়ান","অফিসিয়াল","ওয়েবসাইট","খাওয়া","ব্যবস্থা","স্বাস্থ্য","বিদ্যা","জ্ঞান","ক্ষমতা","পক্ষ","বড়","ইউনিয়ন","সময়"]:
        print(w,"→",candidates(w))
