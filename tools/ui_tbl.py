# -*- coding: utf-8 -*-
"""GAME2 문자열 묶음의 색인(간격 표) 찾기(읽기 전용)."""
import sys, os, glob, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
rows = [l.rstrip('\n').split('\t') for l in open('work/text/ui_pos.tsv', encoding='utf-8')]
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); ent = {f[0]: f for f in iso.walk()}
d = iso.read(*ent['/GAME2.BIN'][1:3])
offs = sorted({int(r[3], 16) for r in rows if r[2] == '/GAME2.BIN' and r[1] == 'K'})
print(len(offs), [hex(x) for x in offs[:6]], [hex(x) for x in offs[-6:]])
grp = []; cur = [offs[0]]
for a, b in zip(offs, offs[1:]):
    if b - a > 0x100: grp.append(cur); cur = []
    cur.append(b)
grp.append(cur); print([(hex(g[0]), hex(g[-1]), len(g)) for g in grp])
g = grp[0]; dif = [b - a for a, b in zip(g, g[1:])][:20]; print(dif)
# u16/u32 표: 연속 값 차이가 dif 와 같은 곳
for w, fmt in ((2, '>H'), (4, '>I')):
    n = len(d) // w; v = struct.unpack('>%d%s' % (n, fmt[1]), d[:n * w])
    for i in range(n - 8):
        if all(v[i + j + 1] - v[i + j] == dif[j] for j in range(6)): print('표', w, hex(i * w), [hex(x) for x in v[i:i + 6]])
print(d[0x19FF0:0x1A040].hex(' '))
print(d[0x5BB20:0x5BB48].hex(' ')); print(d[0x7D730:0x7D740].hex(' '))
