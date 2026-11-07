# -*- coding: utf-8 -*-
"""작전파일 글꼴 칸 배치 판정(읽기 전용): 본편 글자와 비슷한 정도."""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
K = B.disc('K'); F = B.disc('F')
def rd(x, n): return x[0].read(*x[1][n][1:3])
mp = rd(K, '/VIEWCG/ASC16MAP.BIN'); w = struct.unpack('>%dH' % (len(mp) // 2), mp)
ck = rd(K, '/VIEWCG/ASC16X16.BIN') + rd(K, '/VIEWCG/ASC16_2.BIN')
fa, fb = rd(F, '/VIEWCG/ASC16X16.BIN'), rd(F, '/VIEWCG/ASC16_2.BIN')
def hi(b):
    x = np.frombuffer(b, np.uint8); return (np.stack([x >> 4, x & 15], 1).reshape(-1) > 7)
def g(c, i): return b''.join(c[(t - 0x800) * 32:(t - 0x800) * 32 + 32] for t in w[i * 4:i * 4 + 4])
for name, cf in (('이어붙임', fa + fb), ('뒤 고정', fa[:70912] + fb)):
    res = []
    for i in range(0, 1192):
        a, b = hi(g(ck, i)), hi(g(cf, i))
        if len(b) == len(a): res.append((a == b).mean())
        else: res.append(0)
    r = np.array(res); print(name, '구간별 일치율', [round(float(r[x:x + 149].mean()), 3) for x in range(0, 1192, 149)], '95% 이상', int((r > .95).sum()))
print('경계 번호: 시트 칸 2216 =', [i for i in range(1192) if w[i * 4] - 0x800 >= 2216][:1])
print('--- 어긋남 찾기')
cf = fa + fb; X = np.stack([hi(cf[i * 32:i * 32 + 32]) for i in range(len(cf) // 32)])      # 칸별 비트
Kc = np.stack([hi(ck[i * 32:i * 32 + 32]) for i in range(len(ck) // 32)])
ink = Kc.sum(1)
for lo, hi_ in ((2100, 2216), (2216, 2400), (2400, 3000), (3000, 3600), (3600, 4200), (4200, 4800)):
    best = []
    for d in range(-700, 900, 1):
        idx = np.arange(lo, hi_); ok = (idx + d >= 0) & (idx + d < len(X)) & (ink[lo:hi_] > 8)
        if ok.sum() < 20: continue
        best.append((float((Kc[idx[ok]] == X[idx[ok] + d]).mean()), d))
    best.sort(reverse=True); print(lo, hi_, [(round(a, 3), d) for a, d in best[:3]])
