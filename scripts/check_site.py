#!/usr/bin/env python3
"""Checks a built Weekfold site folder (docs/ or test-site/). Free, offline, no network.
Fails if: a page lacks lang, <title> or viewport; a local link or #anchor on a static page points nowhere;
a JSON data file is invalid; or (when fonts are self-hosted) a page still loads Google Fonts.
Run: python3 scripts/check_site.py [folder]"""
import json, pathlib, re, sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'docs')
cfg = json.loads((pathlib.Path(__file__).resolve().parent.parent / 'config.json').read_text(encoding='utf-8'))
self_fonts = (cfg.get('test_build') or {}).get('self_host_fonts') and root.name != 'docs'
errs = []
pages = sorted(root.rglob('*.html'))
ids = {p.name: set(re.findall(r'\bid="([^"]+)"', p.read_text(encoding='utf-8', errors='replace'))) for p in pages}
DYNAMIC = {'home.html', 'index.html'}   # these pages make their #routes in JavaScript
for p in pages:
    rel = p.relative_to(root).as_posix()
    if rel.startswith('newsletter/') or rel.startswith('google'):
        continue
    t = p.read_text(encoding='utf-8', errors='replace')
    if not re.search(r'<html[^>]*\blang="', t): errs.append(f'{rel}: no lang on <html>')
    if not re.search(r'<title>[^<]+</title>', t): errs.append(f'{rel}: no <title>')
    if 'name="viewport"' not in t: errs.append(f'{rel}: no viewport meta')
    if self_fonts and 'fonts.googleapis.com' in t: errs.append(f'{rel}: still loads Google Fonts')
    for href in re.findall(r'\b(?:href|src)="([^"]+)"', t):
        if re.match(r'^(https?:|mailto:|tel:|data:|javascript:|#$)', href) or '{' in href:
            continue
        path, _, frag = href.partition('#')
        path = path.split('?')[0]
        target = (p.parent / path) if path else p
        if path and not target.exists():
            errs.append(f'{rel}: broken link {href}'); continue
        if frag and target.name not in DYNAMIC and target.suffix == '.html' and frag not in ids.get(target.name, set()):
            errs.append(f'{rel}: missing anchor {href}')
for j in root.rglob('*.json'):
    try: json.loads(j.read_text(encoding='utf-8'))
    except Exception as ex: errs.append(f'{j.relative_to(root)}: invalid JSON ({ex})')
if errs:
    print('Site check FAILED:', *errs[:60], sep='\n  - '); sys.exit(1)
print(f'Site check OK: {len(pages)} pages in {root.name}/')
