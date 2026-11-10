"""Evergreen Instagram ad posts for Weekfold (1080x1350). Run: python3 promo/instagram/gen.py  -> promo/instagram/out/*.png"""
import pathlib, html
from playwright.sync_api import sync_playwright
HERE = pathlib.Path(__file__).resolve().parent; K = (HERE.parent.parent / 'src' / 'koala').as_uri()
LOGO = '<svg viewBox="0 0 80 80" fill="none" stroke="currentColor"><rect x="12" y="10" width="54" height="54" stroke-width="2" transform="rotate(-6 39 37)"/><rect x="15" y="14" width="54" height="54" stroke-width="2" transform="rotate(4 42 41)"/><path d="M20 28L28 54L40 26L52 54L60 28" stroke-width="4" stroke-linejoin="round"/><path d="M20 58h40" stroke-width="2" stroke-dasharray="3 3"/></svg>'
# (theme, kicker, headline, sub, koala, koala height)
P = [
 ('cream', 'Hello, world', 'The world’s week, <em>folded</em> into one free edition.', 'Weekfold is a free news edition that lands every Sunday. One page for every day.', 'wave', 500),
 ('navy', 'Sound familiar?', 'Too much news. <em>Too little time.</em>', 'We read the week so you don’t have to scroll it.', 'worry', 500),
 ('cream', 'How it works', 'One page for <em>every day</em> of the week.', 'Monday to Sunday, the stories that still mattered by the end of the week.', 'point', 500),
 ('gold', 'Our rule', 'Every story <em>names its sources.</em>', 'At least two independent outlets behind every story. Always linked.', 'magnify', 500),
 ('navy', 'The best part', 'Free. No ads. <em>No paywall.</em>', 'Just the week’s news, written in plain English.', 'thumb', 500),
 ('cream', 'Mark your calendar', 'A new edition <em>every Sunday.</em>', 'Straight to your inbox. One read, and you’re caught up.', 'sun', 500),
 ('gold', 'Games', 'Two minutes. <em>One crossword.</em>', 'A fresh mini crossword every day, right inside Weekfold.', 'mug', 500),
 ('navy', 'World news', 'Five minutes to <em>catch up</em> on the planet.', 'Politics, science, climate, sport, culture and more, all in one place.', 'globe', 500),
 ('cream', 'Our promise', 'No spin. <em>Just the facts.</em>', 'Plain-English summaries of what actually happened, with the sources one tap away.', 'shock', 500),
 ('navy', 'Ready?', 'Get Weekfold <em>every Sunday.</em>', 'Free forever. Join at weekfold.in (link in bio).', 'mega', 500),
]
TH = {'cream': ('#f7f2e8', '#0a0a0a', '#8c1d18', '#10224a'), 'navy': ('#10224a', '#ffffff', '#f2c94c', '#f7f2e8'), 'gold': ('#e9d98a', '#0a0a0a', '#8c1d18', '#10224a')}
CSS = '''*{box-sizing:border-box;margin:0}body{background:#888;font-family:'Roboto',sans-serif}
.post{width:1080px;height:1350px;position:relative;overflow:hidden;padding:70px 76px;display:flex;flex-direction:column;margin-bottom:20px}
.top{display:flex;align-items:center;gap:14px;font:900 44px 'Playfair Display',serif;letter-spacing:-.01em}.top svg{width:56px;height:56px}
.k{margin-top:70px;font:700 28px 'Roboto';letter-spacing:.18em;text-transform:uppercase}
h1{font:900 112px/1.02 'Playfair Display',serif;letter-spacing:-.025em;margin-top:22px;max-width:900px}h1 em{font-style:italic;font-weight:900}
.sub{font:400 38px/1.4 'Roboto';margin-top:30px;max-width:640px;opacity:.92}
.kl{position:absolute;right:50px;bottom:108px}
.foot{position:absolute;left:0;right:0;bottom:0;height:86px;display:flex;align-items:center;justify-content:space-between;padding:0 76px;font:700 30px 'Roboto';letter-spacing:.08em;border-top:3px solid currentColor}
.card{position:absolute;right:76px;bottom:130px;width:430px;height:430px;border-radius:50%;opacity:.0}'''
def post(i, p):
    th, k, h, sub, ko, kh = p; bg, fg, acc, ink = TH[th]
    return f'''<div class="post" id="p{i+1:02d}" style="background:{bg};color:{fg}"><div class="top">{LOGO}<span>Weekfold</span></div>
<div class="k" style="color:{acc}">{k}</div><h1>{h.replace('<em>', f'<em style="color:{acc}">')}</h1><div class="sub">{sub}</div>
<img class="kl" src="{K}/{ko}.webp" style="height:{kh}px"><div class="foot"><span>weekfold.in</span><span style="color:{acc}">FREE · EVERY SUNDAY</span></div></div>'''
page = '<html><head><meta charset="utf-8"><style>' + CSS + '</style></head><body>' + ''.join(post(i, p) for i, p in enumerate(P)) + '</body></html>'
(HERE / 'posts.html').write_text(page, encoding='utf-8')
out = HERE / 'out'; out.mkdir(exist_ok=True)
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1350})
    pg.goto((HERE / 'posts.html').as_uri()); pg.wait_for_timeout(1500)
    for i in range(len(P)):
        pg.locator(f'#p{i+1:02d}').screenshot(path=str(out / f'weekfold-post-{i+1:02d}.png'))
print(len(P), 'posts ->', out)
