"""Weekfold Instagram posts (1080x1350). Run: python3 promo/instagram/gen.py  -> promo/instagram/out/*.png
Ads use screenshots in promo/instagram/shots/ (re-take them with the site running on localhost:8765) and this week's photos."""
import json, pathlib, html
from playwright.sync_api import sync_playwright
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parent.parent
K = (ROOT / 'src' / 'koala').as_uri(); SH = (HERE / 'shots').as_uri()
IMG = (ROOT / 'docs' / 'img').as_uri()
man = json.loads((ROOT / 'data' / 'photos' / 'manifest.json').read_text())
_n = max(int(f.stem) for f in (ROOT / 'data' / 'editions').glob('*.json'))   # newest edition
ed = json.loads((ROOT / 'data' / 'editions' / f'{_n}.json').read_text())
def photo(t):
    m = man.get(t.replace(' ', '_')); return f"{IMG}/{pathlib.Path(m['file']).stem}.webp"
def story(di, k): d = ed['days'][di]; return ([d['lead']] + d['more'])[k]
LOGO = '<svg viewBox="0 0 80 80" fill="none" stroke="currentColor"><rect x="12" y="10" width="54" height="54" stroke-width="2" transform="rotate(-6 39 37)"/><rect x="15" y="14" width="54" height="54" stroke-width="2" transform="rotate(4 42 41)"/><path d="M20 28L28 54L40 26L52 54L60 28" stroke-width="4" stroke-linejoin="round"/><path d="M20 58h40" stroke-width="2" stroke-dasharray="3 3"/></svg>'
TH = {'cream': ('#f7f2e8', '#0a0a0a', '#8c1d18'), 'navy': ('#10224a', '#ffffff', '#f2c94c'), 'gold': ('#e9d98a', '#0a0a0a', '#8c1d18')}
CSS = '''*{box-sizing:border-box;margin:0}body{background:#888;font-family:'Roboto',sans-serif}
.post{width:1080px;height:1350px;position:relative;overflow:hidden;padding:64px 76px;margin-bottom:20px}
.top{display:flex;align-items:center;gap:14px;font:900 42px 'Playfair Display',serif;letter-spacing:-.01em}.top svg{width:52px;height:52px}.top .r{margin-left:auto;font:700 24px Roboto;letter-spacing:.14em;text-transform:uppercase}
.k{margin-top:52px;font:700 27px Roboto;letter-spacing:.18em;text-transform:uppercase}
h1{font:900 98px/1.03 'Playfair Display',serif;letter-spacing:-.025em;margin-top:18px;max-width:930px}
.sub{font:400 36px/1.4 Roboto;margin-top:26px;max-width:860px;opacity:.92}
.foot{position:absolute;z-index:5;left:0;right:0;bottom:0;height:86px;display:flex;align-items:center;justify-content:space-between;padding:0 76px;font:700 29px Roboto;letter-spacing:.08em;border-top:3px solid currentColor}
.ph{position:absolute;bottom:86px;width:400px;height:520px;border:7px solid #000;border-bottom:0;border-radius:46px 46px 0 0;box-shadow:12px 0 0 #000;overflow:hidden;background:#fff}
.ph img{display:block;width:100%;height:100%;object-fit:cover;object-position:top}
.kl{position:absolute;z-index:3}
.pol{position:absolute;border:6px solid #000;box-shadow:8px 8px 0 #000;background:#fff;overflow:hidden}.pol img{width:100%;height:100%;object-fit:cover;display:block}
.week{position:absolute;left:76px;right:76px;bottom:128px;display:grid;grid-template-columns:repeat(7,1fr);gap:10px}
.wd{background:#fff;border:3px solid #000;box-shadow:5px 5px 0 #000;color:#000}.wd b{display:block;font:700 22px Roboto;letter-spacing:.1em;text-transform:uppercase;padding:8px 0 6px;text-align:center;background:#10224a;color:#fff}.wd div{height:170px;background-size:cover;background-position:center}.wd i{display:block;font:700 15px/1.2 'Playfair Display',serif;padding:8px 8px 10px;height:84px;overflow:hidden;font-style:normal}
.ph1{position:absolute;left:76px;right:76px;top:300px;height:600px;border:7px solid #000;box-shadow:14px 14px 0 #000;overflow:hidden}.ph1 img{width:100%;height:100%;object-fit:cover;display:block}
.pill{display:inline-block;font:700 26px Roboto;letter-spacing:.14em;text-transform:uppercase;padding:10px 18px;border:3px solid #000}
.nh{position:absolute;left:76px;right:76px;top:760px}.nh h2{font:900 82px/1.04 'Playfair Display',serif;letter-spacing:-.02em;margin-top:16px}.nh p{font:400 33px/1.4 Roboto;margin-top:18px;opacity:.92}.nh small{display:block;font:500 25px Roboto;letter-spacing:.04em;margin-top:18px;opacity:.7}'''

