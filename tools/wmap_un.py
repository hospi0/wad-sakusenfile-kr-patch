# -*- coding: utf-8 -*-
"""연표 글꼴 미판독 칸 시트."""
import sys, os, glob, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, asc_table
from iso9660 import Iso
import numpy as np
from PIL import Image, ImageDraw, ImageFont
pk = glob.glob(SS.B + r'\*Koutetsu*')[0]; ik = Iso(sorted(glob.glob(pk + r'\*(Track 1).bin'))[0]); ek = {f[0]: f for f in ik.walk()}
rk = lambda n: ik.read(*ek[n][1:3])
mp = rk('/VIEWCG/ASC16MAP.BIN'); cg = rk('/VIEWCG/ASC16X16.BIN') + rk('/VIEWCG/ASC16_2.BIN')
w = struct.unpack('>%dH' % (len(mp) // 2), mp); G = {}
for i in range(len(w) // 4):
    g = b''.join(cg[(t - 0x800) * 32:(t - 0x800) * 32 + 32] for t in w[i * 4:i * 4 + 4]); G.setdefault(g, asc_table.SHEET[i])
d = rk('/W_MAP2.BIN'); base = 0x4E128; cnt = 428
un = [i for i in range(cnt) if G.get(d[base + i * 128:base + i * 128 + 128], '□') == '□']
N = ImageFont.truetype(r'C:\Windows\Fonts\msgothic.ttc', 12)
pg = Image.new('L', (16 * 60, ((len(un) + 15) // 16) * 66), 20); dr = ImageDraw.Draw(pg)
for j, i in enumerate(un):
    b = np.frombuffer(d[base + i * 128:base + i * 128 + 128], np.uint8); q = np.stack([b >> 4, b & 15], 1).reshape(4, 8, 8); o = np.zeros((16, 16), np.uint8)
    o[:8, :8], o[:8, 8:], o[8:, :8], o[8:, 8:] = q
    x, y = j % 16 * 60, j // 16 * 66; pg.paste(Image.fromarray(o * 17).resize((48, 48), 0), (x + 2, y + 2)); dr.text((x + 4, y + 52), str(i), font=N, fill=200)
pg.save('work/view/wmap_un.png'); print(len(un), un)
