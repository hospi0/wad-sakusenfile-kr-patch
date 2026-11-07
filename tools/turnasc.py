# -*- coding: utf-8 -*-
"""TURNASC 글꼴 풀기 + 문자열 찾기(읽기 전용)."""
import sys, os, glob, struct, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, asc_table
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); fs = iso.walk(); ent = {f[0]: f for f in iso.walk()}
rd = lambda n: iso.read(*ent[n][1:3])
mp = rd('/VIEWCG/ASC16MAP.BIN'); cg = rd('/VIEWCG/ASC16X16.BIN') + rd('/VIEWCG/ASC16_2.BIN')
w = struct.unpack('>%dH' % (len(mp) // 2), mp); G = {}
for i in range(len(w) // 4):
    g = b''.join(cg[(t - 0x800) * 32:(t - 0x800) * 32 + 32] for t in w[i * 4:i * 4 + 4]); G.setdefault(g, asc_table.SHEET[i])
t = rd('/TURNASC.BIN'); n = len(t) // 128
L = [G.get(t[i * 128:i * 128 + 128], '?') for i in range(n)]
print(n, ''.join(L))
for key, nm in ((struct.pack('>3H', 0x72, 0x73, 0x74), '累積度'), (struct.pack('>2H', 0x7B, 0x7C), '通常')):
    r = []
    for f in fs:
        if f[0].endswith(('.MUS', '.CPK', '/', '.EP')) or f[2] < 16 or f[0].startswith('/CDDA') or 'UNIT3D' in f[0]: continue
        try: d = iso.read(f[1], f[2])
        except EOFError: continue
        for m in re.finditer(re.escape(key), d): r.append((f[0], hex(m.start())))
    print(nm, len(r), r[:12])

print('=== 시작 번호열')
for st in (1, 8, 20):
    key = struct.pack('>6H', *range(st, st + 6))
    for f in fs:
        if f[0].endswith(('.MUS', '.CPK', '/', '.EP')) or f[2] < 16 or f[0].startswith('/CDDA') or 'UNIT3D' in f[0]: continue
        try: d = iso.read(f[1], f[2])
        except EOFError: continue
        o = d.find(key)
        if o >= 0:
            print(st, f[0], hex(o))
            if f[0] in ('/TURNASC.BIN',): continue
            a = o - 40; v = struct.unpack('>%dH' % 300, d[a:a + 600])
            print(''.join((L[x] if x < n else '|' if x == 0xFFFF else '<%X>' % x) for x in v))

print('=== 구역')
d = rd('/GAME2.BIN'); a = 0x5D800; n2 = 700
v = struct.unpack('>%dH' % n2, d[a:a + n2 * 2])
print(''.join((L[x] if x < n else '|' if x == 0xFFFF else '/' if x == 0xFFFE else '<%X>' % x) for x in v))
import numpy as np
from PIL import Image, ImageDraw, ImageFont
un = [i for i in range(n) if L[i] == '?']
N = ImageFont.truetype(r'C:\Windows\Fonts\msgothic.ttc', 12)
pg = Image.new('L', (12 * 64, ((len(un) + 11) // 12) * 66), 20); dr = ImageDraw.Draw(pg)
for j, i in enumerate(un):
    b = np.frombuffer(t[i * 128:i * 128 + 128], np.uint8); q = np.stack([b >> 4, b & 15], 1).reshape(4, 8, 8); o = np.zeros((16, 16), np.uint8)
    o[:8, :8], o[:8, 8:], o[8:, :8], o[8:, 8:] = q
    x, y = j % 12 * 64, j // 12 * 66; pg.paste(Image.fromarray(o * 17).resize((48, 48), 0), (x + 2, y + 2)); dr.text((x + 4, y + 52), str(i), font=N, fill=200)
pg.save('work/view/turn_un.png'); print(un)