def ad(i, th, kick, h, sub, body):
    bg, fg, acc = TH[th]; h = h.replace('<em>', f'<em style="color:{acc};font-style:italic">')
    return f'''<div class="post" id="a{i:02d}" style="background:{bg};color:{fg}"><div class="top">{LOGO}<span>Weekfold</span></div>
<div class="k" style="color:{acc}">{kick}</div><h1>{h}</h1><div class="sub">{sub}</div>{body}
<div class="foot"><span>weekfold.in</span><span style="color:{acc}">FREE · EVERY SUNDAY</span></div></div>'''
def phone(f, right=70, w=400, h=520): return f'<div class="ph" style="right:{right}px;width:{w}px;height:{h}px"><img src="{SH}/{f}.png"></div>'
def koala(n, h, left=None, right=None, bottom=96, rot=0):
    pos = f'left:{left}px;' if left is not None else f'right:{right}px;'
    return f'<img class="kl" src="{K}/{n}.webp" style="{pos}bottom:{bottom}px;height:{h}px;transform:rotate({rot}deg)">'
def collage(items):
    return ''.join(f'<div class="pol" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;transform:rotate({r}deg)"><img src="{photo(t)}"></div>' for t, x, y, w, h, r in items)

A = []
A.append(ad(1, 'cream', 'Hello, world', 'The world’s week, <em>folded</em> into one free edition.', 'A free news edition that lands every Sunday. One page for every day.', phone('landing', right=80) + koala('wave', 420, left=40)))
A.append(ad(2, 'navy', 'Sound familiar?', 'Too much news. <em>Too little time.</em>', 'We read the week so you don’t have to scroll it.',
    collage([('United_States_Capitol', 400, 640, 300, 220, 5), ('Oil_tanker', 690, 700, 300, 220, -6), ('Bank_of_England', 520, 840, 300, 220, -3), ('Heat_wave', 790, 880, 240, 190, 7), ('Kyiv', 380, 880, 230, 180, -8)]) + koala('worry', 400, left=50)))
A.append(ad(3, 'cream', 'How it works', 'One page for <em>every day</em> of the week.', 'Monday to Sunday, the stories that still mattered by the end of the week.', phone('days', right=80) + koala('point', 420, left=40)))
A.append(ad(4, 'gold', 'Our rule', 'Every story <em>names its sources.</em>', 'At least two independent outlets behind every story. Always linked.', phone('story_src', right=80) + koala('magnify', 410, left=40)))
A.append(ad(5, 'navy', 'The best part', 'Free. No ads. <em>No paywall.</em>', 'Just the week’s news, written in plain English.', phone('home', right=80) + koala('thumb', 420, left=40)))
wk = ''.join(f'<div class="wd"><b>{d["date"][8:]} Nov</b><div style="background-image:url({photo(d["lead"]["image"]["wiki"])})"></div><i>{html.escape(d["lead"]["headline"][:58])}</i></div>' for d in ed['days'])
A.append(ad(6, 'cream', 'Mark your calendar', 'A new edition <em>every Sunday.</em>', 'Seven days, seven leads, one read. Straight to your inbox.', f'<div class="week">{wk}</div>' + koala('sun', 360, right=60, bottom=420, rot=0)))
A.append(ad(7, 'gold', 'Games', 'Two games. <em>Every day.</em>', 'A fresh mini crossword and Weekfold Word, right inside the site.', phone('crossword', right=60, w=380, h=500) + phone('word', right=480, w=380, h=500) + koala('mug', 380, left=20, bottom=96)))
A.append(ad(8, 'navy', 'World news', 'Five minutes to <em>catch up</em> on the planet.', 'Politics, science, climate, sport, culture and more, all in one place.',
    collage([('Greenland_ice_sheet', 430, 700, 280, 210, -5), ('Pedro_Alliana', 700, 730, 300, 220, 5), ('Beauden_Barrett', 560, 890, 270, 200, -3), ('Joshua_Kutryk', 840, 930, 190, 160, 8)]) + koala('globe', 420, left=40)))
