# Weekly update: instructions for the Sunday task

These are the instructions Claude's Sunday scheduled task follows in this repository. Anyone can follow them by hand too.

## What changes each week
Add **one new file**: `data/editions/<number>.json`. Then run `python3 build.py`, which rebuilds everything in `docs/`. Commit both in **one commit** and push to `main`.
- Your host (GitHub Pages or Netlify) redeploys `docs/` within a minute or two.
- The GitHub Action `Sunday newsletter` sees the new edition file and creates the week's email in Buttondown.

Never edit `docs/` by hand. Never change or delete older edition files, except to fix a factual error. Note any such fix in `corrections` (see below).

## Dates
- The new edition covers the 7 days from the day after the last date in the newest existing edition up to and including Saturday (Asia/Kolkata time). Normally that is Sunday to Saturday.
- `number` = previous number + 1, as a string. The file name must match it: `"number": "42"` → `data/editions/42.json`.

## File format
```json
{
  "number": "42",
  "range": "12 – 18 Oct 2026",
  "rangeLong": "12 – 18 October 2026",
  "next": "Sunday 25 October",
  "featured": 3,
  "days": [
    { "date": "2026-10-12", "lead": STORY, "more": [STORY, STORY] }
  ]
}
```
`featured` is the index (0–6) of the day whose lead is the week's most important story. There are exactly 7 days, oldest first.

STORY:
```json
{
  "category": "World | Politics | Conflict | Business | Tech | Science | Health | Climate | Sport | Culture",
  "headline": "12 words or fewer",
  "dek": "One-sentence summary.",
  "body": ["paragraph", "paragraph"],
  "why": "1–2 sentences on why it matters.",
  "sources": [{ "name": "Reuters", "url": "https://..." }, { "name": "BBC News", "url": "https://..." }],
  "image": { "wiki": "Exact_English_Wikipedia_article_title" }
}
```
Optional: `"corrections": ["What was corrected and when."]` on a story.

Optional extras (test version, branch `test-features`). Use only facts already in the story and its sources:
```json
"facts":  { "who": "...", "what": "...", "where": "...", "when": "...", "why": "...", "how": "...", "howMuch": "..." },
"differ": "Where the sources disagree (numbers, dates, who is blamed). Leave out if they agree.",
"watch":  "What happens next, with dates if the sources give them.",
"india":  "For stories not mainly about India: one hedged sentence on why it could matter in India. Shown as analysis. No new numbers or names.",
"timeline": "iran-war-and-the-gulf"
```
`timeline` is only needed to override the automatic match. Timelines live in `data/extras/timelines.json` (keywords decide which stories join each one) and the glossary in `data/extras/glossary.json`; both pages rebuild themselves. Section pages, corrections and the About page are also built from the editions.
On this branch `python3 build.py` writes to `test-site/` and `test-site/weekfold-test.zip`, and never touches `docs/`.

## Research and writing rules
1. Each day has one lead (the biggest **global** story) plus 2–3 more significant stories across different categories.
2. **At least 2 independent sources per story**, from established outlets or official statements: Reuters, AP, AFP, BBC, Al Jazeera, The Guardian, NPR, CNBC, government and UN releases. Every number, name and quote must come from a page you actually read. Leave out anything you can't confirm. `build.py` refuses to build if a story has fewer than 2 sources.
3. Own words only, never copied sentences. At most one direct quote, under 12 words, per story.
4. Length: leads get 4–6 paragraphs (350–550 words) covering what happened, key names and numbers, background, reactions and what comes next. Other stories get 2–3 paragraphs (150–250 words).
5. Neutral tone. Attribute claims ("police said", "according to the UN"). Give casualty figures with their source and date.

## Photos (copyright)
- Do **not** use photos from news outlets or agencies. They are not free to reuse.
- `image.wiki` names an English Wikipedia article about the main person, place or institution. Open `https://en.wikipedia.org/wiki/<Title>` to make sure it exists.
- The site loads that article's lead image and shows it if it is **public domain, CC0, CC BY or CC BY-SA**, with the photographer and licence credited under the picture. Never use NC/ND files. Choose Wikipedia articles whose lead photo exists (check the article page shows a photo, ideally a real photograph of the person, place or event, not a logo or map); an illustration is only a last resort. Aim for zero illustrations.

## Before you push
- `python3 build.py` finishes with no errors.
- Spot-check 3 stories against their sources.
- Commit message: `Edition <number>: <dates>`.
