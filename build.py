#!/usr/bin/env python3
"""Build the Weekfold site.

Input:  config.json, src/*, data/editions/<number>.json (one file per weekly edition)
Output: docs/  (the folder your host serves: GitHub Pages "main /docs" or Netlify publish dir "docs")

Run:    python3 build.py          (exits with an error if any edition file is invalid)
"""
import datetime, html, json, pathlib, shutil, sys, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent
SRC, DATA = ROOT / 'src', ROOT / 'data' / 'editions'
CFG = json.loads((ROOT / 'config.json').read_text(encoding='utf-8'))
# Test version (branch test-features): build into its own folder and zip, so the live docs/ and weekfold-site.zip never change.
TEST = CFG.get('test_build') or {}
OUT = ROOT / (TEST.get('dir') or 'docs')
ZIP_NAME = TEST.get('zip') or 'weekfold-site.zip'
EXTRAS = ROOT / 'data' / 'extras'
SITE = (CFG.get('site_url') or '').rstrip('/')
INLINE_FULL = int(CFG.get('inline_full_editions', 4))
PROVIDERS = {'buttondown': 'Buttondown', 'kit': 'Kit'}

errors = []


def check(ed, path):
    for k in ('number', 'range', 'rangeLong', 'next', 'days'):
        if not ed.get(k):
            errors.append(f'{path.name}: missing "{k}"')
    if str(ed.get('number')) != path.stem:
        errors.append(f'{path.name}: "number" must match the file name')
    days = ed.get('days') or []
    if len(days) != 7:
        errors.append(f'{path.name}: expected 7 days, found {len(days)}')
    for d in days:
        for k, s in enumerate([d.get('lead')] + (d.get('more') or [])):
            where = f'{path.name} {d.get("date")} story {k}'
            if not isinstance(s, dict):
                errors.append(where + ': missing lead story'); continue
            for f in ('category', 'headline', 'dek', 'body'):
                if not s.get(f):
                    errors.append(f'{where}: missing "{f}"')
            if len(s.get('sources') or []) < 2:
                errors.append(f'{where}: needs at least 2 sources')
            for src in s.get('sources') or []:
                if not str(src.get('url', '')).startswith('http'):
                    errors.append(f'{where}: source without a URL')
    f = ed.get('featured', 0)
    if not isinstance(f, int) or not 0 <= f < len(days or [0]):
        errors.append(f'{path.name}: "featured" must be a day index 0-6')


def caption(story):
    im = story.get('image') or {}
    if isinstance(im, dict) and im.get('wiki'):
        t = im['wiki'].strip().replace(' ', '_')
        story['image'] = {'wiki': t}
    else:
        story.pop('image', None)
    story.pop('uncertain', None)
    return story


def load():
    eds = []
    for p in sorted(DATA.glob('*.json')):
        ed = json.loads(p.read_text(encoding='utf-8'))
        check(ed, p)
        ed['number'] = str(ed['number'])
        cw = DATA.parent / 'crosswords' / (str(ed['number']) + '.json')
        if cw.exists():
            ed['crossword'] = json.loads(cw.read_text(encoding='utf-8'))
        ed['days'] = sorted(ed.get('days') or [], key=lambda d: d['date'])
        for d in ed['days']:
            d['lead'] = caption(d['lead'])
            d['more'] = [caption(m) for m in d.get('more') or []]
        eds.append(ed)
    eds.sort(key=lambda e: int(e['number']), reverse=True)
    return eds


def partial(ed):
    """Short summary of an older edition: enough for archive cards and the date picker."""
    keep = ('category', 'headline', 'image')
    return {**{k: ed[k] for k in ('number', 'range', 'rangeLong', 'next', 'featured')}, 'partial': True,
            'days': [{'date': d['date'], 'lead': {k: d['lead'][k] for k in keep if k in d['lead']}, 'more': []} for d in ed['days']]}


def link(path):
    return (SITE + '/' + path) if SITE else path


def art_url(d, k):
    return link('home.html#a-' + d['date'] + '-' + str(k))


def day_name(iso):
    return datetime.date.fromisoformat(iso).strftime('%A %-d %B')