A.append(ad(9, 'cream', 'Our promise', 'No spin. <em>Just the facts.</em>', 'Plain-English summaries of what actually happened, with the sources one tap away.', phone('story', right=80) + koala('shock', 400, left=50)))
A.append(ad(10, 'navy', 'Ready?', 'Get Weekfold <em>every Sunday.</em>', 'Free forever. Join at weekfold.in (link in bio).', phone('landing', right=80) + koala('mega', 420, left=40)))

N = [  # THE WEEKLY TASK EDITS THIS LIST: (day index 0-6, story index within day, theme cream/navy/gold, koala pose or None). Pick the 5 biggest stories; no koala on deaths/violence.
 (1, 0, 'cream', 'point'), (3, 0, 'navy', None), (3, 1, 'gold', 'magnify'), (5, 0, 'navy', None), (4, 1, 'cream', 'worry')]
def news(i, spec):
    di, k, th, ko = spec; s = story(di, k); bg, fg, acc = TH[th]; d = ed['days'][di]['date']
    import datetime; day = datetime.date.fromisoformat(d).strftime('%A %-d %B')
    kl = f'<img class="kl" src="{K}/{ko}.webp" style="right:34px;top:470px;height:250px">' if ko else ''
    return f'''<div class="post" id="n{i:02d}" style="background:{bg};color:{fg}"><div class="top">{LOGO}<span>Weekfold</span><span class="r" style="color:{acc}">The week · {i}/5</span></div>
<div class="ph1" style="top:160px;height:500px"><img src="{photo(s['image']['wiki'])}"></div>
<div class="nh" style="top:700px"><span class="pill" style="background:{acc if th!='navy' else '#f2c94c'};color:{'#fff' if th!='navy' else '#10224a'};border-color:#000">{s['category']}</span><span style="font:500 25px Roboto;margin-left:16px;opacity:.75">{day}</span>
<h2 style="font-size:{72 if len(s['headline'])>62 else 80}px">{html.escape(s['headline'])}</h2>
<p style="font-size:31px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden">{html.escape(s['dek'])}</p></div>
{kl}<div class="foot"><span>Source: {html.escape(s['sources'][0]['name'].split(' (')[0])}</span><span style="color:{acc}">FULL STORY · WEEKFOLD.IN</span></div></div>'''
posts = A + [news(i + 1, s) for i, s in enumerate(N)]
page = '<html><head><meta charset="utf-8"><style>' + CSS + '</style></head><body>' + ''.join(posts) + '</body></html>'
(HERE / 'posts.html').write_text(page, encoding='utf-8')
out = HERE / 'out'; out.mkdir(exist_ok=True)
for f in out.glob('*.png'): f.unlink()
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1350})
    pg.goto((HERE / 'posts.html').as_uri()); pg.wait_for_timeout(2000)
    for i in range(10): pg.locator(f'#a{i+1:02d}').screenshot(path=str(out / f'weekfold-ad-{i+1:02d}.png'))
    for i in range(5): pg.locator(f'#n{i+1:02d}').screenshot(path=str(out / f'weekfold-news-{i+1:02d}.png'))
print(len(posts), 'posts ->', out)
