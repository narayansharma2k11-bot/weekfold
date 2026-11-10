"""Static, crawlable pages for Weekfold: one page per story, one per edition, an archive, JSON-LD and the sitemap."""
import datetime, html, json, re, unicodedata

E = html.escape


def slugify(s, n=70):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r"['’]", '', s)
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    if len(s) > n:
        s = s[:n].rsplit('-', 1)[0]
    return s or 'story'


def assign(eds):
    """Give every story a stable path like 2026/45/paraguay-senate-removes-president/ ; returns list of flat records."""
    recs = []
    for ed in eds:
        year = ed['days'][0]['date'][:4]
        ed['path'] = f"{year}/{ed['number']}/"
        used = set()
        n = 0
        for di, d in enumerate(ed['days']):
            for k, s in enumerate([d['lead']] + d['more']):
                slug = slugify(s['headline']); base = slug; i = 2
                while slug in used:
                    slug = f'{base}-{i}'; i += 1
                used.add(slug)
                s['path'] = f"{ed['path']}{slug}/"; s['k'] = k; s['date'] = d['date']
                recs.append((ed, d, s, di, k))
    return recs


def day_long(iso):
    return datetime.date.fromisoformat(iso).strftime('%A %-d %B %Y')


def photo_for(story, man):
    t = ((story.get('image') or {}).get('wiki') or '').replace(' ', '_')
    return man.get(t)


def credit_html(p):
    if not p:
        return ''
    who = p.get('artist') or p.get('credit') or 'Wikimedia Commons'
    lic = p.get('license') or ''
    if lic == 'Free licence': lic = ''
    link = p.get('file_page') or p.get('page') or ''
    bits = [E(who)] + ([E(lic)] if lic else [])
    s = 'Photo: ' + ' · '.join(bits)
    if link:
        s += f' · <a href="{E(link)}" rel="noopener nofollow">source</a>'
    return s


def head(site, title, desc, path, og_img=None, jsonld=None, typ='article'):
    url = f'{site}/{path}'
    img = f'<meta property="og:image" content="{E(og_img)}">\n<meta name="twitter:image" content="{E(og_img)}">\n' if og_img else ''
    ld = ''.join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False).replace("</", "<\\/")}</script>\n' for j in (jsonld or []))
    return f'''<!doctype html>
<html lang="en">
<head>
<script>try{{var t=localStorage.getItem('wf-theme');if(t==='dark'||(!t&&window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches))document.documentElement.setAttribute('data-theme','dark')}}catch(e){{}}</script>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{E(url)}">
<meta name="theme-color" content="#F7F7F7">
<link rel="icon" href="/favicon.ico?v=3" sizes="48x48">
<link rel="icon" type="image/svg+xml" href="/favicon.svg?v=3">
<link rel="apple-touch-icon" href="/icon-180.png?v=3">
<meta property="og:type" content="{typ}">
<meta property="og:site_name" content="Weekfold">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{E(url)}">
{img}<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="Weekfold" href="{site}/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;0,900;1,400&family=Roboto:wght@300;400;500;700&display=swap">
<link rel="stylesheet" href="/story.css">
{ld}</head>
<body>
'''


LOGO = ('<svg viewBox="0 0 80 80" aria-hidden="true" fill="none" stroke="#000"><rect x="12" y="10" width="54" height="54" stroke-width="1.6" transform="rotate(-6 39 37)"/>'
        '<rect x="15" y="14" width="54" height="54" stroke-width="1.6" transform="rotate(4 42 41)"/><path d="M20 28L28 54L40 26L52 54L60 28" stroke-width="3.4" stroke-linejoin="round"/>'
        '<path d="M20 58h40" stroke-width="1.6" stroke-dasharray="3 3"/></svg>')


def header():
    return f'''<header class="top"><div class="in">
<a class="logo" href="/" aria-label="Weekfold, home">{LOGO}Weekfold<img class="kl-hang" src="/koala/hang.webp" alt="" width="308" height="301" aria-hidden="true"></a>
<nav class="pnav" aria-label="Main"><a href="/home.html#current">This week</a><a href="/archive/">All editions</a><a href="/home.html#crossword">Games</a><a href="/index.html#about">About</a></nav>
</div></header>
'''


def footer():
    return '''<footer class="sitefoot"><div class="wrap">
<div class="legal"><span>© Weekfold · New edition every Sunday · <a href="mailto:weekfoldsupport@gmail.com">weekfoldsupport@gmail.com</a></span>
<span class="made">Made by Narayan Sharma</span>
<p class="credits">Weekfold uses only public-domain or Creative Commons images from Wikimedia, credited beneath each picture. Every story names its sources. <a href="/privacy.html">Privacy</a> · <a href="/feed.xml">RSS</a></p></div>
</div></footer>
</body></html>
'''


