#!/usr/bin/env python3
"""Checks every data/crosswords/<edition>.json: a square grid of capital letters with '#' for black squares,
every across/down entry (2+ letters) must have exactly one clue, and no clue may point at a missing entry."""
import json, sys, pathlib
bad = 0
for p in sorted(pathlib.Path(__file__).resolve().parent.parent.joinpath('data', 'crosswords').glob('*.json')):
    d = json.loads(p.read_text(encoding='utf-8')); g = d['grid']; n = len(g); errs = []
    if any(len(r) != n for r in g): errs.append('grid is not square')
    if any(ch != '#' and not ch.isalpha() or (ch.isalpha() and not ch.isupper()) for r in g for ch in r): errs.append('grid must be capital letters or #')
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
    # every letter must belong to at least one entry and the grid must be connected
    seen = set(); stack = [(r, c) for r in range(n) for c in range(n) if cell(r, c)][:1]
    while stack:
        r, c = stack.pop()
        if (r, c) in seen: continue
        seen.add((r, c)); stack += [(a, b) for a, b in ((r+1, c), (r-1, c), (r, c+1), (r, c-1)) if cell(a, b)]
    if len(seen) != sum(cell(r, c) for r in range(n) for c in range(n)): errs.append('grid is not connected')
    print(p.name, 'OK' if not errs else 'PROBLEMS', f'({len(across)} across, {len(down)} down)')
    for e in errs: print('  -', e); bad = 1
sys.exit(bad)
