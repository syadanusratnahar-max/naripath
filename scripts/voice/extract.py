# Render every page in Bangla and collect exactly the sentences the app's reader speaks.
import asyncio, json
from playwright.async_api import async_playwright
import os,pathlib
U=pathlib.Path(os.environ.get("NV_APP","index.html")).resolve().as_uri()
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path=os.environ.get("CHROME","/usr/bin/google-chrome"))
        ctx=await b.new_context(viewport={"width":400,"height":860})
        await ctx.add_init_script("localStorage.setItem('naripath:lang',JSON.stringify('bn'));localStorage.setItem('naripath:tour',JSON.stringify(1));")
        pg=await ctx.new_page(); errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
        await pg.goto(U+"#home"); await pg.wait_for_timeout(400)
        res=await pg.evaluate("R.filter(r=>!r.office).map(r=>'r-'+r.id)")
        gds=await pg.evaluate("GUIDES.map(g=>'g-'+g.id)")
        les=await pg.evaluate("PS_LESSONS.map(l=>'period-'+l.id)")
        routes=["home","explore","learn","path","settings","about","gaps","navigator","check","allowances","apps","migrate","mother","disaster","map","district",
                "period","period-check","period-group","period-cal"]+les+gds+res
        out=[]
        async def grab(name):
            ch=await pg.evaluate("speechChunks(readableText(document.getElementById('view')))")
            out.append([name,ch])
        for r in routes:
            await pg.goto(U+"#"+r); await pg.wait_for_timeout(120)
            await grab(r)
            if r=="migrate":
                for k in ["abroad","home"]:
                    await pg.click(f"[data-migtab='{k}']"); await pg.wait_for_timeout(80); await grab(r)
            if r=="disaster":
                for k in ["during","after"]:
                    await pg.click(f"[data-distab='{k}']"); await pg.wait_for_timeout(80); await grab(r)
            if r=="mother":
                await pg.click("[data-mbmode='baby']"); await pg.wait_for_timeout(80); await grab(r)
        # explicit extras: lesson cards, quiz, tour, greetings, voice test, calendar statuses without dates
        extra=await pg.evaluate("""()=>{
          const o=[];
          PS_LESSONS.forEach(l=>psCards(l).forEach(c=>{ o.push(...speechChunks(raw(c[2]?{en:c[2].en+'. '+c[3].en,bn:c[2].bn+'। '+c[3].bn}:c[0]))); }));
          PS_Q.forEach(q=>o.push(...speechChunks(raw(q[0]))));
          TOUR.forEach(s=>o.push(...speechChunks(raw(s.t)+'।\\n'+raw(s.b))));
          ['শুভ রাত্রি','শুভ সকাল','শুভ দুপুর','শুভ বিকেল','শুভ সন্ধ্যা'].forEach(g=>o.push(g));
          o.push(...speechChunks('আমি নারীপথের কণ্ঠ। আমি আপনাকে প্রতিটি পাতা পড়ে শোনাতে পারি।'));
          return o; }""")
        out.append(["_extra",extra])
        months=await pg.evaluate("[...Array(12)].map((_,m)=>new Date(2026,m,18).toLocaleDateString('bn-BD',{day:'numeric',month:'short',year:'numeric'}))")
        keys=await pg.evaluate("(arr)=>Object.fromEntries(arr.map(c=>[c,nvKey(c)]))",list(set(c for _,ch in out for c in ch)))
        json.dump({"pages":out,"keys":keys,"months":months},open(os.environ.get("NV_CHUNKS","chunks.json"),"w"),ensure_ascii=False)
        allc=[c for _,ch in out for c in ch]
        print("pages",len(out),"chunks",len(allc),"unique",len(set(allc)),"chars",sum(len(c) for c in set(allc)),"errs",errs)
        await b.close()
asyncio.run(main())
