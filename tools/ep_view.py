# -*- coding: utf-8 -*-
"""엔딩 EP 그림 모아 보기(읽기 전용).  python tools/ep_view.py"""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso9660 import Iso
import numpy as np
from PIL import Image, ImageDraw
B = r'C:\claude\roms\ss\World Advanced Daisenryaku'
iso = Iso(glob.glob(glob.glob(B + r'\*Koutetsu*')[0] + r'\*(Track 1).bin')[0]); fs = iso.walk()
eps = sorted((f for f in fs if f[0].endswith('.EP')), key=lambda f: f[0])
W = int(sys.argv[1]) if len(sys.argv) > 1 else 352
H = 236544 // W; cols = 5; CW, CH = 320, int(320 * H / W)
pg = Image.new('RGB', (cols * CW, ((len(eps) + cols - 1) // cols) * CH)); d = ImageDraw.Draw(pg)
for i, f in enumerate(eps):
    b = iso.read(f[1], f[2]); a = np.frombuffer(b, '>u2')[:W * H]
    im = np.stack([(a & 31) << 3, (a >> 5 & 31) << 3, (a >> 10 & 31) << 3], 1).reshape(H, W, 3).astype(np.uint8)
    t = Image.fromarray(im).resize((CW - 2, CH - 2)); x, y = i % cols * CW, i // cols * CH; pg.paste(t, (x, y)); d.text((x + 2, y + 2), f[0][1:], fill=(255, 255, 0))
pg.save('work/view/ep_sheet.png'); print(pg.size)