def org(site):
    return {'@context': 'https://schema.org', '@type': 'NewsMediaOrganization', 'name': 'Weekfold', 'url': site + '/', 'logo': {'@type': 'ImageObject', 'url': site + '/icon-512.png'},
            'description': "A free weekly world news edition: the stories that mattered, one page for every day, every story sourced.", 'email': 'weekfoldsupport@gmail.com'}


def story_page(site, ed, d, s, man, nav):
    p = photo_for(s, man)
    img_url = f"{site}/img/{p['file']}" if p else f'{site}/icon-512.png'
    desc = s['dek']
    title = f"{s['headline']} | Weekfold {ed['number']}"
    pub = d['date'] + 'T00:00:00+05:30'
    ld = [org(site), {
        '@context': 'https://schema.org', '@type': 'NewsArticle', 'headline': s['headline'][:110], 'description': desc,
        'datePublished': pub, 'dateModified': pub, 'inLanguage': 'en', 'articleSection': s['category'],
        'image': [img_url], 'mainEntityOfPage': {'@type': 'WebPage', '@id': f"{site}/{s['path']}"},
        'author': {'@type': 'Organization', 'name': 'Weekfold', 'url': site + '/'},
        'publisher': {'@type': 'Organization', 'name': 'Weekfold', 'logo': {'@type': 'ImageObject', 'url': site + '/icon-512.png'}},
        'isPartOf': {'@type': 'CreativeWork', 'name': f"Weekfold Edition {ed['number']}", 'url': f"{site}/{ed['path']}"},
        'citation': [{'@type': 'WebPage', 'name': x['name'], 'url': x['url']} for x in s.get('sources', [])],
    }, {
        '@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Weekfold', 'item': site + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': f"Edition {ed['number']}", 'item': f"{site}/{ed['path']}"},
            {'@type': 'ListItem', 'position': 3, 'name': s['headline'], 'item': f"{site}/{s['path']}"}]}]
    h = head(site, title, desc, s['path'], img_url if p else None, ld)
    fig = ''
    if p:
        fig = f'<figure class="pic"><img src="/img/{E(p["file"])}" alt="{E(s["headline"])}" width="1200" height="800" fetchpriority="high"><figcaption>{credit_html(p)}</figcaption></figure>'
    body = ''.join(f'<p>{E(x)}</p>' for x in s['body'])
    why = f'<aside class="why"><b>Why it matters</b><p>{E(s["why"])}</p></aside>' if s.get('why') else ''
    srcs = ''.join(f'<li><a href="{E(x["url"])}" rel="noopener nofollow">{E(x["name"])}</a></li>' for x in s['sources'])
    corr = ''
    if s.get('corrections'):
        corr = '<aside class="why"><b>Corrections</b>' + ''.join(f'<p>{E(c)}</p>' for c in s['corrections']) + '</aside>'
    prev, nxt = nav
    pn = ''
    if prev: pn += f'<a class="pn" href="/{prev["path"]}"><small>Earlier</small>{E(prev["headline"])}</a>'
    if nxt: pn += f'<a class="pn r" href="/{nxt["path"]}"><small>Later</small>{E(nxt["headline"])}</a>'
    return (h + header() + f'''<main class="story wrap">
<p class="crumb"><a href="/">Weekfold</a> › <a href="/{ed["path"]}">Edition {E(ed["number"])}</a> › {E(s["category"])}</p>
<p class="kick">{E(s["category"])} · {E(day_long(d["date"]))}</p>
<h1>{E(s["headline"])}</h1>
<p class="dek">{E(s["dek"])}</p>
{fig}
<div class="txt">{body}</div>
{why}{corr}
<section class="srcs"><h2>Sources</h2><ul>{srcs}</ul><p class="note">Weekfold summarises these reports in its own words. Read the originals for full detail.</p></section>
<section class="cta"><p><b>Get the whole week in one read.</b> A free edition every Sunday.</p><a class="btn" href="/#subscribe">Subscribe free</a> <a class="btn alt" href="/{ed["path"]}">Edition {E(ed["number"])} · {E(ed["range"])}</a></section>
<nav class="pns">{pn}</nav>
</main>
''' + footer())


