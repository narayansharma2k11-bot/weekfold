#!/usr/bin/env python3
"""Build the Weekfold site.

Input:  config.json, src/*, data/editions/<number>.json (one file per weekly edition)
Output: docs/  (the folder your host serves: GitHub Pages "main /docs" or Netlify publish dir "docs")

Run:    python3 build.py          (exits with an error if any edition file is invalid)
"""
import datetime, html, json, pathlib, shutil, sys, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent
SRC, DATA, OUT = ROOT / 'src', ROOT / 'data' / 'editions', ROOT / 'docs'
CFG = json.loads((ROOT / 'config.json').read_text(encoding='utf-8'))
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


def main():
    eds = load()
    if errors:
        print('Build stopped. Fix these problems in data/editions/:', *errors, sep='\n  - ')
        sys.exit(1)
    if not eds:
        print('No editions in data/editions/.'); sys.exit(1)

    if OUT.exists():
        shutil.rmtree(OUT)
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
    for name, target in (('landing.html', 'index.html'), ('home.html', 'home.html')):
        t = (SRC / name).read_text(encoding='utf-8')
        t = t.replace('/*THEME*/', theme).replace('/*PHOTOS*/', photos_blob).replace('/*EDITIONS*/', blob).replace('/*CONFIG*/', cfg_blob).replace('/*ART*/', art).replace('/*SITE*/', site_js)
        og_image = (f'<meta property="og:image" content="{SITE}/img/{top_photo["file"]}">\n<meta name="twitter:image" content="{SITE}/img/{top_photo["file"]}">\n') if (SITE and top_photo) else ''
        if SITE:
            t = t.replace('<meta property="og:type"', f'<link rel="canonical" href="{canon[target]}">\n<meta property="og:url" content="{canon[target]}">\n{og_image}<link rel="alternate" type="application/rss+xml" title="Weekfold" href="{SITE}/feed.xml">\n<meta property="og:type"', 1)
        (OUT / target).write_text(t, encoding='utf-8')

    provider = PROVIDERS.get((CFG.get('newsletter') or {}).get('provider'), 'our email provider')
    priv = (SRC / 'privacy.html').read_text(encoding='utf-8')
    priv = priv.replace('/*THEME*/', theme).replace('/*TODAY*/', datetime.date.today().strftime('%-d %B %Y')).replace('/*PROVIDER*/', provider).replace('/*CONTACT*/', CFG.get('contact_email', ''))
    (OUT / 'privacy.html').write_text(priv, encoding='utf-8')
    shutil.copy(SRC / 'favicon.svg', OUT / 'favicon.svg')
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
    (OUT / 'newsletter' / 'latest.json').write_text(json.dumps({'number': eds[0]['number'], 'subject': subject}, ensure_ascii=False), encoding='utf-8')

    if SITE:
        (OUT / 'feed.xml').write_text(rss(eds), encoding='utf-8')
        today = datetime.date.today().isoformat()
        urls = ''.join(f'<url><loc>{SITE}/{p}</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq></url>' for p in ('', 'home.html', 'privacy.html'))
        (OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + '</urlset>\n')
        (OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
    else:
        (OUT / 'robots.txt').write_text('User-agent: *\nAllow: /\n')
        print('Note: config.json has no site_url yet, so feed.xml and sitemap.xml were skipped and email links are relative.')

    print(f'Photos: {len(man)} local copies served from docs/img/')
    for name in ('index.html', 'home.html'):
        print(f'{name}: {(OUT / name).stat().st_size // 1024} KB')
    for e in eds:
        print(f"Edition {e['number']}: {len(e['days'])} days, {sum(1 + len(d['more']) for d in e['days'])} stories")


if __name__ == '__main__':
    main()
