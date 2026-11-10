import sys, os, http.server, threading, functools
from playwright.sync_api import sync_playwright
f, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=os.path.dirname(os.path.abspath(__file__)))
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 8799), functools.partial(Q, directory=os.path.dirname(os.path.abspath(__file__)))); threading.Thread(target=srv.serve_forever, daemon=True).start()
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
    pg.goto('http://127.0.0.1:8799/' + f); pg.wait_for_timeout(1200)
    ids = pg.evaluate("[...document.querySelectorAll('.story')].map(e=>e.id)")
    for i in ids:
        pg.locator('#' + i).screenshot(path=f'{out}/{i}.png')
    # overflow check: any element whose right edge exceeds story width or text overflowing its box
    bad = pg.evaluate("""[...document.querySelectorAll('.story')].flatMap(s=>{const R=s.getBoundingClientRect();return [...s.querySelectorAll('*')].filter(e=>{const r=e.getBoundingClientRect();if(!r.width||e.classList.contains('cat')||e.closest('.crease,.mapw,.paper'))return false;return r.right>R.right-40||r.left<R.left+40&&!e.closest('.mapw')}).slice(0,3).map(e=>s.id+':'+e.tagName+'.'+e.className+' '+Math.round(e.getBoundingClientRect().right-R.left))})""")
    print('edge warnings:', bad[:12])
    print(len(ids), 'stories ->', out)
srv.shutdown()
