# -*- coding: utf-8 -*-
"""SAKU_DT.BIN 구조 조사(읽기 전용).  python tools/sakudt.py"""
import sys, os, glob, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
R = r'C:\claude\roms\ss\World Advanced Daisenryaku\World Advanced Daisenryaku - Koutetsu no Senpuu (Japan) (Rev A) (10M)'
iso = Iso(glob.glob(R + r'\*(Track 1).bin')[0]); fs = iso.walk()
sk = sorted((f for f in fs if f[0].startswith('/SAKUSEN/')), key=lambda f: f[0])
print(len(sk), collections.Counter(f[0].split('/')[-1][:6] for f in sk).most_common(12))
for f in sk[:6] + sk[-6:]: print(f[0], f[1], f[2])
ent = {f[0]: f for f in fs}
d = iso.read(*ent['/SAKUSEN/SAKU_DT.BIN'][1:3]); print('DT', len(d))
print(d[:64].hex(' '))
print([hex(x) for x in struct.unpack('>32I', d[:128])])
# 번호열 구간: u16 BE, 값 < 0x400 이 8개 이상 이어지고 FFFF 로 끝남
runs = []; i = 0; n = len(d) // 2; w = struct.unpack('>%dH' % n, d[:n * 2])
s = None
for i, x in enumerate(w):
    if x == 0xFFFF:
        if s is not None and i - s >= 3: runs.append((s * 2, i - s))
        s = i + 1
    elif x >= 0x400: s = None
    elif s is None: s = i
print('문장 후보', len(runs), '글자 합', sum(r[1] for r in runs), runs[:8], runs[-4:])
hist = collections.Counter(r[0] >> 14 for r in runs); print(sorted(hist.items())[:40])

# 시나리오 경계: 글꼴은 처음 나오는 순서 → 새 글자 번호가 0 부터 차례로
F = {}
for k in range(1, 55):
    b = iso.read(*ent['/SAKUSEN/SAKU_F%02d.BIN' % k][1:3]); F[k] = [b[i:i + 128] for i in range(0, len(b), 128)]
print('글꼴 글자 수', [len(F[k]) for k in sorted(F)][:54], '합', sum(len(F[k]) for k in F))
uniq = collections.Counter(g for k in F for g in F[k]); print('서로 다른 그림', len(uniq), '여러 시나리오 공유', sum(1 for g, c in uniq.items() if c > 1))
big = [r for r in runs if r[0] >= 0x17000]
seg = []; mx = -1; start = None
for o, n in big:
    ids = w[o // 2:o // 2 + n]
    if 0 in ids[:4] and mx > 40:
        seg.append((start, mx)); mx = -1; start = o
    if start is None: start = o
    mx = max(mx, max(ids))
seg.append((start, mx))
print('구역', len(seg), [(hex(a), b + 1) for a, b in seg][:60])
print('첫 문장들', [w[o // 2:o // 2 + min(n, 14)] for o, n in big[:6]])
print(hex(big[0][0]), [hex(x) for x in w[big[0][0] // 2 - 24:big[0][0] // 2]])

print('=== 경계 다시')
seg = []; mx = -1; start = None; cnt = 0
for o, n in big:
    ids = [x for x in w[o // 2:o // 2 + n] if x < 0x100]
    if 32 in ids[:3] and mx > 60:
        seg.append((start, mx + 1, cnt)); mx = -1; start = o; cnt = 0
    if start is None: start = o
    if ids: mx = max(mx, max(ids))
    cnt += 1
seg.append((start, mx + 1, cnt))
fs_ = [len(F[k]) for k in sorted(F)]
print(len(seg)); print([(hex(a), b, c) for a, b, c in seg])
print('글꼴 크기와 일치', sum(1 for s_, f_ in zip(seg, fs_) if s_[1] == f_), fs_[:len(seg)][:10])
g0 = [F[k][:32] for k in sorted(F)]; print('앞 32칸 전 시나리오 같음', all(g == g0[0] for g in g0))
print('257 등 특수 값', collections.Counter(x for o, n in big for x in w[o // 2:o // 2 + n] if x >= 0xF0).most_common(12))