def newsletter(ed):
    """Markdown email for the edition (Buttondown sends Markdown; it also pastes cleanly into Kit or Mailchimp)."""
    f = ed['days'][ed.get('featured', 0)]['lead']
    lines = [f"**Edition {ed['number']} · {ed['rangeLong']}**", '',
             "This week's world news, one page for every day. Read it in one sitting and you're up to date.", '',
             f"[Open this week's book →]({link('index.html')})", '', '---', '']
    for d in ed['days']:
        lead = d['lead']
        lines += [f"## {day_name(d['date'])}", '', f"### [{lead['headline']}]({art_url(d, 0)})", '', lead['dek'], '']
        if d['more']:
            lines.append('Also that day:')
            for k, m in enumerate(d['more'], 1):
                lines.append(f"- [{m['headline']}]({art_url(d, k)})")
            lines.append('')
    lines += ['---', '', f"Every story on Weekfold names its sources. Past weeks: [Previous news]({link('home.html#previous')}).", '',
              f"Next edition: {ed['next']}. Made by Narayan Sharma."]
    subject = f"Weekfold {ed['number']}: {f['headline']}"
    return subject, '\n'.join(lines)


def email_html(ed):
    """Email-ready HTML for the edition (inline styles, table layout, works in Gmail/Outlook/Apple Mail).
    {{UNSUBSCRIBE_URL}} and {{INTRO}} are filled in per recipient by the Supabase edge functions."""
    e = html.escape
    serif = "'Playfair Display',Georgia,'Times New Roman',serif"; sans = "Roboto,'Segoe UI',Helvetica,Arial,sans-serif"
    f = ed['days'][ed.get('featured', 0)]['lead']
    rows = []
    for d in ed['days']:
        lead = d['lead']
        rows.append(f'<tr><td style="padding:26px 0 0"><div style="font:700 12px/1 {sans};letter-spacing:.14em;text-transform:uppercase;color:#a8231b">{e(day_name(d["date"]))} &middot; {e(lead["category"])}</div>'
                    f'<a href="{art_url(d, 0)}" style="display:block;margin-top:10px;font:700 23px/1.25 {serif};color:#0b0b0b;text-decoration:none">{e(lead["headline"])}</a>'
                    f'<div style="margin-top:8px;font:400 15px/1.55 {sans};color:#3d3b38">{e(lead["dek"])}</div>')
        if d['more']:
            rows.append(f'<div style="margin-top:12px;border-top:1px solid #e6e2d8;padding-top:10px">')
            for k, m in enumerate(d['more'], 1):
                rows.append(f'<div style="padding:5px 0;font:400 15px/1.45 {sans}"><span style="font:700 11px {sans};letter-spacing:.1em;text-transform:uppercase;color:#7a766d">{e(m["category"])}</span>&nbsp; '
                            f'<a href="{art_url(d, k)}" style="color:#0b0b0b;text-decoration:underline;text-decoration-color:#c9c3b5">{e(m["headline"])}</a></div>')
            rows.append('</div>')
        rows.append('</td></tr>')
    btn = lambda href, label, bg, fg: f'<a href="{href}" style="display:inline-block;background:{bg};color:{fg};font:700 14px/1 {sans};letter-spacing:.06em;text-transform:uppercase;text-decoration:none;padding:14px 22px;border:2px solid #0b0b0b">{label}</a>'
    return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e('Weekfold ' + str(ed['number']))}</title></head>
<body style="margin:0;padding:0;background:#f4efe4">
<div style="display:none;max-height:0;overflow:hidden;opacity:0">{e(f['headline'])} and the rest of the week, on one page.</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4efe4"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;background:#ffffff;border:1px solid #e3ddd0">
<tr><td style="padding:28px 32px 18px;border-bottom:3px double #0b0b0b">
 <a href="{link('index.html')}" style="font:900 34px/1 {serif};color:#0b0b0b;text-decoration:none">Weekfold</a>
 <div style="margin-top:10px;font:400 13px/1.4 {sans};color:#6b675f">Edition {e(str(ed['number']))} &middot; {e(ed['rangeLong'])}</div></td></tr>
