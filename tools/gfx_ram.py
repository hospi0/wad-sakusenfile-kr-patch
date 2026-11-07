# -*- coding: utf-8 -*-
"""RAM 선택 판 한글화(GMS2 0x35EA6·0x39EA6, 128×128 8비트).  python tools/gfx_ram.py 폴더"""
import sys, os, glob, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate, bdf, sprite_scan as SS
from iso9660 import Iso
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.stdout.reconfigure(encoding='utf-8')
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); ent = {f[0]: f for f in iso.walk()}
g = iso.read(*ent['/GMS2.BIN'][1:3])
s, v = mstate.load('work/states/44.state')
def mem(k):
    o, n = v[k]; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; return bytes(b)
vr = mem('VDP1/VRAM'); c = np.frombuffer(mem('VDP2/CRAM'), '>u2').astype(int)
col = 0
pp = 0; seen = set()
for _ in range(4000):
    if pp in seen: break
    seen.add(pp); q = struct.unpack_from('>16H', vr, pp); ctrl, link, mode, cc, src, size = q[0:6]; jp = ctrl >> 12 & 7
    if ctrl & 0x8000: break
    if not ctrl & 0x4000 and (ctrl & 15) in (0, 1, 2) and size == 0x1080: col = cc
    pp = link * 8 if jp in (1, 2) else pp + 32
bank = col & 0xFF00; print('색', hex(col))
GB = "C:/claude/utils/font/nanum-gothic/NanumGothicBold.ttf"
def rgb(a):
    q = c[(a.astype(int) + bank) & 0x7FF]; return np.stack([(q & 31) << 3, (q >> 5 & 31) << 3, (q >> 10 & 31) << 3], 2).astype(np.uint8)
pg = Image.new('RGB', (2 * 400, 2 * 400), (40, 40, 60))
for k, (o, t) in enumerate(((0x35EA6, '본체 RAM'), (0x39EA6, '카트리지 RAM'))):
    a = np.frombuffer(g[o:o + 0x4000], np.uint8).reshape(128, 128).copy(); src = a.copy()
    y0, y1, x0, x1 = 105, 120, 9, 119
    reg = a[y0:y1, x0:x1]; cnt = collections.Counter(int(x) for x in reg.ravel()); print(cnt.most_common(6))
    bg = cnt.most_common(1)[0][0]
    lum = lambda i: int(rgb(np.array([[i]])).astype(int).sum())
    ink = max((i for i, n in cnt.items() if n >= 20 and i != bg), key=lum); print('바탕', bg, '글자', ink, rgb(np.array([[ink]])).ravel())
    reg[reg != bg] = bg
    # 나눔고딕 볼드를 8배로 그려 줄이고, 원본 글자의 단계 색(바탕→글자)으로 옮긴다
    ramp = sorted([i for i, n in cnt.items() if n >= 10], key=lum); ramp = ramp[ramp.index(bg):]
    lv = np.array([lum(i) for i in ramp], float); lv = (lv - lv[0]) / (lv[-1] - lv[0]); print("단계", ramp, lv.round(2))
    K = 8; SZ = 15; f = ImageFont.truetype(GB, SZ * K); bb = f.getbbox(t)
    W, H = x1 - x0, y1 - y0
    big = Image.new("L", (W * K, H * K), 0); dr = ImageDraw.Draw(big)
    dr.text(((W * K - (bb[2] - bb[0])) // 2 - bb[0], (H * K - (bb[3] - bb[1])) // 2 - bb[1]), t, font=f, fill=255)
    cov = np.asarray(big.resize((W, H), Image.BOX), float) / 255
    print("폭", (bb[2] - bb[0]) / K, "높이", (bb[3] - bb[1]) / K, "안쪽", W, H)
    a[y0:y1, x0:x1] = np.array(ramp, np.uint8)[np.abs(cov[..., None] - lv).argmin(2)]
    a.tofile('%s/GMS2_%X.bin' % (OUT, o))
    for i, q in enumerate((src, a)):
        pg.paste(Image.fromarray(rgb(q)).resize((384, 384), 0), (i * 400 + 8, k * 400 + 8))
pg.save(OUT + '/preview.png')
