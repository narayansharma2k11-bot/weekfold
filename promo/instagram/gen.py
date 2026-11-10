"""Weekfold Instagram posts (1080x1350). Run: python3 promo/instagram/gen.py  -> promo/instagram/out/*.png
Ads use screenshots in promo/instagram/shots/ (re-take them with the site running on localhost:8765) and this week's photos."""
import json, pathlib, html
from playwright.sync_api import sync_playwright
HERE = pathlib.Path(__file__).resolve().parent; ROOT = HERE.parent.parent
from PIL import Image, ImageFilter
_hi = HERE / 'koala_hi'; _hi.mkdir(exist_ok=True)
import numpy as np
from scipy import ndimage as ndi
def _hires(p):
    im = Image.open(p).convert('RGBA'); a = np.array(im).astype(float)
    a[..., :3] *= a[..., 3:4] / 255                          # premultiply so transparent white doesn't bleed
    im = Image.fromarray(a.astype('uint8'), 'RGBA').resize((im.width * 3, im.height * 3), Image.LANCZOS)
    a = np.array(im).astype(float); al = a[..., 3:4].clip(1, 255); a[..., :3] = (a[..., :3] * 255 / al).clip(0, 255)
    a = a.astype('uint8'); lum = a[..., :3].mean(2); opaque = a[..., 3] > 30
    dark = opaque & (lum < 80)
    # peel any light pixels outside the black outline (flood in from transparency through non-dark pixels, up to 10px)
    reach = ~opaque
    for _ in range(10): reach = ndi.binary_dilation(reach) & ~dark | reach
    a[reach & ~dark, 3] = 0
    for _ in range(2):                                         # remove remaining light edge pixels
        t = a[..., 3] < 30; e = ndi.binary_dilation(t) & ~t & (a[..., :3].mean(2) > 60); a[e, 3] = 0
    edge = (a[..., 3] > 0) & (a[..., 3] < 255); a[edge, :3] = np.minimum(a[edge, :3], 40)   # dark fringe, never white
    a[..., 3] = np.where(a[..., 3] < 30, 0, a[..., 3])
    return Image.fromarray(a, 'RGBA')
for _p in (ROOT / 'src' / 'koala').glob('*.webp'):
    _hires(_p).save(_hi / (_p.stem + '.png'))
K = _hi.as_uri(); SH = (HERE / 'shots').as_uri()
IMG = (ROOT / 'docs' / 'img').as_uri()
man = json.loads((ROOT / 'data' / 'photos' / 'manifest.json').read_text())
_n = max(int(f.stem) for f in (ROOT / 'data' / 'editions').glob('*.json'))   # newest edition
ed = json.loads((ROOT / 'data' / 'editions' / f'{_n}.json').read_text())
def photo(t):
    m = man.get(t.replace(' ', '_')); return f"{IMG}/{pathlib.Path(m['file']).stem}.webp"
def story(di, k): d = ed['days'][di]; return ([d['lead']] + d['more'])[k]
LOGO = '<svg viewBox="0 0 80 80" fill="none" stroke="currentColor"><rect x="12" y="10" width="54" height="54" stroke-width="2" transform="rotate(-6 39 37)"/><rect x="15" y="14" width="54" height="54" stroke-width="2" transform="rotate(4 42 41)"/><path d="M20 28L28 54L40 26L52 54L60 28" stroke-width="4" stroke-linejoin="round"/><path d="M20 58h40" stroke-width="2" stroke-dasharray="3 3"/></svg>'
TH = {'cream': ('#f7f2e8', '#0a0a0a', '#8c1d18'), 'navy': ('#10224a', '#ffffff', '#f2c94c'), 'gold': ('#e9d98a', '#0a0a0a', '#8c1d18')}
CSS = '''.big{text-align:center;margin-left:auto;margin-right:auto}h1.big{font:900 122px/1.0 'Playfair Display',serif;letter-spacing:-.03em;margin-top:70px;max-width:930px}.sub.big{font:400 42px/1.35 Roboto;margin-top:30px;max-width:800px}.url{position:absolute;z-index:6;right:70px;bottom:50px;font:900 40px Roboto;letter-spacing:.01em}.note{position:absolute;z-index:4;font:700 46px/1.05 Caveat,cursive;text-align:center}
*{box-sizing:border-box;margin:0}body{background:#888;font-family:'Roboto',sans-serif}
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
    """Big-mascot layout: brand top-left, huge centred headline, small sub, big koala bottom-left, url bottom-right."""
    bg, fg, acc = TH[th]; h = h.replace('<em>', f'<em style="color:{acc};font-style:italic">')
    return f'''<div class="post" id="a{i:02d}" style="background:{bg};color:{fg}"><div class="top">{LOGO}<span>Weekfold</span></div>
