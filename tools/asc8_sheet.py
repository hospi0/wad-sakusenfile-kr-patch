# -*- coding: utf-8 -*-
"""ASC8X8 칸 번호 시트 + 유닛 레코드 덤프(읽기 전용)."""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS
from iso9660 import Iso
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.stdout.reconfigure(encoding='utf-8')
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); ent = {f[0]: f for f in iso.walk()}
d = iso.read(*ent['/VIEWCG/ASC8X8.BIN'][1:3]); n = len(d) // 32
N = ImageFont.truetype(r'C:\Windows\Fonts\msgothic.ttc', 11); W = 24; CW, CH = 56, 62
pg = Image.new('RGB', (W * CW, ((n + W - 1) // W) * CH), (30, 30, 40)); dr = ImageDraw.Draw(pg)
for i in range(n):
    a = np.frombuffer(d[i * 32:i * 32 + 32], np.uint8); q = (np.stack([a >> 4, a & 15], 1).reshape(8, 8) * 17).astype(np.uint8)
    x, y = i % W * CW, i // W * CH; pg.paste(Image.fromarray(q).resize((48, 48), 0).convert('RGB'), (x + 2, y + 2)); dr.text((x + 4, y + 50), '%02X' % i, font=N, fill=(150, 220, 255))
pg.save('work/view/asc8_sheet.png'); print(n)
u = iso.read(*ent['/UNITPACK/UPK02C.BIN'][1:3]); print(len(u))
print(u[:0x40].hex(' ')); print(u[0x340:0x3C0].hex(' '))
