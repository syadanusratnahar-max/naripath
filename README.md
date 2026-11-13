# NariPath — নারীপথ

**A bilingual (Bangla/English) digital companion that helps women in Bangladesh find support, discover opportunities and navigate life with confidence.**

Millennium Fellowship project prototype · Live demo: https://syadanusratnahar-max.github.io/naripath/

NariPath does not replace existing organisations or provide medical, legal, financial or emergency services. It makes the support systems that already exist easier to discover, understand and use.

## What it does

- **Six areas of support:** Education & Career, Health & Wellbeing, Rights & Legal Support, Personal & Digital Safety, Financial Independence, Everyday Life & Community.
- **Life Situation Navigator:** start from "I want to…" instead of a category, get suggested next steps and matching services.
- **Resource Passport:** every listing shows who it is for, cost, documents, contact, original sources, last-checked date and verification status.
- **Personal Action Path:** turn any listing into a checklist with progress tracking.
- **Eligibility checker:** four tap-only questions; answers are never saved.
- **Safety tools (simulated):** Trusted Circle alert, safety check-in timer, hidden trigger, fake incoming call, loud alarm.
- **Quick exit and discreet mode:** one tap covers the app with a recipe page.
- **Read aloud** in Bangla or English, **tap-to-call** and **copy number** buttons.
- **Information Gap Finder:** an admin view showing districts and areas with missing or unconfirmed information.

## Data

28 public-source records (Type A) from official and reputable sources, checked 13 November 2026, including the 109 and 999 helplines, Police Cyber Support for Women, Shastho Batayon 16263, the government legal aid helpline 16699, District Legal Aid Offices, BLAST, One-Stop Crisis Centres, SME Foundation's WE-HELP, Bangladesh Bank women-entrepreneur refinancing, UGC merit scholarships and SICIP skills training. Every record lists its sources in the app.

| Type | Meaning |
| --- | --- |
| A — Public source | Taken from a public website or publication, with source and checked date |
| B — Demo | Fictional test data (none in this version) |
| C — Provider-verified | Confirmed with the provider (none yet; needs partnerships) |

Information can change. Always confirm with the provider before acting.

## Files

| Path | Purpose |
| --- | --- |
| `index.html` | The whole app: one self-contained page, no build step |
| `db/schema.sql` | Supabase/PostgreSQL schema for the next version |
| `db/resources.json` | The 28 records, ready to import |

## Run it

Open `index.html` in any browser, or visit the live demo. To host your own copy, enable GitHub Pages (Settings → Pages → Branch: `main`, folder: `/ (root)`).

## Privacy

No account, no tracking, no names or locations collected. Saved items, Action Paths and Trusted Circle contacts stay in the user's own browser and can be cleared at any time. Safety alerts are simulated in this prototype; real sending needs a native Android app and an SMS service, and will only be built with safeguarding review.

## Roadmap

1. Test with women from different backgrounds and districts.
2. Connect the Supabase database and shared problem reports.
3. Expand district coverage and confirm direct contacts with providers (Type C).
4. Native Android app for real safety alerts, with weekly delivery tests.
