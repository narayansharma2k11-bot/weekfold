#!/usr/bin/env python3
"""Checks every data/crosswords/<edition>.json. A file is either one puzzle or {"puzzles":[7 puzzles, Monday..Sunday]}.
A puzzle: square grid of capital letters, '#' for black squares; every across/down entry (2+ letters) has exactly one clue."""
import json, sys, pathlib

def check(name, d):
    g = d['grid']; n = len(g); errs = []
    if any(len(r) != n for r in g): errs.append('grid is not square')
    if any((ch != '#' and not ch.isalpha()) or (ch.isalpha() and not ch.isupper()) for r in g for ch in r): errs.append('grid must be capital letters or #')
    cell = lambda r, c: 0 <= r < n and 0 <= c < n and g[r][c] != '#'
    num = 0; across = {}; down = {}
    for r in range(n):
        for c in range(n):
            if not cell(r, c): continue
            sa = not cell(r, c - 1) and cell(r, c + 1); sd = not cell(r - 1, c) and cell(r + 1, c)
            if sa or sd: num += 1
            if sa:
                w = ''; k = c
                while cell(r, k): w += g[r][k]; k += 1
                across[str(num)] = w
            if sd:
                w = ''; k = r
                while cell(k, c): w += g[k][c]; k += 1
                down[str(num)] = w
    for kind, ents, clues in (('across', across, d.get('across', {})), ('down', down, d.get('down', {}))):
        for k in ents:
            if k not in clues or not clues[k].strip(): errs.append(f'{kind} {k} ({ents[k]}) has no clue')
        for k in clues:
            if k not in ents: errs.append(f'{kind} clue {k} has no entry in the grid')
    seen = set(); stack = [(r, c) for r in range(n) for c in range(n) if cell(r, c)][:1]
    while stack:
        r, c = stack.pop()
        if (r, c) in seen: continue
        seen.add((r, c)); stack += [(a, b) for a, b in ((r+1, c), (r-1, c), (r, c+1), (r, c-1)) if cell(a, b)]
    if len(seen) != sum(cell(r, c) for r in range(n) for c in range(n)): errs.append('grid is not connected')
    print(name, 'OK' if not errs else 'PROBLEMS', f'({len(across)} across, {len(down)} down)')
    for e in errs: print('  -', e)
    return bool(errs)

bad = 0
for p in sorted(pathlib.Path(__file__).resolve().parent.parent.joinpath('data', 'crosswords').glob('*.json')):
    raw = json.loads(p.read_text(encoding='utf-8'))
    ps = raw['puzzles'] if 'puzzles' in raw else [raw]
    if 'puzzles' in raw and len(ps) != 7: print(p.name, 'needs exactly 7 puzzles (Monday to Sunday)'); bad = 1
    for i, d in enumerate(ps): bad |= check(p.name + (f' #{i+1}' if 'puzzles' in raw else ''), d)
sys.exit(bad)