<tr><td style="padding:22px 32px 4px;font:400 16px/1.6 {sans};color:#2b2a28">{{{{INTRO}}}}</td></tr>
<tr><td style="padding:14px 32px 0">{btn(link('home.html#current'), "Read this week's edition", '#1f3a6e', '#ffffff')}</td></tr>
<tr><td style="padding:0 32px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0">{''.join(rows)}</table></td></tr>
<tr><td style="padding:30px 32px 6px"><div style="background:#f4efe4;padding:20px 22px"><div style="font:700 19px/1.3 {serif};color:#0b0b0b">Today's mini crossword and Weekfold Word</div>
 <div style="margin:6px 0 14px;font:400 14px/1.5 {sans};color:#3d3b38">A new puzzle every day. Two minutes each.</div>{btn(link('home.html#crossword'), 'Play', '#ffffff', '#0b0b0b')}</div></td></tr>
<tr><td style="padding:22px 32px 30px;font:400 12px/1.6 {sans};color:#7a766d;border-top:1px solid #e6e2d8">
 Every story on Weekfold names its sources. Next edition: {e(ed['next'])}.<br>
 You're getting this because this address was entered at weekfold.in. <a href="{{{{UNSUBSCRIBE_URL}}}}" style="color:#7a766d">Unsubscribe</a> in one click.</td></tr>