<h1 class="big">{h}</h1><div class="sub big">{sub}</div>{body}
<div class="url" style="color:{fg}">weekfold.in</div></div>'''
def note(txt, right=70, bottom=640, w=300, arrow='up'):
    return f'<div class="note" style="right:{right}px;bottom:{bottom}px;width:{w}px">{txt}</div>'
def phone(f, right=70, w=400, h=520): return f'<div class="ph" style="right:{right}px;width:{w}px;height:{h}px;bottom:170px"><img src="{SH}/{f}.png"></div>'
def koala(n, h, left=None, right=None, bottom=96, rot=0):
    pos = f'left:{left}px;' if left is not None else f'right:{right}px;'
    return f'<img class="kl" src="{K}/{n}.png" style="{pos}bottom:{bottom}px;height:{h}px;transform:rotate({rot}deg)">'
def collage(items):
    return ''.join(f'<div class="pol" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;transform:rotate({r}deg)"><img src="{photo(t)}"></div>' for t, x, y, w, h, r in items)

A = []
KB = dict(left=-40, bottom=-40)   # big mascot bleeding off the bottom-left like the reference
def big(n, h=700, **kw): return koala(n, h, **{**KB, **kw})
A.append(ad(1, 'cream', '', 'The world’s week, <em>folded</em>.', 'One free news edition, every Sunday.', phone('landing', right=70, w=300, h=420, ) .replace('bottom:86px','bottom:170px') + note('your Sunday read', right=70, bottom=620) + big('cheer', 620, left=-60)))
A.append(ad(2, 'navy', '', 'Too much news. <em>Too little time.</em>', 'We read the week so you don’t have to scroll it.',
    collage([('United_States_Capitol', 690, 660, 290, 210, 5), ('Oil_tanker', 740, 880, 260, 180, -6), ('Heat_wave', 720, 1060, 220, 130, 4)]) + big('worry', 620, left=-50)))
A.append(ad(3, 'cream', '', 'One page for <em>every day.</em>', 'Monday to Sunday, the stories that still mattered.', phone('days', right=70, w=300, h=420).replace('bottom:86px','bottom:170px') + note('tap a day', right=110, bottom=600) + big('point')))
A.append(ad(4, 'gold', '', 'Sources on <em>every story.</em>', 'Two outlets minimum. Always linked.', phone('story_src', right=70, w=300, h=420).replace('bottom:86px','bottom:170px') + note('check it yourself', right=70, bottom=600) + big('magnify', 680)))
A.append(ad(5, 'navy', '', 'Free. No ads. <em>No paywall.</em>', 'Just the week’s news, in plain English.', phone('home', right=70, w=300, h=420).replace('bottom:86px','bottom:170px') + note('no catch, really', right=70, bottom=600) + big('thumb')))
wk = ''.join(f'<div class="wd"><b>{d["date"][8:]} Nov</b><div style="background-image:url({photo(d["lead"]["image"]["wiki"])})"></div></div>' for d in ed['days'])
A.append(ad(6, 'cream', '', 'A new edition <em>every Sunday.</em>', 'Seven days. One read.', f'<div class="week" style="bottom:170px">{wk}</div>' + koala('sun', 260, right=50, bottom=420) + note('see you Sunday!', right=330, bottom=470, w=320)))
A.append(ad(7, 'gold', '', 'Two games. <em>Every day.</em>', 'A mini crossword and Weekfold Word.', phone('word', right=60, w=270, h=420).replace('bottom:86px','bottom:170px') + phone('crossword', right=370, w=270, h=420).replace('bottom:86px','bottom:170px') + note('play both, free', right=300, bottom=600, w=360) + big('mug', 480, left=-50)))
A.append(ad(8, 'navy', '', 'Five minutes on <em>the planet.</em>', 'Politics, science, climate, sport and culture.',
    collage([('Greenland_ice_sheet', 700, 660, 290, 210, -5), ('Pedro_Alliana', 750, 880, 250, 190, 5), ('Joshua_Kutryk', 760, 1080, 170, 120, -4)]) + big('globe', 620, left=-50)))
A.append(ad(9, 'cream', '', 'No spin. <em>Just the facts.</em>', 'Plain-English summaries, sources one tap away.', phone('story', right=70, w=300, h=420).replace('bottom:86px','bottom:170px') + note('tap for sources', right=70, bottom=600) + big('shock', 700)))
A.append(ad(10, 'navy', '', 'Get Weekfold <em>every Sunday.</em>', 'Free forever. Link in bio.', phone('landing', right=70, w=300, h=420).replace('bottom:86px','bottom:170px') + note('join free', right=130, bottom=600) + big('mega')))

N = [  # THE WEEKLY TASK EDITS THIS LIST: (day index 0-6, story index within day, theme cream/navy/gold, koala pose or None). Pick the 5 biggest stories; no koala on deaths/violence.
 (1, 0, 'cream', 'point'), (3, 0, 'navy', None), (3, 1, 'gold', 'magnify'), (5, 0, 'navy', None), (4, 1, 'cream', 'worry')]
NCSS = '''.np{display:flex;flex-direction:column;padding:60px 70px 0}.np .top{margin-bottom:0}.np .r{font:700 26px Roboto;letter-spacing:.14em;text-transform:uppercase;margin-left:auto}
.np .meta{margin-top:46px;display:flex;align-items:center;gap:16px}.np .meta span{font:500 28px Roboto;opacity:.75}
.np h2{font:900 92px/1.02 'Playfair Display',serif;letter-spacing:-.03em;margin-top:22px}.np p.d{font:400 38px/1.35 Roboto;margin-top:24px;opacity:.92;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.np .zone{position:relative;flex:1;margin:34px -70px 0}.np .foot2{position:absolute;left:70px;right:70px;bottom:46px;z-index:6;display:flex;justify-content:space-between;font:700 30px Roboto}
.np .pic{position:absolute;border:7px solid #000;box-shadow:12px 12px 0 #000;overflow:hidden;background:#fff}.np .pic img{width:100%;height:100%;object-fit:cover;display:block}'''
def news(i, spec, H=1350):
    di, k, th, ko = spec; s = story(di, k); bg, fg, acc = TH[th]; d = ed['days'][di]['date']
    import datetime; day = datetime.date.fromisoformat(d).strftime('%A %-d %B')
    pill_bg, pill_fg = (acc, '#fff') if th != 'navy' else ('#f2c94c', '#10224a')
    hl = s['headline']; fs = 92 if len(hl) < 60 else 80
    if ko: pic = '<div class="pic" style="right:70px;%s;width:%dpx;height:%dpx;transform:rotate(2.5deg)"><img src="%s"></div>' % ('bottom:185px' if H < 1500 else 'top:30px', 470 if H < 1500 else 470, 300 if H < 1500 else 700, photo(s['image']['wiki'])); kl = f'<img class="kl" src="{K}/{ko}.png" style="left:-50px;bottom:-30px;height:{540 if H<1500 else 820}px;z-index:3">'
    else: pic = '<div class="pic" style="left:70px;right:82px;top:0;bottom:130px"><img src="%s"></div>' % photo(s['image']['wiki']); kl = ''
    return f'''<div class="post np" id="n{i:02d}{'s' if H>1400 else ''}" style="height:{H}px;background:{bg};color:{fg}"><div class="top">{LOGO}<span>Weekfold</span><span class="r" style="color:{acc}">The week · {i}/5</span></div>
<div class="meta"><span class="pill" style="background:{pill_bg};color:{pill_fg};border-color:#000">{s['category']}</span><span>{day}</span></div>
<h2 style="font-size:{fs}px">{html.escape(hl)}</h2><p class="d">{html.escape(s['dek'])}</p>
<div class="zone">{pic}{kl}<div class="foot2" style="{'flex-direction:column;align-items:flex-end;gap:6px' if ko else ''}"><span>Source: {html.escape(s['sources'][0]['name'].split(' (')[0])}</span><span>weekfold.in</span></div></div></div>'''
posts = A + [news(i + 1, s) for i, s in enumerate(N)] + [news(i + 1, s, 1920) for i, s in enumerate(N)]
page = '<html><head><meta charset="utf-8"><style>' + CSS + NCSS + '</style></head><body>' + ''.join(posts) + '</body></html>'
(HERE / 'posts.html').write_text(page, encoding='utf-8')
out = HERE / 'out'; out.mkdir(exist_ok=True)
for f in out.glob('*.png'): f.unlink()
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1920}, device_scale_factor=2)
    pg.goto((HERE / 'posts.html').as_uri()); pg.wait_for_timeout(2000)
    for i in range(10): pg.locator(f'#a{i+1:02d}').screenshot(path=str(out / f'weekfold-ad-{i+1:02d}.png'))
    for i in range(5):
        pg.locator(f'#n{i+1:02d}').screenshot(path=str(out / f'weekfold-news-{i+1:02d}.png'))
        pg.locator(f'#n{i+1:02d}s').screenshot(path=str(out / f'weekfold-story-{i+1:02d}.png'))
print(len(posts), 'posts ->', out)
