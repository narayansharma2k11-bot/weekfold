#!/usr/bin/env python3
"""Download Wikipedia's lead photo for the hand-supplied Weekfold photos so Claude can check they match. Writes ~/Pictures/weekfold-photos/verify/*.jpg"""
import json, os, re, time, urllib.parse, urllib.request
OUT = os.path.expanduser('~/Pictures/weekfold-photos/verify'); os.makedirs(OUT, exist_ok=True)
UA = 'WeekfoldPhotoFetch/1.0 (https://weekfold.in)'
TITLES = [t.strip() for t in open(os.path.expanduser('~/Pictures/verify_titles.txt'), encoding='utf-8') if t.strip()]
def get(url, binary=False):
    for n in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=50) as r:
                d = r.read(); return d if binary else json.loads(d)
        except Exception as e: err = e; time.sleep(2 * (n + 1))
    raise err
for t in TITLES:
    try:
        q = get('https://en.wikipedia.org/w/api.php?' + urllib.parse.urlencode(dict(action='query', titles=t.replace('_', ' '), prop='pageimages', piprop='thumbnail', pithumbsize=800, redirects=1, format='json')))
        th = (next(iter(q['query']['pages'].values())).get('thumbnail') or {}).get('source')
        if not th: print('no image', t); continue
        open(os.path.join(OUT, re.sub(r'[^A-Za-z0-9_]+', '_', t) + '.jpg'), 'wb').write(get(th, True)); print('ok', t); time.sleep(0.3)
    except Exception as e: print('FAIL', t, e)
print('Done. Tell Claude "done".')
