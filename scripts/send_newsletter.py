#!/usr/bin/env python3
"""Send (or draft) the newest Weekfold edition through Buttondown.

Used by .github/workflows/newsletter.yml after a new edition is pushed.
Environment:
  BUTTONDOWN_API_KEY  required (Buttondown › Settings › API)
  NEWSLETTER_MODE     "draft" (default: saved in Buttondown for you to review and send)
                      or "send" (goes out to subscribers automatically)
"""
import json, os, pathlib, sys, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
key = os.environ.get('BUTTONDOWN_API_KEY', '').strip()
mode = os.environ.get('NEWSLETTER_MODE', 'draft').strip().lower() or 'draft'
if not key:
    print('BUTTONDOWN_API_KEY is not set, so no email was created. Add it under GitHub › Settings › Secrets and variables › Actions.')
    sys.exit(0)

cfg = json.loads((ROOT / 'config.json').read_text(encoding='utf-8'))
if not cfg.get('site_url'):
    print('config.json has no site_url, so the email links would not work. Set site_url first.')
    sys.exit(1)

meta = json.loads((ROOT / 'docs' / 'newsletter' / 'latest.json').read_text(encoding='utf-8'))
body = (ROOT / 'docs' / 'newsletter' / 'latest.md').read_text(encoding='utf-8')
payload = {'subject': meta['subject'], 'body': body, 'status': 'about_to_send' if mode == 'send' else 'draft'}

req = urllib.request.Request('https://api.buttondown.com/v1/emails', data=json.dumps(payload).encode('utf-8'), method='POST',
                             headers={'Authorization': 'Token ' + key, 'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        print(f"Buttondown accepted edition {meta['number']} ({payload['status']}): HTTP {r.status}")
except urllib.error.HTTPError as e:
    print(f'Buttondown refused the email: HTTP {e.code}\n{e.read().decode("utf-8", "replace")[:2000]}')
    sys.exit(1)
