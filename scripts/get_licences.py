#!/usr/bin/env python3
"""Look up the real author + licence of each Weekfold photo on Wikipedia/Wikimedia Commons.
Reads titles (one per line) from ~/Pictures/licence_titles.txt and writes ~/Pictures/weekfold-photos/licences.json. Standard library only."""
import json, os, re, time, urllib.parse, urllib.request
OUT = os.path.expanduser('~/Pictures/weekfold-photos'); os.makedirs(OUT, exist_ok=True)
UA = 'WeekfoldPhotoFetch/1.0 (https://weekfold.in)'
TITLES = [t.strip() for t in open(os.path.expanduser('~/Pictures/licence_titles.txt'), encoding='utf-8') if t.strip()]
def api(**p):
    p['format'] = 'json'
    url = 'https://en.wikipedia.org/w/api.php?' + urllib.parse.urlencode(p)
    for n in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=40) as r: return json.loads(r.read())
        except Exception as e:
            err = e; time.sleep(2 * (n + 1))
    raise err
clean = lambda s: re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', s or '')).strip()
res = {}; fail = []
for t in TITLES:
    try:
        q = api(action='query', titles=t.replace('_', ' '), prop='pageimages', piprop='name', redirects=1)
        fname = next(iter(q['query']['pages'].values())).get('pageimage')
        if not fname: fail.append((t, 'no lead image')); print('SKIP', t); continue
        i = api(action='query', titles='File:' + fname, prop='imageinfo', iiprop='extmetadata')
        md = next(iter(i['query']['pages'].values()))['imageinfo'][0]['extmetadata']
        lic = clean(md.get('LicenseShortName', {}).get('value'))
        who = clean(md.get('Artist', {}).get('value'))[:90]
        res[t] = {'source_file': fname, 'license': lic, 'artist': who}
        print('ok  ', t, '|', lic or '?', '|', who or '?'); time.sleep(0.25)
    except Exception as e:
        fail.append((t, str(e))); print('FAIL', t, e)
json.dump(res, open(os.path.join(OUT, 'licences.json'), 'w'), ensure_ascii=False, indent=1)
print('\nDone: %d looked up, %d failed. Tell Claude "done".' % (len(res), len(fail)))
