# -*- coding: utf-8 -*-
"""GMS2 전용 글꼴 번호 문자열 전수(읽기 전용): 번호 1~99 만으로 된 연속 워드, 일본어 2자 이상, 처리 목록 표시."""
import sys, os, struct, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B, gms_build as G
sys.stdout.reconfigure(encoding='utf-8')
iso, E = B.disc('K'); d, L = G.table(iso, E); R = G.rows(); done = {st for st, n, s in G.runs(d, L)}
n = len(d) // 2; W = struct.unpack('>%dH' % n, d[:n * 2]); i = 0; out = []
while i < n:
    if 1 <= W[i] <= 99:
        j = i
        while j < n and W[j] <= 99: j += 1
        s = ''.join(L[x - 1] if x else '　' for x in W[i:j]).strip('　')
        if 2 <= len(s) <= 24 and len(re.findall('[ぁ-ヶ一-龥]', s)) >= 2 and '?' not in s: out.append((i * 2, s, j * 2 < len(d) and W[j]))
        i = j
    else: i += 1
for o, s, nx in out:
    if not any(a <= o < a + 60 for a in done) or o < 0x12000: print('%X %s 뒤 %s' % (o, s, hex(nx) if nx is not False else '-'), '처리' if any(a == o for a in done) else '')
print(len(out))
