# -*- coding: utf-8 -*-
"""SAKU_F 고유 글자 판독 + SAKU_DT 문장 풀기(읽기 전용). cyberdoll tools/ocrmap.py 방식.
  python tools/wad_ocr.py → work/text/glyph_sf.tsv(해시·문자·점수·2등), work/text/saku_raw.txt"""
import sys, os, glob, struct, collections, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso9660 import Iso
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\claude\roms\ss\World Advanced Daisenryaku'
R2 = glob.glob(B + r'\*Sakusen*')[0]
iso = Iso(sorted(glob.glob(R2 + r'\*.bin'))[0]); fs = iso.walk(); ent = {f[0]: f for f in fs}
F = {}
for f in sorted(fs):
    if '/SAK_F' in f[0]:
        b = iso.read(f[1], f[2]); F[int(f[0][-7:-4])] = [b[i:i + 128] for i in range(0, len(b), 128)]

def px(g):
    a = np.frombuffer(g, np.uint8); p = np.stack([a >> 4, a & 15], 1).reshape(4, 8, 8)
    o = np.zeros((16, 16), np.uint8)
    o[:8, :8], o[:8, 8:], o[8:, :8], o[8:, 8:] = p
    return o

TH = int(sys.argv[1]) if len(sys.argv) > 1 else 7
U = list(dict.fromkeys(g for k in F for g in F[k]))
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
with open('work/text/glyph_sf.tsv', 'w', encoding='utf-8', newline='\n') as f:
    for r in out: f.write('%s\t%s\t%.3f\t%s\t%.3f\t%s\n' % r)
print('끝')
