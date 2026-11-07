# -*- coding: utf-8 -*-
"""Sakusen File SAKU_DT·글꼴 규모(읽기 전용).  python tools/sf_font.py"""
import sys, os, glob, struct, hashlib, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\claude\roms\ss\World Advanced Daisenryaku'
R2 = glob.glob(B + r'\*Sakusen*')[0]
b = Iso(sorted(glob.glob(R2 + r'\*.bin'))[0]); fs = b.walk(); ent = {f[0]: f for f in fs}
sk = sorted(f[0] for f in fs if f[0].startswith('/SAKUSEN/'))
print(len(sk), sk[:3], sk[-4:], collections.Counter(x.split('/')[-1][:5] for x in sk))
hm = dict(l.rstrip('\n').split('\t') for l in open('work/text/glyph_final.tsv', encoding='utf-8'))
F = {}
for n in sk:
    if 'SAK_F' in n:
        d = b.read(*ent[n][1:3]); F[int(n[-7:-4])] = [hashlib.md5(d[i:i + 128]).hexdigest()[:10] for i in range(0, len(d), 128)]
print('글꼴', len(F), '글자 합', sum(len(v) for v in F.values()))
u = {h for v in F.values() for h in v}; print('고유', len(u), '본편에 있는 글자', sum(1 for h in u if h in hm), '새 글자', sum(1 for h in u if h not in hm))
d = b.read(*ent['/SAKUSEN/SAKU_DT.BIN'][1:3]); n = len(d) // 2; w = struct.unpack('>%dH' % n, d[:n * 2])
runs = []; s = None
for i, x in enumerate(w):
    if x == 0xFFFF:
        if s is not None and i - s >= 3: runs.append((s * 2, i - s))
        s = i + 1
    elif x >= 0x400: s = None
    elif s is None: s = i
big = [r for r in runs if r[1] >= 3]
print('문장 후보', len(runs), '글자', sum(r[1] for r in runs), hex(runs[0][0]), hex(runs[-1][0]))
offs = {o for o, _ in runs}
c = collections.Counter()
for i in range(0, len(d) - 3, 4):
    v = struct.unpack('>I', d[i:i + 4])[0]
    if v - 0x2C0000 in offs: c[i >> 8] += 1
print('포인터 구역', sorted(c.items())[:12], sum(c.values()))
for t in ('/README.TXT',): print(b.read(*ent[t][1:3])[:0])
print([f[0] for f in fs if f[0].endswith('.TXT')], [(f[0], f[2]) for f in fs if f[0].endswith('.CPK')])

print('=== 구조 대조')
import numpy as np
from PIL import Image
a = Iso(glob.glob(glob.glob(B + r'\*Koutetsu*')[0] + r'\*(Track 1).bin')[0]); ea = {f[0]: f for f in a.walk()}
A = a.read(*ea['/SAKUSEN/SAKU_F01.BIN'][1:3])
Bf = b.read(*ent['/SAKUSEN/SAK_F001.BIN'][1:3])
def px(g):
    x = np.frombuffer(g, np.uint8); p = np.stack([x >> 4, x & 15], 1).reshape(4, 8, 8)
    o = np.zeros((16, 16), np.uint8); o[:8, :8], o[:8, 8:], o[8:, :8], o[8:, 8:] = p; return o
print('앞 32칸 본편과 같음', sum(A[i * 128:i * 128 + 128] == Bf[i * 128:i * 128 + 128] for i in range(32)))
print('색 본편', collections.Counter(int(v) for i in range(40, 90) for v in px(A[i * 128:i * 128 + 128]).ravel()).most_common(5))
print('색 작전', collections.Counter(int(v) for i in range(40, 90) for v in px(Bf[i * 128:i * 128 + 128]).ravel()).most_common(5))
NG = len(Bf) // 128; W = 24; im = np.zeros((6 * 18, W * 18), np.uint8)
for i in range(32, min(NG, 32 + 6 * W)):
    j = i - 32; im[j // W * 18:j // W * 18 + 16, j % W * 18:j % W * 18 + 16] = px(Bf[i * 128:i * 128 + 128]) * 17
Image.fromarray(im).resize((W * 18 * 3, 6 * 18 * 3), 0).save('work/view/sf_f001.png')
txt = [r for r in runs if r[0] >= 0x1000]
print('줄', len(txt), [(hex(o), l) for o, l in runs[:6]])
j0 = [i for i, (o, l) in enumerate(runs) if 32 in w[o // 2:o // 2 + 3]]
print('번호 32로 시작 줄', len(j0), [hex(runs[i][0]) for i in j0[:10]], '간격', collections.Counter(b_ - a_ for a_, b_ in zip(j0, j0[1:])).most_common(5))
print('앞줄', [w[o // 2:o // 2 + min(l, 8)] for o, l in runs[:10]])
ptr = [i for i in range(0, len(d) - 3, 4) if struct.unpack('>I', d[i:i + 4])[0] - 0x2C0000 in offs]
print('포인터', len(ptr), hex(ptr[0]), hex(ptr[-1]), len(d), hex(len(d)))