</table></td></tr></table></body></html>"""


def md_to_html(md):
    """Tiny Markdown → HTML for the email preview file (headings, links, lists, bold, rules)."""
    import re
    out, in_list = [], False
    def inline(t):
        t = html.escape(t)
        t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
        return re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" style="color:#B42318">\1</a>', t)
    for ln in md.split('\n'):
        if ln.startswith('- '):
            if not in_list: out.append('<ul>'); in_list = True
            out.append('<li>' + inline(ln[2:]) + '</li>'); continue
        if in_list: out.append('</ul>'); in_list = False
        if ln.startswith('### '): out.append('<h3 style="font-family:Georgia,serif;font-size:20px;margin:6px 0">' + inline(ln[4:]) + '</h3>')
        elif ln.startswith('## '): out.append('<h2 style="font:600 12px monospace;letter-spacing:.1em;text-transform:uppercase;color:#D92D20;margin:28px 0 4px">' + inline(ln[3:]) + '</h2>')
        elif ln == '---': out.append('<hr style="border:0;border-top:1px solid #E6E8EE;margin:24px 0">')
        elif ln.strip(): out.append('<p>' + inline(ln) + '</p>')
    if in_list: out.append('</ul>')
    return ('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Weekfold</title></head>'
            '<body style="margin:0;background:#F5F6F8"><div style="max-width:620px;margin:0 auto;background:#fff;padding:28px 24px;font:16px/1.6 Arial,sans-serif;color:#15192B">'
            '<p style="font:700 26px Georgia,serif;margin:0 0 12px">Weekfold</p>' + '\n'.join(out) + '</div></body></html>')


def rss(eds):
    items = []
    for ed in eds[:4]:
        for d in reversed(ed['days']):
            s = d['lead']
            pub = datetime.datetime.fromisoformat(d['date'] + 'T18:00:00+00:00').strftime('%a, %d %b %Y %H:%M:%S +0000')
            items.append(f"<item><title>{html.escape(s['headline'])}</title><link>{html.escape(art_url(d, 0))}</link>"
                         f"<guid isPermaLink=\"false\">weekfold-{d['date']}-0</guid><pubDate>{pub}</pubDate>"
                         f"<category>{html.escape(s['category'])}</category><description>{html.escape(s['dek'])}</description></item>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>Weekfold</title>'
            f'<link>{SITE}/</link><description>The world\'s week, folded into one free edition every Sunday.</description><language>en</language>'
            + ''.join(items) + '</channel></rss>\n')


FONT_CSS = """@font-face{font-family:'Source Serif 4';src:url(fonts/SourceSerif4-Bold.woff) format('woff');font-weight:400 900;font-style:normal;font-display:swap}
@font-face{font-family:'Source Sans 3';src:url(fonts/SourceSans3-Regular.woff) format('woff');font-weight:100 499;font-display:swap}
@font-face{font-family:'Source Sans 3';src:url(fonts/SourceSans3-Bold.woff) format('woff');font-weight:500 900;font-display:swap}
:root{--display:'Source Serif 4',Georgia,'Times New Roman',serif;--ui:'Source Sans 3','Segoe UI',system-ui,sans-serif}
"""


def finish(t):
    """Test-build touches on every page: no Google Fonts request when fonts are self-hosted, and noindex so search engines skip the test copy."""
    import re
    if TEST.get('self_host_fonts'):
        t = re.sub(r'<link rel="preconnect" href="https://fonts\.(googleapis|gstatic)\.com"[^>]*>\n?', '', t)
        t = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/[^"]*">\n?', '', t)
        t = t.replace('<li><strong>Google Fonts</strong> supplies the typefaces.</li>', '<li>The typefaces (Source Serif 4 and Source Sans 3, free under the SIL Open Font Licence) are served from Weekfold itself, so reading a page does not contact Google.</li>')
    if TEST.get('noindex'):
        t = t.replace('<meta name="viewport"', '<meta name="robots" content="noindex, nofollow">\n<meta name="viewport"', 1)
    return t


def slug(s):
    import re
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def all_stories(eds):
    """Every story in every edition, oldest first, with its date and link."""
    out = []
    for ed in sorted(eds, key=lambda e: int(e['number'])):
        for d in ed['days']:
            for k, s in enumerate([d['lead']] + d['more']):
                out.append({**s, 'date': d['date'], 'ed': ed['number'], 'href': 'home.html#a-' + d['date'] + '-' + str(k)})
    return out


def items(stories):
    e = html.escape
    return '<ul class="items">' + ''.join(
        f'<li><span class="d">{e(day_name(s["date"]))} {s["date"][:4]} · {e(s["category"])}</span><a class="h" href="{s["href"]}">{e(s["headline"])}</a><p>{e(s.get("dek", ""))}</p></li>'
        for s in stories) + '</ul>'


def extra_pages(eds, glossary, timelines, tpl):
    """About, corrections, glossary, timelines and section pages. Plain HTML, built from the data; returns the file names."""
    import re
    e = html.escape
    made = []
    def page(name, title, desc, body):
        (OUT / name).write_text(tpl.replace('/*TITLE*/', e(title)).replace('/*DESC*/', e(desc)).replace('/*BODY*/', body), encoding='utf-8')
        made.append(name)
    st = all_stories(eds)
    # timelines
    def tl_match(x, s):
        if s.get('timeline'):
            return x['slug'] in ([s['timeline']] if isinstance(s['timeline'], str) else s['timeline'])
        t = (s['headline'] + ' ' + s.get('dek', '')).lower()
        return any(m in t for m in x['match']) and not any(m in t for m in x.get('exclude', []))
    rows = []
    for x in timelines:
        hits = [s for s in st if tl_match(x, s)]
        page(f'timeline-{x["slug"]}.html', x['title'], x['intro'],
             f'<p><a href="timelines.html">← All timelines</a></p><h1>{e(x["title"])}</h1><p class="lead">{e(x["intro"])}</p>'
             f'<p class="upd">{len(hits)} stories from Weekfold editions. It grows by itself every Sunday.</p>' + items(hits))
        if hits:
            rows.append(f'<li><span class="d">{len(hits)} stories · latest {e(day_name(hits[-1]["date"]))}</span><a class="h" href="timeline-{x["slug"]}.html">{e(x["title"])}</a><p>{e(x["intro"])}</p></li>')
    page('timelines.html', 'How we got here', 'Timelines of the big running stories, built from every Weekfold edition.',
         '<h1>How we got here</h1><p class="lead">The big stories that run for weeks, in order. Each one collects every Weekfold story on the subject, so you can catch up from the start.</p><ul class="items">' + ''.join(rows) + '</ul>')
    # glossary
    gl = sorted(glossary, key=lambda g: g['term'].lower())
    page('glossary.html', 'Words in the news, explained', 'Plain-English meanings of words that come up in the news.',
         '<h1>Words in the news, explained</h1><p class="lead">Short, plain meanings of words that come up in this week’s stories. Stories link here under “Words in this story”.</p>'
         '<dl class="gl">' + ''.join(f'<dt id="{slug(g["term"])}">{e(g["term"])}</dt><dd>{e(g["def"])}</dd>' for g in gl) + '</dl>')
    # sections
    cats = sorted({s['category'] for s in st})
    for c in cats:
        cs = [s for s in reversed(st) if s['category'] == c]
        page(f'section-{slug(c)}.html', c, f'Every Weekfold {c} story, newest first.',
             f'<p><a href="sections.html">← All sections</a></p><h1>{e(c)}</h1><p class="lead">Every {e(c)} story from Weekfold, newest first.</p>' + items(cs))
    page('sections.html', 'Sections', 'Weekfold stories by section.',
         '<h1>Sections</h1><p class="lead">Every Weekfold story, sorted by section.</p><ul class="chips">'
         + ''.join(f'<li><a href="section-{slug(c)}.html">{e(c)} ({sum(1 for s in st if s["category"] == c)})</a></li>' for c in cats) + '</ul>')
    # corrections
    fixes = [(s, c) for s in reversed(st) for c in (s.get('corrections') or [])]
    body = ''.join(f'<li><span class="d">{e(day_name(s["date"]))} {s["date"][:4]}</span><a class="h" href="{s["href"]}">{e(s["headline"])}</a><p>{e(c)}</p></li>' for s, c in fixes)
    page('corrections.html', 'Updates and corrections', 'Every correction Weekfold has made, newest first.',
         '<h1>Updates and corrections</h1><p class="lead">When we get something wrong, we fix it on the story and list it here, newest first. Spotted a mistake? Email '
         f'<a href="mailto:{e(CFG.get("contact_email", ""))}">{e(CFG.get("contact_email", ""))}</a>.</p>'
         + (f'<ul class="items">{body}</ul>' if body else '<p class="upd">No corrections so far.</p>'))
    # about
    outlets = {}
    for s in st:
        for src in s.get('sources') or []:
            n = re.split(r' \(|,| via | - ', src.get('name', ''))[0].strip()
            n = {'AP': 'Associated Press', 'AFP': 'Agence France-Presse'}.get(n, n)
            if n: outlets[n] = outlets.get(n, 0) + 1
    top = ', '.join(n for n, _ in sorted(outlets.items(), key=lambda kv: -kv[1])[:14])
    page('about.html', 'About Weekfold and how we check', 'Who makes Weekfold, where the news comes from and how it is checked.', f"""<h1>About Weekfold</h1>
