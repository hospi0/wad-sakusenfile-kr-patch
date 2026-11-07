# -*- coding: utf-8 -*-
"""ASC 글꼴 1,192자 판독 + 시트(읽기 전용).  python tools/asc_ocr.py"""
import sys, os, glob, struct, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS
from iso9660 import Iso
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.stdout.reconfigure(encoding='utf-8')
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); fs = iso.walk(); ent = {f[0]: f for f in fs}
rd = lambda n: iso.read(*ent[n][1:3])
mp = rd('/VIEWCG/ASC16MAP.BIN'); cg = rd('/VIEWCG/ASC16X16.BIN') + rd('/VIEWCG/ASC16_2.BIN')
w = struct.unpack('>%dH' % (len(mp) // 2), mp); N = len(w) // 4
def glyph(i):
    o = np.zeros((16, 16), np.uint8)
    for k, t in enumerate(w[i * 4:i * 4 + 4]):
        a = np.frombuffer(cg[(t - 0x800) * 32:(t - 0x800) * 32 + 32], np.uint8)
        c = np.stack([a >> 4, a & 15], 1).reshape(8, 8); o[k // 2 * 8:k // 2 * 8 + 8, k % 2 * 8:k % 2 * 8 + 8] = c
    return o
G = [glyph(i) for i in range(N)]
print(sorted({int(x) for g in G[:300] for x in g.ravel()}))
chars = []
for hi in list(range(0x81, 0x85)) + list(range(0x88, 0xA0)) + list(range(0xE0, 0xEB)):
    for lo in range(0x40, 0xFD):
        if lo == 0x7F: continue
        try: chars.append(bytes([hi, lo]).decode('cp932'))
        except UnicodeDecodeError: pass
chars = [c for c in chars if '\u3041' <= c <= '\u30fe' or '\u4e00' <= c <= '\u9fff' or c in '、。・：？！「」『』（）ー…％０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ']
def GF(r):
    m = r.max() or 1
    return np.asarray(Image.fromarray((r / m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1)), np.float32)
def box(a, thr):
    ys, xs = np.nonzero(a > thr)
    if len(ys) == 0: return np.zeros((24, 24), np.float32)
    c = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.float32); h, w_ = c.shape; S = max(h, w_)
    q = np.zeros((S, S), np.float32); q[(S - h) // 2:(S - h) // 2 + h, (S - w_) // 2:(S - w_) // 2 + w_] = c
    r = GF(np.asarray(Image.fromarray(q).resize((24, 24), Image.BILINEAR))); r = r - r.mean(); return r / (np.linalg.norm(r) + 1e-6)
refs = []
for fn in (r'C:\Windows\Fonts\msgothic.ttc', r'C:\Windows\Fonts\YuGothB.ttc', r'C:\Windows\Fonts\msmincho.ttc'):
    T = ImageFont.truetype(fn, 48); A = np.zeros((len(chars), 576), np.float32)
    for i, c in enumerate(chars):
        im = Image.new('L', (64, 64)); ImageDraw.Draw(im).text((8, 2), c, font=T, fill=255); A[i] = box(np.array(im), 96).ravel()
    refs.append(A)
out = []
for g in G:
    q = box(g.astype(np.float32) * (g >= 3), 3).ravel(); b = np.max([A @ q for A in refs], 0); o = np.argsort(-b)[:2]
    out.append((chars[o[0]], float(b[o[0]]), chars[o[1]]))
with open('work/text/asc_glyph.tsv', 'w', encoding='utf-8', newline='\n') as f:
    for i, r in enumerate(out): f.write('%d\t%s\t%.3f\t%s\n' % (i, r[0], r[1], r[2]))
T = ImageFont.truetype(r'C:\Windows\Fonts\msgothic.ttc', 18); Nn = ImageFont.truetype(r'C:\Windows\Fonts\msgothic.ttc', 11)
W = 25; per = W * 12; CW, CH = 54, 78
for s in range(0, N, per):
    pg = Image.new('RGB', (W * CW, 12 * CH), (30, 30, 40)); d = ImageDraw.Draw(pg)
    for j, i in enumerate(range(s, min(N, s + per))):
        x, y = j % W * CW, j // W * CH
        pg.paste(Image.fromarray((G[i] * 17).astype(np.uint8)).resize((48, 48), 0).convert('RGB'), (x + 2, y + 2))
        d.text((x + 2, y + 52), out[i][0], font=T, fill=(255, 220, 90)); d.text((x + 22, y + 58), str(i), font=Nn, fill=(150, 220, 255))
    pg.save('work/view/asc_%d.png' % (s // per))
print('끝', N)
