# -*- coding: utf-8 -*-
"""SAKU_F 고유 글자 판독 + SAKU_DT 문장 풀기(읽기 전용). cyberdoll tools/ocrmap.py 방식.
  python tools/wad_ocr.py → work/text/glyph.tsv(해시·문자·점수·2등), work/text/saku_raw.txt"""
import sys, os, glob, struct, collections, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso9660 import Iso
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.stdout.reconfigure(encoding='utf-8')
R = r'C:\claude\roms\ss\World Advanced Daisenryaku\World Advanced Daisenryaku - Koutetsu no Senpuu (Japan) (Rev A) (10M)'
iso = Iso(glob.glob(R + r'\*(Track 1).bin')[0]); fs = iso.walk(); ent = {f[0]: f for f in fs}
d = iso.read(*ent['/SAKUSEN/SAKU_DT.BIN'][1:3])
F = {}
for k in range(1, 55):
    b = iso.read(*ent['/SAKUSEN/SAKU_F%02d.BIN' % k][1:3]); F[k] = [b[i:i + 128] for i in range(0, len(b), 128)]

def px(g):
    a = np.frombuffer(g, np.uint8); p = np.stack([a >> 4, a & 15], 1).reshape(4, 8, 8)
    o = np.zeros((16, 16), np.uint8)
    o[:8, :8], o[:8, 8:], o[8:, :8], o[8:, 8:] = p
    return o

TH = int(sys.argv[1]) if len(sys.argv) > 1 else 7
U = list(dict.fromkeys(g for k in F for g in F[k]))
for r in px(U[40]): print(''.join('%X' % v if v else '.' for v in r))
print('고유', len(U), '색', collections.Counter(int(v) for g in U[:200] for v in px(g).ravel()).most_common(8))
ink = max(collections.Counter(int(v) for g in U[:200] for v in px(g).ravel() if v), key=lambda c: collections.Counter(int(v) for g in U[:200] for v in px(g).ravel())[c])
print('주 색', ink)
chars = []
for hi in list(range(0x81, 0x85)) + list(range(0x88, 0xA0)) + list(range(0xE0, 0xEB)):
    for lo in range(0x40, 0xFD):
        if lo == 0x7F: continue
        try: chars.append(bytes([hi, lo]).decode('cp932'))
        except UnicodeDecodeError: pass
from PIL import ImageFilter
def GF(r, _):
    m = r.max() or 1
    return np.asarray(Image.fromarray((r / m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1)), np.float32)
def box(a, thr):
    ys, xs = np.nonzero(a > thr)
    if len(ys) == 0: return np.zeros((24, 24), np.float32)
    c = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.float32)
    h, w_ = c.shape; S_ = max(h, w_)
    q = np.zeros((S_, S_), np.float32); q[(S_ - h) // 2:(S_ - h) // 2 + h, (S_ - w_) // 2:(S_ - w_) // 2 + w_] = c
    r = np.asarray(Image.fromarray(q).resize((24, 24), Image.BILINEAR))
    r = GF(r, 1.0); r = r - r.mean(); return r / (np.linalg.norm(r) + 1e-6)
chars = [c for c in chars if 'ぁ' <= c <= 'ヾ' or '一' <= c <= '鿿' or c in '、。，．・：？！「」『』（）〔〕―ー…％０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ']
refs = []
for fn, ix in ((r'C:\Windows\Fonts\msgothic.ttc', 0), (r'C:\Windows\Fonts\meiryob.ttc', 0), (r'C:\Windows\Fonts\YuGothB.ttc', 0), (r'C:\Windows\Fonts\msmincho.ttc', 0)):
    if not os.path.exists(fn): print('없음', fn); continue
    T = ImageFont.truetype(fn, 48, index=ix); A = np.zeros((len(chars), 576), np.float32)
    for i, c in enumerate(chars):
        im = Image.new('L', (64, 64)); ImageDraw.Draw(im).text((8, 2), c, font=T, fill=255); A[i] = box(np.array(im), 96).ravel()
    refs.append(A)
print('후보', len(chars), '글꼴', len(refs))
out = []
for g in U:
    q = box(px(g).astype(np.float32) * (px(g) >= 3), 3).ravel(); best = np.max([A @ q for A in refs], 0)
    o = np.argsort(-best)[:3]
    out.append((hashlib.md5(g).hexdigest()[:10], chars[o[0]], float(best[o[0]]), chars[o[1]], float(best[o[1]]), chars[o[2]]))
os.makedirs('work/text', exist_ok=True)
with open('work/text/glyph.tsv', 'w', encoding='utf-8', newline='\n') as f:
    for r in out: f.write('%s\t%s\t%.3f\t%s\t%.3f\t%s\n' % r)
gm = {g: r[1] for g, r in zip(U, out)}
print('점수 분포', np.histogram([r[2] for r in out], bins=[0, .5, .6, .7, .8, .9, 1.01])[0])
# 시트
S = 3; W = 40; H = (len(U) + W - 1) // W
sh = Image.new('L', (W * 18 * S, H * 18 * S), 0)
for i, g in enumerate(U):
    im = Image.fromarray((px(g) * 17).astype(np.uint8)).resize((16 * S, 16 * S), 0); sh.paste(im, (i % W * 18 * S, i // W * 18 * S))
sh.save('work/view/glyphs.png')
n = len(d) // 2; w = struct.unpack('>%dH' % n, d[:n * 2])
res = []; s = None; i0 = 0x17E98 // 2
for i in range(i0, n):
    x = w[i]
    if x == 0xFFFF:
        if s is not None: res.append((s * 2, w[s:i]))
        s = i + 1
    elif s is None: s = i
sc = 0; mx = -1; L = []
for o, ids in res:
    v = [x for x in ids if x < 0x100]
    if sc < 53 and 32 in v[:3] and mx + 1 >= len(F[sc + 1]) - 3:
        sc += 1; mx = -1
    k = min(sc + 1, 54)
    if v: mx = max(mx, max(v))
    t = ''.join(gm.get(F[k][x], '?') if x < len(F[k]) else '〓' if x < 0x100 else '<%X>' % x for x in ids)
    L.append('%02d %06X %s' % (k, o, t))
open('work/text/saku_raw.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
print(len(L), '시나리오', sc + 1)
print('\n'.join(L[:14]))
