# -*- coding: utf-8 -*-
"""스테이트 VDP2 VRAM 칸 → 디스크 파일 출처 + DC 그림 모음(읽기 전용).  python tools/vdp2_scan.py"""
import sys, os, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate, sprite_scan as SS
from iso9660 import Iso
import numpy as np
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8')
tile = collections.defaultdict(set)
for f in sorted(glob.glob('work/states/*.state')) + sorted(glob.glob('work/states_sf/*.state')):
    try: s, v = mstate.load(f)
    except Exception: continue
    o, n = v['VDP2/VRAM']; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; b = bytes(b)
    for i in range(0, len(b), 32):
        t = b[i:i + 32]
        if len(set(t)) >= 6: tile[t].add(os.path.basename(f))
print('칸', len(tile), flush=True)
for pat, tag in ((r'\*Koutetsu*', '본편'), (r'\*Sakusen*', '작전')):
    p = glob.glob(SS.B + pat)[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); c = collections.Counter()
    for f in iso.walk():
        if f[0].endswith(('.MUS', '.CPK', '/')) or f[2] < 64 or f[0].startswith('/CDDA') or 'UNIT3D' in f[0]: continue
        try: d = iso.read(f[1], f[2])
        except EOFError: continue
        for a in (0, 4, 8, 12, 16, 20, 24, 28):
            for i in range(a, len(d) - 32, 32):
                if d[i:i + 32] in tile: c[f[0]] += 1
    print(tag, c.most_common(24), flush=True)
    dcs = sorted((f for f in iso.walk() if f[0].endswith('.DC')), key=lambda f: f[0]); cols = 5; CW, CH = 320, 204
    pg = Image.new('RGB', (cols * CW, ((len(dcs) + cols - 1) // cols) * CH)); dr = ImageDraw.Draw(pg)
    for i, f in enumerate(dcs):
        d = iso.read(f[1], f[2]); n = len(d) // 2; a = np.frombuffer(d[:n * 2], '>u2'); W = 352; H = n // W
        if H == 0: continue
        a = a[:W * H]; im = np.stack([(a & 31) << 3, (a >> 5 & 31) << 3, (a >> 10 & 31) << 3], 1).reshape(H, W, 3).astype(np.uint8)
        x, y = i % cols * CW, i // cols * CH; pg.paste(Image.fromarray(im).resize((CW - 2, CH - 2)), (x, y)); dr.text((x + 2, y + 2), '%s %d' % (f[0][1:], f[2]), fill=(255, 255, 0))
    pg.save('work/view/dc_%s.png' % ('k' if tag == '본편' else 'f'))
