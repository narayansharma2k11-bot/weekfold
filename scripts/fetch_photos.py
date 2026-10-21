#!/usr/bin/env python3
"""Download the free-licensed Wikipedia lead photo for every story, so the site serves its own copies.

Runs on GitHub (see .github/workflows/build.yml), where the internet is open. For each story that names a
Wikipedia article (image.wiki) it:
  1. asks Wikipedia for that article's lead photo,
  2. checks the photo's licence on Wikimedia Commons (public domain, CC0, CC BY, CC BY-SA only),
  3. downloads it, shrinks it to 900 px and saves it as data/photos/<name>.jpg,
  4. records photographer + licence in data/photos/manifest.json.
Photos already downloaded are kept, so each Sunday only the new stories are fetched.
Stories whose article has no usable photo are listed in data/photos/missing.json (the site shows an illustration for them).
"""
import hashlib, html, io, json, pathlib, re, sys, time, urllib.error, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
EDITIONS, PHOTOS = ROOT / 'data' / 'editions', ROOT / 'data' / 'photos'
MANIFEST, MISSING = PHOTOS / 'manifest.json', PHOTOS / 'missing.json'
API = 'https://en.wikipedia.org/w/api.php'
UA = 'WeekfoldBot/1.0 (https://github.com/narayansharma2k11-bot/weekfold; narayansharma2k11@gmail.com)'
MAX_SIDE, QUALITY = 900, 80


def fetch(url, tries=5):
    for n in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (404, 403, 400):
                raise
            time.sleep(2 * (n + 1))
        except Exception:
            time.sleep(2 * (n + 1))
    raise RuntimeError('could not fetch ' + url)


def api(**params):
    q = {'format': 'json', 'formatversion': '2', 'action': 'query', **params}
    return json.loads(fetch(API + '?' + urllib.parse.urlencode(q)))


def ok_license(lic):
    lic = (lic or '').strip().lower()
    if not lic:
        return False
    if re.match(r'^(public domain|pd[ -]|cc0|cc zero|no restrictions|attribution$)', lic):
        return True
    return bool(re.match(r'^cc[ -]by([ -]sa)?[ -][0-9.]+(\s(us|au|nz|ca|uk|in|ie|de|nl|fr|es|it|igo))?$', lic))


def strip_html(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s or ''))).strip()


def titles_in_use():
    seen = []
    for p in sorted(EDITIONS.glob('*.json')):
        ed = json.loads(p.read_text(encoding='utf-8'))
        for d in ed.get('days') or []:
            for s in [d.get('lead')] + (d.get('more') or []):
                w = ((s or {}).get('image') or {}).get('wiki')
                if w:
                    t = w.strip().replace(' ', '_')
                    if t not in seen:
                        seen.append(t)
    return seen


def lookup(title):
    """Return (thumbnail_url, commons_file_name, credit, license) for the article's lead photo, or None."""
    j = api(redirects='1', prop='pageimages', piprop='thumbnail|name', pithumbsize=str(MAX_SIDE + 100), pilicense='free', titles=title.replace('_', ' '))
    pages = (j.get('query') or {}).get('pages') or []
    if not pages or not pages[0].get('thumbnail') or not pages[0].get('pageimage'):
        return None
    pg = pages[0]
    f = pg['pageimage']
    k = api(prop='imageinfo', iiprop='extmetadata', iiextmetadatafilter='Artist|LicenseShortName', titles='File:' + f)
    info = ((k.get('query') or {}).get('pages') or [{}])[0].get('imageinfo') or [{}]
    em = info[0].get('extmetadata') or {}
    credit = strip_html((em.get('Artist') or {}).get('value'))
    lic = (em.get('LicenseShortName') or {}).get('value') or ''
    if not ok_license(lic):
        return ('licence', f, credit, lic)
    return (pg['thumbnail']['source'], f, credit[:140], lic)


def save_jpeg(raw, dest):
    from PIL import Image
    im = Image.open(io.BytesIO(raw))
    im.load()
    if im.mode in ('RGBA', 'LA', 'P'):
        bg = Image.new('RGB', im.size, (255, 255, 255))
        im = im.convert('RGBA')
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert('RGB')
    im.thumbnail((MAX_SIDE, MAX_SIDE))
    im.save(dest, 'JPEG', quality=QUALITY, optimize=True, progressive=True)
    return im.size


def main():
    PHOTOS.mkdir(parents=True, exist_ok=True)
    man = json.loads(MANIFEST.read_text(encoding='utf-8')) if MANIFEST.exists() else {}
    missing = {}
    titles = titles_in_use()
    todo = [t for t in titles if not (t in man and (PHOTOS / man[t]['file']).exists())]
    print(f'{len(titles)} story photos named, {len(titles) - len(todo)} already downloaded, {len(todo)} to fetch.')
    for t in todo:
        try:
            res = lookup(t)
            if not res:
                missing[t] = 'article has no free lead photo'
                print('  MISSING', t, '- no free lead photo'); continue
            url, f, credit, lic = res
            if url == 'licence':
                missing[t] = f'licence not allowed: {lic or "unknown"}'
                print('  MISSING', t, '- licence', lic or 'unknown'); continue
            name = re.sub(r'[^A-Za-z0-9]+', '-', t).strip('-')[:48] + '-' + hashlib.sha1(t.encode()).hexdigest()[:6] + '.jpg'
            w, h = save_jpeg(fetch(url), PHOTOS / name)
            man[t] = {'file': name, 'credit': credit, 'license': lic, 'page': 'https://commons.wikimedia.org/wiki/File:' + urllib.parse.quote(f.replace(' ', '_')), 'w': w, 'h': h}
            print('  ok     ', t, '->', name, f'({w}x{h}, {(PHOTOS / name).stat().st_size // 1024} KB, {lic})')
        except Exception as e:  # never fail the build because of one photo
            missing[t] = 'download failed: ' + str(e)[:120]
            print('  FAILED ', t, '-', e)
        time.sleep(0.4)
    MANIFEST.write_text(json.dumps(man, ensure_ascii=False, indent=1, sort_keys=True), encoding='utf-8')
    MISSING.write_text(json.dumps(missing, ensure_ascii=False, indent=1, sort_keys=True), encoding='utf-8')
    have = sum(1 for t in titles if t in man)
    print(f'Done: {have}/{len(titles)} stories have a local photo; {len(missing)} will show an illustration.')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('fetch_photos stopped early:', e)  # the build still runs with whatever photos exist
