import sys,os,subprocess
from playwright.sync_api import sync_playwright
FPS=30
names=sys.argv[1:] or ['fold','map','games','days','sections']
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1920})
    for s in names:
        os.makedirs(f'frames/{s}',exist_ok=True)
        pg.goto(f'http://localhost:8776/scene.html?s={s}'); dur=pg.evaluate('window.ready')
        n=int(dur*FPS)
        for i in range(n):
            pg.evaluate(f'setT({i/FPS})'); pg.screenshot(path=f'frames/{s}/{i:04d}.jpg',type='jpeg',quality=92)
        print(s,n,'frames')
