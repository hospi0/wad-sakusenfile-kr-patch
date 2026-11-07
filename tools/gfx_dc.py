# -*- coding: utf-8 -*-
"""16비트 화면 그림 한글화(DAI_TXT·DAI_MOV·DAI_MES·DAI_TIT1).  python tools/gfx_dc.py 폴더
  폴더/preview.png(왼쪽 원본, 오른쪽 새것), 폴더/*.bin. 디스크는 안 건드림."""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso9660 import Iso
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\claude\roms\ss\World Advanced Daisenryaku'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'work/gfx/d1'; os.makedirs(OUT, exist_ok=True)
iso = Iso(glob.glob(glob.glob(B + r'\*Koutetsu*')[0] + r'\*(Track 1).bin')[0]); ent = {f[0]: f for f in iso.walk()}
FD = r'C:\claude\utils\font'
MJ = glob.glob(FD + r'\nanum-myeongjo\*ExtraBold*.ttf') + glob.glob(FD + r'\nanum-myeongjo\*.ttf')
BH = glob.glob(FD + r'\blackhansans\*.ttf')
GB = FD + r'\nanum-gothic\NanumGothicBold.ttf'


def load(n, o, w, h):
    d = iso.read(*ent[n][1:3]); a = np.frombuffer(d[o:o + w * h * 2], '>u2').reshape(h, w)
    return np.stack([(a & 31) << 3, (a >> 5 & 31) << 3, (a >> 10 & 31) << 3], 2).astype(np.float32), (a & 0x8000)


def pack(rgb, msb):
    r = np.clip(rgb, 0, 255).astype(np.uint16) >> 3
    return (msb | r[:, :, 0] | r[:, :, 1] << 5 | r[:, :, 2] << 10).astype('>u2').tobytes()


def inpaint(rgb, mask, it=120):
    a = rgb.copy(); known = ~mask
    a[mask] = 0
    for _ in range(it):
        s = np.zeros_like(a); c = np.zeros(mask.shape, np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            s += np.roll(np.roll(a * known[..., None], dy, 0), dx, 1); c += np.roll(np.roll(known.astype(np.float32), dy, 0), dx, 1)
        new = (c > 0) & ~known
        a[new] = s[new] / c[new][:, None]; known = known | new
        if known.all(): break
    return a


def dil(m, n):
    m = m.copy()
    for _ in range(n):
        q = m.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)): q |= np.roll(np.roll(m, dy, 0), dx, 1)
        m = q
    return m


def draw(rgb, items):
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)); 
    for t, xy, font, size, fill, stroke, sw, glow in items:
        f = ImageFont.truetype(font, size)
        if glow:
            g = Image.new('L', im.size, 0); ImageDraw.Draw(g).text(xy, t, 255, font=f, anchor='mm', stroke_width=1, stroke_fill=255)
            g = g.filter(ImageFilter.GaussianBlur(glow[1])); im.paste(Image.new('RGB', im.size, glow[0]), (0, 0), g)
        ImageDraw.Draw(im).text(xy, t, fill, font=f, anchor='mm', stroke_width=sw, stroke_fill=stroke)
    return np.asarray(im, np.float32)


rows = []
# 자료 제공 / 영상 제공: 위 띠의 붉은 글자
for n, t in (('/DAI_TXT.DC', '자료 제공'), ('/DAI_MOV.DC', '영상 제공')):
    rgb, msb = load(n, 0, 352, 224); src = rgb.copy()
    X0, X1, Y0, Y1 = 26, 178, 12, 48
    base = rgb.copy(); tt = np.linspace(0, 1, X1 - X0)[None, :, None]
    base[Y0:Y1, X0:X1] = rgb[Y0:Y1, X0 - 1:X0] * (1 - tt) + rgb[Y0:Y1, X1:X1 + 1] * tt
    m = np.zeros((224, 352), bool); m[Y0:Y1, X0:X1] = np.abs(rgb[Y0:Y1, X0:X1] - base[Y0:Y1, X0:X1]).sum(2) > 60
    m = dil(m, 2); m[:Y0] = False; m[Y1:] = False
    new = rgb.copy(); new[m] = base[m]
    col = (175, 60, 50)
    new = draw(new, [(t, (92, 33), GB, 25, col, (240, 235, 228), 1, None)])
    open('%s/%s.bin' % (OUT, n[1:-3]), 'wb').write(pack(new, msb)); rows.append((src, new))
# 이 비극이…
rgb, msb = load('/DAI_MES.DC', 0, 352, 224); src = rgb.copy()
box = np.zeros((224, 352), bool); box[76:103, 14:220] = True; box[126:156, 14:338] = True
m = box & (rgb.sum(2) > 450); m = dil(m, 4); m |= np.roll(np.roll(m, 2, 0), 2, 1)
new = inpaint(rgb, m)
W = (235, 232, 225)
D = (28, 22, 18)
new = draw(new, [('이 비극이 두 번 다시', (138, 90), GB, 23, D, D, 0, None), ('되풀이되지 않기를 바라며', (162, 140), GB, 23, D, D, 0, None)])
new = draw(new, [('이 비극이 두 번 다시', (136, 88), GB, 23, W, W, 0, None), ('되풀이되지 않기를 바라며', (160, 138), GB, 23, W, W, 0, None)])
open(OUT + '/DAI_MES.bin', 'wb').write(pack(new, msb)); rows.append((src, new))
# 제목 띠
rgb, msb = load('/DAI_TIT1.DC', 0x200, 312, 28); src = rgb.copy()
r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
m = np.zeros((28, 312), bool); m[:, 70:250] = (r[:, 70:250] < 120) | (g[:, 70:250] < r[:, 70:250] * 0.45); m = dil(m, 1)
new = inpaint(rgb, m)
new = draw(new, [('강철의 전풍', (156, 15), BH[0], 25, (58, 8, 4), (58, 8, 4), 0, None)])
open(OUT + '/DAI_TIT1.bin', 'wb').write(pack(new, msb)); rows.append((src, new))
S = 2; H = sum(r[0].shape[0] * S + 8 for r in rows); pg = Image.new('RGB', (2 * 352 * S + 20, H), (30, 30, 40)); y = 0
for a, b in rows:
    for i, x in enumerate((a, b)):
        im = Image.fromarray(np.clip(x, 0, 255).astype(np.uint8)); pg.paste(im.resize((im.width * S, im.height * S), 0), (i * (352 * S + 20), y))
    y += a.shape[0] * S + 8
pg.save(OUT + '/preview.png'); print(pg.size)