def edition_page(site, ed, man):
    f = ed['days'][ed.get('featured', 0)]['lead']
    title = f"Weekfold {ed['number']}: {f['headline']} | Weekly world news"
    desc = f"Edition {ed['number']} ({ed['rangeLong']}): " + '; '.join(d['lead']['headline'] for d in ed['days'][:3]) + ' and more. One page for every day, every story sourced.'
    items, rows = [], []
    pos = 0
    for d in ed['days']:
        rows.append(f'<section class="dayblk"><h2>{E(day_long(d["date"]))}</h2>')
        for s in [d['lead']] + d['more']:
            pos += 1
            items.append({'@type': 'ListItem', 'position': pos, 'url': f"{site}/{s['path']}", 'name': s['headline']})
            p = photo_for(s, man)
            th = f'<img src="/img/{E(p["file"])}" alt="" loading="lazy" width="160" height="107">' if p else ''
            rows.append(f'<article class="li{" lead" if s["k"] == 0 else ""}"><a class="th" href="/{s["path"]}" tabindex="-1" aria-hidden="true">{th}</a><div><p class="kick">{E(s["category"])}</p><h3><a href="/{s["path"]}">{E(s["headline"])}</a></h3><p>{E(s["dek"])}</p></div></article>')
        rows.append('</section>')
    ld = [org(site), {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': f"Weekfold Edition {ed['number']}", 'description': desc, 'url': f"{site}/{ed['path']}",
                      'datePublished': ed['days'][-1]['date'], 'mainEntity': {'@type': 'ItemList', 'itemListElement': items}}]
    return (head(site, title, desc, ed['path'], None, ld, 'website') + header() + f'''<main class="story wrap">
<p class="crumb"><a href="/">Weekfold</a> › <a href="/archive/">All editions</a> › Edition {E(ed["number"])}</p>
<p class="kick">Edition {E(ed["number"])} · {E(ed["rangeLong"])}</p>
<h1>The week in the world: {E(f["headline"])}</h1>
<p class="dek">Every story from {E(ed["rangeLong"])}, one page for every day. <a href="/home.html#current">Read it as a book →</a></p>
{''.join(rows)}
</main>
''' + footer())


def archive_page(site, eds):
    title = 'All Weekfold editions | Weekly world news archive'
    desc = 'Every weekly edition of Weekfold, newest first: the biggest world news story of each week and links to every day.'
    rows = ''.join(f'<li><a href="/{ed["path"]}"><b>Edition {E(ed["number"])}</b> · {E(ed["rangeLong"])}</a><span>{E(ed["days"][ed.get("featured", 0)]["lead"]["headline"])}</span></li>' for ed in eds)
    ld = [org(site)]
    return (head(site, title, desc, 'archive/', None, ld, 'website') + header() + f'''<main class="story wrap"><p class="crumb"><a href="/">Weekfold</a> › All editions</p>
<h1>All editions</h1><p class="dek">A new edition every Sunday. Newest first.</p><ul class="arch">{rows}</ul></main>
''' + footer())


def static_block(site, ed):
    """Plain-HTML list of the current edition's stories, in the page source for search engines and no-JS readers."""
    out = [f'<h2>This week\'s stories · Edition {E(ed["number"])}</h2><p class="sn-sub">{E(ed["rangeLong"])} · <a href="/{ed["path"]}">all stories on one page</a> · <a href="/archive/">all editions</a></p><div class="sn-grid">']
    for d in ed['days']:
        out.append(f'<div><h3>{E(day_long(d["date"]))}</h3><ul>' + ''.join(f'<li><a href="/{s["path"]}">{E(s["headline"])}</a></li>' for s in [d['lead']] + d['more']) + '</ul></div>')
    out.append('</div>')
    return ''.join(out)


def website_ld(site):
    return [org(site), {'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'Weekfold', 'url': site + '/', 'inLanguage': 'en'}]


def sitemap(site, eds, recs, today):
    u = [('', today, 'weekly', '1.0'), ('home.html', today, 'weekly', '0.9'), ('archive/', today, 'weekly', '0.7'), ('privacy.html', today, 'yearly', '0.2')]
    for ed in eds:
        u.append((ed['path'], ed['days'][-1]['date'], 'monthly', '0.8'))
    for ed, d, s, di, k in recs:
        u.append((s['path'], d['date'], 'yearly', '0.7' if k == 0 else '0.6'))
    body = ''.join(f'<url><loc>{site}/{p}</loc><lastmod>{lm}</lastmod><changefreq>{cf}</changefreq><priority>{pr}</priority></url>' for p, lm, cf, pr in u)
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + body + '</urlset>\n'