<p class="lead">Weekfold folds the world's week into one free edition every Sunday: one page for each day, with the stories that still mattered by the end of the week.</p>
<h2>Who makes it</h2><p>Weekfold is made by Narayan Sharma. Stories are researched and drafted with the help of an AI assistant (Claude, made by Anthropic), working only from the reports named under each story, and then checked before the edition goes out.</p>
<h2>Where the news comes from</h2><p>Every story names at least two sources, linked so you can read them yourself: wire services, official statements and established news organisations. The outlets used most so far: {e(top)}.</p>
<h2>How we check</h2><ul><li>Every name, number, date and quote must appear in a source we read. Anything we cannot confirm is left out.</li><li>When reports disagree, we say so under “Where the reports differ”.</li><li>Claims are attributed (“police said”, “according to the UN”) and casualty figures carry their source and date.</li><li>Quotes are short, and the writing is our own.</li><li>Lines marked “analysis”, such as “What it could mean for India”, are Weekfold’s reading of the news, not reporting.</li></ul>
<h2>Mistakes</h2><p>We fix mistakes on the story and list them on the <a href="corrections.html">corrections page</a>. Email <a href="mailto:{e(CFG.get('contact_email', ''))}">{e(CFG.get('contact_email', ''))}</a>.</p>
<h2>Photos</h2><p>Only public-domain or Creative Commons images from Wikimedia Commons, credited beneath each picture. We do not use photos from news agencies.</p>
<h2>Listening</h2><p>The Listen buttons use your own device's built-in voice. It is free, nothing is sent anywhere, and voices differ from device to device.</p>
<h2>Privacy</h2><p>No ads and no tracking cookies. See the <a href="privacy.html">privacy page</a>.</p>""")
    return made


def main():
    eds = load()
    if errors:
        print('Build stopped. Fix these problems in data/editions/:', *errors, sep='\n  - ')
        sys.exit(1)
    if not eds:
        print('No editions in data/editions/.'); sys.exit(1)

    if OUT.exists():
        shutil.rmtree(OUT)
    if OUT.name != 'docs':
        print(f'TEST BUILD: writing to {OUT.name}/ (docs/ is left untouched)')
    (OUT / 'editions').mkdir(parents=True)
    (OUT / 'newsletter').mkdir()

    embedded = [e if i < INLINE_FULL else partial(e) for i, e in enumerate(eds)]
    blob = json.dumps(embedded, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    public_cfg = {'newsletter': CFG.get('newsletter') or {}, 'google_client_id': CFG.get('google_client_id') or '',
                  'contact_email': CFG.get('contact_email') or ''}
    cfg_blob = json.dumps(public_cfg, ensure_ascii=False).replace('</', '<\\/')
    # Story photos: scripts/fetch_photos.py (run by GitHub) saves them in data/photos/; the site serves its own copies from docs/img/.
    pdir = ROOT / 'data' / 'photos'
    man = json.loads((pdir / 'manifest.json').read_text(encoding='utf-8')) if (pdir / 'manifest.json').exists() else {}
    # Photos dropped in by hand: data/photos/<Wikipedia_title>.jpg|jpeg|png|webp (e.g. Riyadh.jpg)
    for f in sorted(pdir.glob('*')) if pdir.exists() else []:
        if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp') and f.stem not in man and f.name not in {m['file'] for m in man.values()}:
            man[f.stem] = {'file': f.name, 'credit': 'Wikimedia Commons', 'license': 'Free licence', 'page': 'https://en.wikipedia.org/wiki/' + f.stem}
    man = {t: m for t, m in man.items() if (pdir / m['file']).exists()}
    if man:
        (OUT / 'img').mkdir()
        for m in man.values():
            shutil.copy(pdir / m['file'], OUT / 'img' / m['file'])
    photos_blob = json.dumps({t: {'src': 'img/' + m['file'], 'credit': m.get('credit', ''), 'license': m.get('license', ''), 'page': m.get('page', '')} for t, m in man.items()},
                             ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    theme = (SRC / 'theme.css').read_text(encoding='utf-8')
    top = eds[0]['days'][eds[0].get('featured', 0)]['lead']
    top_photo = man.get(((top.get('image') or {}).get('wiki') or '').replace(' ', '_'))
    art = (SRC / 'art.js').read_text(encoding='utf-8')
    site_js = (SRC / 'site.js').read_text(encoding='utf-8')
    canon = {'index.html': SITE + '/', 'home.html': SITE + '/home.html'}
    world = (SRC / 'worldmap.txt').read_text(encoding='utf-8').strip() if (SRC / 'worldmap.txt').exists() else ''
    glossary = json.loads((EXTRAS / 'glossary.json').read_text(encoding='utf-8')) if (EXTRAS / 'glossary.json').exists() else []
    timelines = json.loads((EXTRAS / 'timelines.json').read_text(encoding='utf-8')) if (EXTRAS / 'timelines.json').exists() else []
    jsb = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    extras_js = (SRC / 'extras.js').read_text(encoding='utf-8')
    if TEST.get('self_host_fonts'):
        theme = theme + FONT_CSS
        (OUT / 'fonts').mkdir()
        for f in (SRC / 'fonts').glob('*.woff'):
            shutil.copy(f, OUT / 'fonts' / f.name)
    for name, target in (('landing.html', 'index.html'), ('home.html', 'home.html')):
        t = finish((SRC / name).read_text(encoding='utf-8'))
        t = t.replace('/*GLOSSARY*/', jsb(glossary)).replace('/*TIMELINES*/', jsb([{k: x[k] for k in ('slug', 'title', 'match', 'exclude') if k in x} for x in timelines])).replace('/*EXTRAS*/', extras_js)
        t = t.replace('/*THEME*/', theme).replace('/*PHOTOS*/', photos_blob).replace('/*EDITIONS*/', blob).replace('/*CONFIG*/', cfg_blob).replace('/*ART*/', art).replace('/*SITE*/', site_js).replace('/*WORLD*/', world).replace('/*MAP*/', (SRC / 'map.js').read_text(encoding='utf-8'))
        og_image = (f'<meta property="og:image" content="{SITE}/img/{top_photo["file"]}">\n<meta name="twitter:image" content="{SITE}/img/{top_photo["file"]}">\n') if (SITE and top_photo) else ''
        if SITE:
            t = t.replace('<meta property="og:type"', f'<link rel="canonical" href="{canon[target]}">\n<meta property="og:url" content="{canon[target]}">\n{og_image}<link rel="alternate" type="application/rss+xml" title="Weekfold" href="{SITE}/feed.xml">\n<meta property="og:type"', 1)
        (OUT / target).write_text(t, encoding='utf-8')

    nl = CFG.get('newsletter') or {}
    provider = 'Supabase (emails are sent through Resend)' if nl.get('supabase_url') else PROVIDERS.get(nl.get('provider'), 'our email provider')
    priv = finish((SRC / 'privacy.html').read_text(encoding='utf-8'))
    priv = priv.replace('/*THEME*/', theme).replace('/*TODAY*/', datetime.date.today().strftime('%-d %B %Y')).replace('/*PROVIDER*/', provider).replace('/*CONTACT*/', CFG.get('contact_email', ''))
    (OUT / 'privacy.html').write_text(priv, encoding='utf-8')
    pages = extra_pages(eds, glossary, timelines, finish((SRC / 'page.html').read_text(encoding='utf-8')).replace('/*THEME*/', theme))
    shutil.copy(SRC / 'favicon.svg', OUT / 'favicon.svg')
    for _f in ['favicon.ico','icon-48.png','icon-96.png','icon-180.png','icon-192.png','icon-512.png']:
        shutil.copy(SRC / _f, OUT / _f)
    for gf in SRC.glob('google*.html'):  # Search Console verification file(s) must survive every rebuild
        shutil.copy(gf, OUT / gf.name)
    (OUT / '.nojekyll').write_text('')
    if CFG.get('custom_domain'):
        (OUT / 'CNAME').write_text(CFG['custom_domain'].strip() + '\n')

    for ed in eds:
        (OUT / 'editions' / f"{ed['number']}.json").write_text(json.dumps(ed, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    subject, md = newsletter(eds[0])
    for stem in (eds[0]['number'], 'latest'):
        (OUT / 'newsletter' / f'{stem}.md').write_text(md, encoding='utf-8')
        (OUT / 'newsletter' / f'{stem}.html').write_text(md_to_html(md), encoding='utf-8')
    em = email_html(eds[0])
    for stem in (eds[0]['number'], 'latest'):
        (OUT / 'newsletter' / f'{stem}-email.html').write_text(em, encoding='utf-8')
    (OUT / 'newsletter' / 'latest.json').write_text(json.dumps({'number': int(eds[0]['number']), 'subject': subject, 'email': 'newsletter/latest-email.html',
                                                                 'range': eds[0]['rangeLong'], 'next': eds[0]['next']}, ensure_ascii=False), encoding='utf-8')

    if SITE:
        (OUT / 'feed.xml').write_text(rss(eds), encoding='utf-8')
        today = datetime.date.today().isoformat()
        urls = ''.join(f'<url><loc>{SITE}/{p}</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq></url>' for p in ['', 'home.html', 'privacy.html'] + pages)
        (OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + '</urlset>\n')
        (OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
    else:
        (OUT / 'robots.txt').write_text('User-agent: *\nAllow: /\n')
        print('Note: config.json has no site_url yet, so feed.xml and sitemap.xml were skipped and email links are relative.')

    # A ready-to-upload copy of the whole site for Hostinger: download it from <site>/weekfold-site.zip
    # and upload it into public_html with Hostinger's File Manager (Extract, replace existing files).
    import zipfile
    zpath = OUT / ZIP_NAME
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(OUT.rglob('*')):
            if f.is_file() and f != zpath and f.name != '.nojekyll':
                z.write(f, f.relative_to(OUT).as_posix())
    print(f'Hostinger upload: {OUT.name}/{ZIP_NAME} ({zpath.stat().st_size // 1024} KB)')
    print(f'Photos: {len(man)} local copies served from docs/img/')
    for name in ('index.html', 'home.html'):
        print(f'{name}: {(OUT / name).stat().st_size // 1024} KB')
    print(f'Extra pages: {len(pages)}')
    for e in eds:
        print(f"Edition {e['number']}: {len(e['days'])} days, {sum(1 + len(d['more']) for d in e['days'])} stories")


if __name__ == '__main__':
    main()
    import subprocess
    r = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'check_site.py'), str(OUT)])
    sys.exit(r.returncode)
