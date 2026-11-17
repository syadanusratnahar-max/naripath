# NariPath — নারীপথ

**A bilingual (Bangla/English) digital companion that helps women in Bangladesh find support, discover opportunities and navigate life with confidence.**

Millennium Fellowship project prototype · Live demo: https://syadanusratnahar-max.github.io/naripath/

NariPath does not replace existing organisations or provide medical, legal, financial or emergency services. It makes the support systems that already exist easier to discover, understand and use.

## What it does

- **Six areas of support:** Education & Career, Health & Wellbeing, Rights & Legal Support, Personal & Digital Safety, Financial Independence, Everyday Life & Community.
- **What should I do next?** Start from your situation (study, work, health, rights, online problems, money) and get a step-by-step action plan linked to services and guides. Save it and tick off steps.
- **Support near you:** choose any of the 64 districts to see local services with address, contact, eligibility, cost, source, checked date and status, then nationwide services. Shows which districts have local information and which have not yet been researched.
- **Learn and understand:** five short guides (online safety, money and fraud, preparing for work, basic rights, reliable health information), each with sources.
- **Resource Passport:** every listing shows who it is for, cost, documents, contact, original sources, last-checked date and verification status.
- **My Path dashboard:** saved listings, plans and Action Paths with progress, and "continue where you left off". Optional, private (stored only in the browser) and clearable in one tap.
- **Relevance checker:** four tap-only questions show *potentially relevant* services, which answers matched and what still needs confirming. It never decides eligibility; answers are never saved.
- **Discreet mode:** hide saved items in My Path.
- **Report a problem:** wrong phone number, broken link, closed service, changed eligibility, wrong cost. Reports stay on the device in this prototype and can be copied to send to the team.
- **Read aloud** in Bangla or English (on-device voices preferred), **tap-to-call** and **copy number** buttons.
- **Information Gap Finder:** an admin view that separates information *not yet researched* from information *checked and not publicly available*, with coverage across all 64 districts.

## Data

28 public-source records (Type A) from official and reputable sources, checked 13 November 2026, including the 109 and 999 helplines, Police Cyber Support for Women, Shastho Batayon 16263, the government legal aid helpline 16699, District Legal Aid Offices, BLAST, One-Stop Crisis Centres, SME Foundation's WE-HELP, Bangladesh Bank women-entrepreneur refinancing, UGC merit scholarships and SICIP skills training. Every record lists its sources in the app.

Every listing describes a real service. None is fictional, and no provider has confirmed its listing yet.

| Status | Meaning |
| --- | --- |
| Public-source information | Found in a public source |
| Awaiting provider confirmation | Direct confirmation requested, pending |
| Provider-confirmed | The provider confirmed it, with reviewer and date |
| Needs review | May be out of date (set automatically when the review date passes) |
| Demo record | Synthetic test data (none in this version) |

A source URL alone never makes a listing provider-confirmed. Local listings currently cover 9 of Bangladesh's 64 districts; other districts rely on nationwide services.

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

No account, no tracking, no names or locations collected. Saved items, Action Paths and Trusted Circle contacts stay in the user's own browser and can be cleared at any time. NariPath is not an emergency service. Personal safety alerts (check-in timer, trusted-contact alerts) are listed only as planned future work: they would need a native Android app, an SMS provider, weekly delivery tests and safeguarding review before being built.

## Roadmap

1. Test with women from different backgrounds and districts.
2. Connect the Supabase database and shared problem reports.
3. Expand district coverage and confirm direct contacts with providers (Type C).
4. Only after safeguarding review: a native Android app for safety alerts, with weekly delivery tests.
