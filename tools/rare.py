# -*- coding: utf-8 -*-
"""드문 글자 문맥(판독 검수용, 읽기 전용)."""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import extract as X
sys.stdout.reconfigure(encoding='utf-8')
rows = X.disc('K') + X.disc('F')
c = collections.Counter(ch for r in rows for ch in r[3])
seen = {}
for r in rows:
    t = r[3]
    for i, ch in enumerate(t):
        if c[ch] <= 3 and ch not in seen: seen[ch] = t[max(0, i - 6):i + 6]
print(len(seen))
print(' / '.join(seen.values()))
print([t for t in {r[3] for r in rows} if '？' in t or '〓' in t][:6])
