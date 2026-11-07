# -*- coding: utf-8 -*-
"""스테이트 VDP2 면 렌더 + 칸 출처(읽기 전용).  python tools/plane_src.py 스테이트번호 [K|F]
   출력 work/view/audit/p_<번호>.png(면별 회색, 8배 칸 눈금), work/text/plane_<번호>.tsv(면, x, y, 칸, 파일, 위치)."""
import sys, os, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate, asc_build as B
import numpy as np
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8')
st = sys.argv[1]; tag = sys.argv[2] if len(sys.argv) > 2 else 'K'
s, v = mstate.load('work/states/%s.state' % st)
o, n = v['VDP2/VRAM']; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; vr = bytes(b)
a, c = v['VDP2/RawRegs']; r = [int(x) for x in np.frombuffer(s[a:a + c], '<u2')]
R = lambda x: r[x // 2]
bgon = R(0x20); chcta = R(0x28); chctb = R(0x2A)
bits = {0: chcta >> 4 & 7, 1: chcta >> 12 & 3, 2: chctb >> 1 & 1, 3: chctb >> 5 & 1}
mp = {0: R(0x40) & 0x3F, 1: R(0x44) & 0x3F, 2: R(0x48) & 0x3F, 3: R(0x4C) & 0x3F}
print('BGON %04X' % bgon, '비트', bits, '맵', {k: hex(x * 0x2000) for k, x in mp.items()},
      'PNCN', [hex(R(0x30 + i * 2)) for i in range(4)], '스크롤', [hex(R(x)) for x in (0x70, 0x74, 0x80, 0x84, 0x90, 0x92, 0x94, 0x96)])
base = {p: (R(0x30 + p * 2) >> 2 & 7) << 12 for p in range(4)}; print('칸 기준', {k: hex(x) for k, x in base.items()})
iso, E = B.disc(tag)
idx = {}
want = set()
planes = {}
for p in range(4):
    if not bgon >> p & 1: continue
    m = np.frombuffer(vr[mp[p] * 0x2000:mp[p] * 0x2000 + 0x2000], '>u2').reshape(64, 64)
    planes[p] = m
    sz = 64 if bits[p] else 32
    for y in range(32):
        for x in range(46):
            t = (int(m[y, x]) & 0xFFF) + base[p]
            d = vr[t * 32:t * 32 + sz]
            if len(set(d)) >= 5: want.add(d)
print('찾을 칸', len(want), flush=True)
SK = ('.MUS', '.CPK', '/')
for fn, e in E.items():
    if fn.endswith(SK) or e[2] < 64 or fn.startswith(('/CDDA', '/UNIT3D', '/UNITPACK', '/UNITINIT', '/EARTH')): continue
    try: d = iso.read(*e[1:3])
    except EOFError: continue
    for sz in (32, 64):
        for al in range(0, 4, 2):
            for i in range(al, len(d) - sz, 32 if sz == 32 else 64):
                t = d[i:i + sz]
                if t in want and t not in idx: idx[t] = (fn, i)
rows = []
H = 32 * 8; W = 46 * 8
pg = Image.new('L', ((W + 8) * 2, (H + 8) * 2), 30)
for k, (p, m) in enumerate(planes.items()):
    sz = 64 if bits[p] else 32
    g = np.zeros((H, W), np.uint8)
    for y in range(32):
        for x in range(46):
            e_ = int(m[y, x]); t = (e_ & 0xFFF) + base[p]; dd = vr[t * 32:t * 32 + sz]
            if not any(dd): continue
            if sz == 64: q = np.frombuffer(dd, np.uint8).reshape(8, 8)
            else:
                q0 = np.frombuffer(dd, np.uint8); q = (np.stack([q0 >> 4, q0 & 15], 1).reshape(8, 8) * 17).astype(np.uint8)
            if e_ & 0x8000 and False: q = q[::-1]
            g[y * 8:y * 8 + 8, x * 8:x * 8 + 8] = q
            src = idx.get(dd)
            rows.append((p, x, y, t, src[0] if src else '-', src[1] if src else -1))
    pg.paste(Image.fromarray(g), ((k % 2) * (W + 8), (k // 2) * (H + 8)))
os.makedirs('work/view/audit', exist_ok=True)
pg.save('work/view/audit/p_%s.png' % st)
open('work/text/plane_%s.tsv' % st, 'w', encoding='utf-8', newline='\n').write(''.join('%d\t%d\t%d\t%X\t%s\t%X\n' % r for r in rows))
c = collections.Counter((r[0], r[4]) for r in rows); print(c.most_common(16))
