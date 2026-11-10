#!/usr/bin/env python3
"""Download the free-licensed Wikipedia lead photo for each Weekfold story title.
Reads titles from ~/Pictures/titles.txt, wipes last week's downloads first, then saves JPG files + meta.json into ~/Pictures/weekfold-photos. Uses only the Python standard library."""
import json, os, re, time, urllib.parse, urllib.request, urllib.error
OUT = os.path.expanduser('~/Pictures/weekfold-photos'); os.makedirs(OUT, exist_ok=True)
UA = 'WeekfoldPhotoFetch/1.0 (https://weekfold.in)'
TL = os.path.expanduser('~/Pictures/titles.txt')
TITLES = open(TL, encoding='utf-8').read().split() if os.path.exists(TL) else []
if not TITLES: raise SystemExit('No titles: put Wikipedia titles (one per line) in ' + TL)
# start clean: delete last week's downloads so no old photos linger
for _f in os.listdir(OUT):
    if _f.endswith(('.jpg', '.json')): os.remove(os.path.join(OUT, _f))
OK = re.compile(r'^(public domain.*|pd[ -].*|cc0.*|cc[ -]by([ -]sa)?[ -]\d(\.\d)?.*)$', re.I)
NO = re.compile(r'\b(nc|nd)\b|non-?commercial|no ?derivs', re.I)
def get(url, binary=False):
    last = None
    for n in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60) as r:
                d = r.read(); return d if binary else json.loads(d)
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (404, 400): break
            time.sleep(3 * (n + 1))
        except Exception as e:
            last = e; time.sleep(2)
    raise last
def api(host, **p):
    p['format'] = 'json'; return get('https://%s/w/api.php?%s' % (host, urllib.parse.urlencode(p)))
meta = {}; bad = []
for t in TITLES:
    try:
        q = api('en.wikipedia.org', action='query', titles=t.replace('_', ' '), prop='pageimages', piprop='thumbnail|name', pithumbsize=1200, redirects=1)
        page = next(iter(q['query']['pages'].values()))
        th, fname = (page.get('thumbnail') or {}).get('source'), page.get('pageimage')
        if not th: bad.append((t, 'no lead photo')); print('SKIP', t, '(no lead photo)'); continue
        lic, who = '', ''
        try:
            info = api('commons.wikimedia.org', action='query', titles='File:' + fname, prop='imageinfo', iiprop='extmetadata')
            md = next(iter(info['query']['pages'].values()))['imageinfo'][0]['extmetadata']
            lic = re.sub('<[^>]+>', '', md.get('LicenseShortName', {}).get('value', '')).strip()
            who = re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', md.get('Artist', {}).get('value', ''))).strip()[:80]
        except Exception: pass
        if lic and (NO.search(lic) or not OK.match(lic)): bad.append((t, 'licence ' + lic)); print('SKIP', t, '- licence', lic); continue
        data = get(th, True); fn = re.sub(r'[^A-Za-z0-9_]+', '_', t).strip('_') + '.jpg'
        open(os.path.join(OUT, fn), 'wb').write(data)
        meta[t] = {'file': fn, 'source_file': fname, 'license': lic, 'artist': who}
        print('ok  ', t, '|', lic or 'licence unknown', '|', len(data) // 1024, 'KB'); time.sleep(0.4)
    except Exception as e:
        bad.append((t, str(e))); print('FAIL', t, e)
json.dump({'photos': meta, 'skipped': bad}, open(os.path.join(OUT, 'meta.json'), 'w'), ensure_ascii=False, indent=1)
print('\nDone: %d downloaded, %d skipped. Tell Claude "done".' % (len(meta), len(bad)))
