# -*- coding: utf-8 -*-
"""VDP1 명령표 판독 + 스프라이트 그려 보기(읽기 전용).  python tools/vdp1.py 스테이트 [출력 이름]"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate
import numpy as np
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8')
s, v = mstate.load(sys.argv[1]); nm = sys.argv[2] if len(sys.argv) > 2 else 'v1'
o, n = v['VDP1/VRAM']; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; vram = bytes(b)   # u16 호스트 순서 → 빅엔디언
print(vram[:32].hex(' '))
p = 0; seen = set(); rows = []; pal = None
for i in range(4000):
    if p in seen: break
    seen.add(p)
    c = struct.unpack_from('>16H', vram, p)
    ctrl, link, mode, col, src, size = c[0:6]; xa, ya = [(x ^ 0x8000) - 0x8000 for x in c[6:8]]
    jp = ctrl >> 12 & 7; cm = ctrl & 15
    if ctrl & 0x8000: break
    if not ctrl & 0x4000:
        rows.append((p, cm, mode >> 3 & 7, col, src * 8, (size >> 8) * 8, size & 255, xa, ya, [(x ^ 0x8000) - 0x8000 for x in c[8:10]]))
    nx = p + 32
    if jp == 1: nx = link * 8
    elif jp == 2: nx = link * 8
    p = nx
print('명령', len(rows))
for r in rows[:70]: print('%05X 종류%d 색%d col=%04X src=%05X %dx%d x=%d y=%d %s' % r)
os.makedirs('work/view', exist_ok=True)
pg = Image.new('L', (1500, 1000), 40); x = y = 4; hh = 0
d = ImageDraw.Draw(pg)
for r in rows:
    p0, cm, m, col, src, w, h, xa, ya, xc = r
    if cm not in (0, 1) or w == 0 or h == 0 or w * h > 90000: continue
    bits = {0: 4, 1: 4, 2: 8, 3: 8, 4: 8, 5: 16}.get(m, 4)
    if bits == 4:
        a = np.frombuffer(vram[src:src + w * h // 2], np.uint8); pxl = np.stack([a >> 4, a & 15], 1).reshape(-1) * 17
    elif bits == 8:
        pxl = np.frombuffer(vram[src:src + w * h], np.uint8)
    else:
        a = np.frombuffer(vram[src:src + w * h * 2], '>u2'); pxl = ((a >> 5 & 31) << 3).astype(np.uint8)
    if len(pxl) < w * h: continue
    im = Image.fromarray(pxl[:w * h].reshape(h, w).astype(np.uint8))
    if x + w + 6 > 1500: x = 4; y += hh + 16; hh = 0
    if y + h > 990: break
    pg.paste(im, (x, y + 11)); d.text((x, y), '%X' % p0, fill=255); x += max(w, 40) + 6; hh = max(hh, h)
pg.save('work/view/%s.png' % nm)
