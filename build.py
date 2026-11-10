#!/usr/bin/env python3
"""Build the Weekfold site.

Input:  config.json, src/*, data/editions/<number>.json (one file per weekly edition)
Output: docs/  (the folder your host serves: GitHub Pages "main /docs" or Netlify publish dir "docs")

Run:    python3 build.py          (exits with an error if any edition file is invalid)
"""
import datetime, html, json, pathlib, shutil, sys, urllib.parse
import seo

ROOT = pathlib.Path(__file__).resolve().parent
SRC, DATA, OUT = ROOT / 'src', ROOT / 'data' / 'editions', ROOT / 'docs'
CFG = json.loads((ROOT / 'config.json').read_text(encoding='utf-8'))
SITE = (CFG.get('site_url') or '').rstrip('/')
INLINE_FULL = int(CFG.get('inline_full_editions', 4))
PROVIDERS = {'buttondown': 'Buttondown', 'kit': 'Kit', 'hostinger': 'Hostinger (emails are sent from our own mailbox)'}

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
    s = ([d['lead']] + d['more'])[k]
    return link(s['path']) if s.get('path') else link('home.html#a-' + d['date'] + '-' + str(k))


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


def main():
    eds = load()
    recs = seo.assign(eds)
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
    # Photos dropped in by hand: data/photos/<Wikipedia_title>.jpg|jpeg|png|webp (e.g. Riyadh.jpg)
    for f in sorted(pdir.glob('*')) if pdir.exists() else []:
        if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp') and f.stem not in man and f.name not in {m['file'] for m in man.values()}:
            man[f.stem] = {'file': f.name, 'credit': 'Wikimedia Commons', 'license': 'Free licence', 'page': 'https://en.wikipedia.org/wiki/' + f.stem}
    lic_file = pdir / 'licences.json'   # filled by scripts/get_licences.py: {title: {source_file, license, artist}}
    lics = json.loads(lic_file.read_text(encoding='utf-8')) if lic_file.exists() else {}
    man = {t: dict(m) for t, m in man.items() if (pdir / m['file']).exists()}
    for t, m in man.items():
        L = lics.get(t) or {}
        if L.get('license'): m['license'] = L['license']
        if L.get('artist'): m['artist'] = L['artist']
        if L.get('source_file'): m['file_page'] = 'https://commons.wikimedia.org/wiki/File:' + urllib.parse.quote(L['source_file'].replace(' ', '_'))
    if man:
        from PIL import Image
        (OUT / 'img').mkdir()
        for m in man.values():
            im = Image.open(pdir / m['file']); im = im.convert('RGB')
            if im.width > 1000:
                im = im.resize((1000, round(im.height * 1000 / im.width)), Image.LANCZOS)
            m['file'] = pathlib.Path(m['file']).stem + '.webp'
            im.save(OUT / 'img' / m['file'], 'WEBP', quality=68, method=6)
    photos_blob = json.dumps({t: {'src': 'img/' + m['file'], 'credit': m.get('artist') or m.get('credit', ''), 'license': m.get('license', ''), 'page': m.get('file_page') or m.get('page', '')} for t, m in man.items()},
                             ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    theme = (SRC / 'theme.css').read_text(encoding='utf-8')
    top = eds[0]['days'][eds[0].get('featured', 0)]['lead']
    top_photo = man.get(((top.get('image') or {}).get('wiki') or '').replace(' ', '_'))
    art = (SRC / 'art.js').read_text(encoding='utf-8')
    site_js = (SRC / 'site.js').read_text(encoding='utf-8')
    canon = {'index.html': SITE + '/', 'home.html': SITE + '/home.html'}
    world = (SRC / 'worldmap.txt').read_text(encoding='utf-8').strip() if (SRC / 'worldmap.txt').exists() else ''
    for name, target in (('landing.html', 'index.html'), ('home.html', 'home.html')):
        t = (SRC / name).read_text(encoding='utf-8')
        ftop = eds[0]['days'][eds[0].get('featured', 0)]['lead']
        if target == 'home.html':
            ttl = f"Weekfold {eds[0]['number']}: {ftop['headline']} | Weekly world news"
            dsc = f"This week's world news, {eds[0]['rangeLong']}: " + '; '.join(d['lead']['headline'] for d in eds[0]['days'][:3]) + '. Free, sourced, every Sunday.'
        else:
            ttl = 'Weekfold: free weekly world news, one page for every day'
            dsc = "Weekfold folds the world's week into one free edition every Sunday: the stories that mattered, one page for every day, every story sourced."
        t = t.replace('<title>Weekfold</title>', '<title>' + html.escape(ttl) + '</title>', 1).replace('<meta property="og:title" content="Weekfold">', '<meta property="og:title" content="' + html.escape(ttl) + '">', 1)
        t = t.replace('/*DESC*/', html.escape(dsc))
        t = t.replace('/*STATIC*/', seo.static_block(SITE, eds[0]) if SITE else '')
        lds = ''.join('<script type="application/ld+json">' + json.dumps(j, ensure_ascii=False).replace('</', '<\\/') + '</script>\n' for j in (seo.website_ld(SITE) if SITE else []))
        t = t.replace('</head>', lds + '</head>', 1)
        t = t.replace('/*THEME*/', theme).replace('/*PHOTOS*/', photos_blob).replace('/*EDITIONS*/', blob).replace('/*CONFIG*/', cfg_blob).replace('/*ART*/', art).replace('/*SITE*/', site_js).replace('/*WORLD*/', world).replace('/*MAP*/', (SRC / 'map.js').read_text(encoding='utf-8'))
        og_image = (f'<meta property="og:image" content="{SITE}/img/{top_photo["file"]}">\n<meta name="twitter:image" content="{SITE}/img/{top_photo["file"]}">\n') if (SITE and top_photo) else ''
        if SITE:
            t = t.replace('<meta property="og:type"', f'<link rel="canonical" href="{canon[target]}">\n<meta property="og:url" content="{canon[target]}">\n{og_image}<link rel="alternate" type="application/rss+xml" title="Weekfold" href="{SITE}/feed.xml">\n<meta property="og:type"', 1)
        (OUT / target).write_text(t, encoding='utf-8')

    nl = CFG.get('newsletter') or {}
    provider = 'Supabase (emails are sent through Resend)' if nl.get('supabase_url') else PROVIDERS.get(nl.get('provider'), 'our email provider')
    priv = (SRC / 'privacy.html').read_text(encoding='utf-8')
    priv = priv.replace('/*THEME*/', theme).replace('/*TODAY*/', datetime.date.today().strftime('%-d %B %Y')).replace('/*PROVIDER*/', provider).replace('/*CONTACT*/', CFG.get('contact_email', ''))
    (OUT / 'privacy.html').write_text(priv, encoding='utf-8')
    shutil.copy(SRC / 'favicon.svg', OUT / 'favicon.svg')
    for _f in ['favicon.ico','icon-48.png','icon-96.png','icon-180.png','icon-192.png','icon-512.png']:
        shutil.copy(SRC / _f, OUT / _f)
    shutil.copytree(SRC / 'koala', OUT / 'koala', dirs_exist_ok=True)
    shutil.copytree(SRC / 'api', OUT / 'api', dirs_exist_ok=True, ignore=shutil.ignore_patterns('config.php', 'data'))
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
        css = (SRC / 'story.css').read_text(encoding='utf-8').replace('/*THEME*/', theme)
        (OUT / 'story.css').write_text(css, encoding='utf-8')
        flat = {}
        for ed, d, s, di, k in recs:
            flat.setdefault(ed['number'], []).append(s)
        for ed, d, s, di, k in recs:
            lst = flat[ed['number']]; i = lst.index(s)
            page = seo.story_page(SITE, ed, d, s, man, (lst[i - 1] if i > 0 else None, lst[i + 1] if i + 1 < len(lst) else None))
            (OUT / s['path']).mkdir(parents=True, exist_ok=True)
            (OUT / s['path'] / 'index.html').write_text(page, encoding='utf-8')
        for ed in eds:
            (OUT / ed['path']).mkdir(parents=True, exist_ok=True)
            (OUT / ed['path'] / 'index.html').write_text(seo.edition_page(SITE, ed, man), encoding='utf-8')
        (OUT / 'archive').mkdir(exist_ok=True)
        (OUT / 'archive' / 'index.html').write_text(seo.archive_page(SITE, eds), encoding='utf-8')
        print(f'SEO pages: {len(recs)} story pages, {len(eds)} edition pages')
    if SITE:
        (OUT / 'feed.xml').write_text(rss(eds), encoding='utf-8')
        today = datetime.date.today().isoformat()
        (OUT / 'sitemap.xml').write_text(seo.sitemap(SITE, eds, recs, today))
        (OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
    else:
        (OUT / 'robots.txt').write_text('User-agent: *\nAllow: /\n')
        print('Note: config.json has no site_url yet, so feed.xml and sitemap.xml were skipped and email links are relative.')

    # A ready-to-upload copy of the whole site for Hostinger: download it from <site>/weekfold-site.zip
    # and upload it into public_html with Hostinger's File Manager (Extract, replace existing files).
    import zipfile
    zpath = OUT / 'weekfold-site.zip'
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(OUT.rglob('*')):
            if f.is_file() and f != zpath and f.name != '.nojekyll':
                z.write(f, f.relative_to(OUT).as_posix())
    print(f'Hostinger upload: docs/weekfold-site.zip ({zpath.stat().st_size // 1024} KB)')
    print(f'Photos: {len(man)} local copies served from docs/img/')
    for name in ('index.html', 'home.html'):
        print(f'{name}: {(OUT / name).stat().st_size // 1024} KB')
    for e in eds:
        print(f"Edition {e['number']}: {len(e['days'])} days, {sum(1 + len(d['more']) for d in e['days'])} stories")


if __name__ == '__main__':
    main()
