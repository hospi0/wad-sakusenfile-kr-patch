# -*- coding: utf-8 -*-
"""그림 글자 한글화 1차: 작전 버튼·나라 이름판·인구/국력/병력(8비트 색번호 그림).  python tools/gfx_kr.py 폴더
  결과 폴더/preview.png(왼쪽 원본, 오른쪽 새것, 실제 색) · 폴더/*.bin(색번호 그대로). 디스크는 안 건드림."""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate, bdf
from iso9660 import Iso
import numpy as np
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\claude\roms\ss\World Advanced Daisenryaku'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'work/gfx/v2'; os.makedirs(OUT, exist_ok=True)
iso = Iso(glob.glob(glob.glob(B + r'\*Koutetsu*')[0] + r'\*(Track 1).bin')[0]); ent = {f[0]: f for f in iso.walk()}
G14 = bdf.Font(r'C:\claude\utils\font\Galmuri-v2.40.3\Galmuri14.bdf')
G11 = bdf.Font(r'C:\claude\utils\font\Galmuri-v2.40.3\Galmuri11.bdf')


def cram(st):
    s, v = mstate.load('work/states/%s.state' % st)
    k = 'VDP2/CRAM' if 'VDP2/CRAM' in v else max((x for x in v if 'CRAM' in x), key=lambda x: v[x][1]); o, n = v[k]; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]
    return np.frombuffer(bytes(b), '>u2').astype(int)


def to_rgb(a, c, bank):
    v = c[(a.astype(int) + bank) & 0x7FF]
    return np.stack([(v & 31) << 3, (v >> 5 & 31) << 3, (v >> 10 & 31) << 3], 2).astype(np.uint8)


def nearest(c, bank, used, rgb):
    best, bd = None, 1e9
    for i in used:
        v = int(c[(int(i) + bank) & 0x7FF]); p = ((v & 31) << 3, (v >> 5 & 31) << 3, (v >> 10 & 31) << 3)
        d = sum((x - y) ** 2 for x, y in zip(p, rgb))
        if d < bd: best, bd = int(i), d
    return best


def text_mask(t, w, h, font=None):
    pts, tw = (font or G14).draw(t)
    m = np.zeros((h, w), bool)
    if not pts: return m
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    ox = (w - (max(xs) - min(xs) + 1)) // 2 - min(xs); oy = (h - (max(ys) - min(ys) + 1)) // 2 - min(ys)
    for x, y in pts:
        if 0 <= x + ox < w and 0 <= y + oy < h: m[y + oy, x + ox] = True
    return m


def emboss(a, box, t, ink, hi, face, rowbg=None, bold=False, font=None, mid=None):
    mid = ink if mid is None else mid
    """box 안을 행별 바탕으로 메우고, 글자(ink)와 오른쪽 아래 밝은 그림자(hi)."""
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        if rowbg is None:
            edge = np.concatenate([a[y, max(0, x0 - 3):x0], a[y, x1:x1 + 3]])
            v = np.bincount(edge).argmax() if len(edge) else a[y, x0]
        else: v = rowbg[y]
        if x0 <= 1 and rowbg is None:                 # 버튼: 왼쪽 끝 두 칸 무늬(바둑판 디더)를 이어 붙임
            for x in range(x0, x1): a[y, x] = a[y, x % 2]
        else: a[y, x0:x1] = v
    m = text_mask(t, x1 - x0, y1 - y0, font)
    if bold:
        m2 = m.copy(); m2[:, 1:] |= m[:, :-1]; m = m2
    sh = np.zeros_like(m); sh[1:, 1:] = m[:-1, :-1]
    tl = np.zeros_like(m); tl[:-1, :-1] = m[1:, 1:]
    sh2 = np.zeros_like(m); sh2[1:, :] |= m[:-1, :]; sh2[:, 1:] |= m[:, :-1]      # 오른쪽·아래 그림자
    r = a[y0:y1, x0:x1]; r[sh] = ink; r[m] = face


JOB = []
BT = [(0x78F0, '작전정보'), (0x7CF0, '진영정보'), (0x80F0, '승리조건'), (0x84F0, '작전명령'), (0x88F0, '세력정보'), (0x8CF0, '중요거점'), (0x90F0, '진격경로'), (0x94F0, '돌아가기'), (0x98F0, '종료')]
c28 = cram('28'); c25 = cram('25')
dt = iso.read(*ent['/SAKUSEN/SAKU_DT.BIN'][1:3]); g = iso.read(*ent['/GMS2.BIN'][1:3])
rows = []
for o, t in BT:
    a = np.frombuffer(dt[o:o + 1024], np.uint8).reshape(16, 64).copy(); src = a.copy(); u = np.unique(a)
    ink = nearest(c28, 0x200, u, (0, 0, 0)); hi = nearest(c28, 0x200, u, (255, 255, 255))
    emboss(a, (1, 0, 64, 16), t, ink, hi, nearest(c28, 0x200, u, (235, 240, 240)), mid=nearest(c28, 0x200, u, (60, 70, 70))); a.tofile('%s/DT_%X.bin' % (OUT, o)); rows.append((src, a, c28, 0x200, t))
PL = [(0x26D26, '독일 제3제국'), (0x28E26, '대일본제국'), (0x2AF26, '미합중국')]
for o, t in PL:
    bank = 0x500 if o == 0x26D26 else 0x600
    a = np.frombuffer(g[o:o + 96 * 88], np.uint8).reshape(88, 96).copy(); src = a.copy(); r = a[68:86]; u = np.unique(r)
    ink = nearest(c25, bank, u, (0, 0, 0)); hi = nearest(c25, bank, u, (255, 255, 255))
    emboss(a, (3, 69, 93, 86), t, ink, hi, nearest(c25, bank, u, (235, 240, 240)), mid=nearest(c25, bank, u, (60, 70, 70))); a.tofile('%s/GMS2_%X.bin' % (OUT, o)); rows.append((src, a, c25, bank, t))
o = 0x2E6E6; a = np.frombuffer(g[o:o + 128 * 32], np.uint8).reshape(32, 128).copy(); src = a.copy(); u = np.unique(a[8:26])
ink = nearest(c25, 0x500, u, (0, 0, 0)); hi = nearest(c25, 0x500, u, (255, 255, 255))
rb = [int(a[y, 42]) for y in range(32)]       # 글자·막대 없는 열: 판 세로 그라데이션 그대로
for box, t in (((12, 6, 42, 22), '인구'), ((50, 6, 82, 22), '국력'), ((90, 6, 122, 22), '병력')): emboss(a, box, t, ink, hi, nearest(c25, 0x500, u, (165, 178, 172)), rb, mid=nearest(c25, 0x500, u, (60, 70, 70)))
a.tofile('%s/GMS2_%X.bin' % (OUT, o)); rows.append((src, a, c25, 0x500, '인구 국력 병력'))
S = 3; H = sum(r[0].shape[0] * S + 6 for r in rows); W = 2 * 128 * S + 30
pg = Image.new('RGB', (W, H), (40, 40, 60)); y = 0
for src, a, c, bank, t in rows:
    for i, x in enumerate((src, a)):
        im = Image.fromarray(to_rgb(x, c, bank)); pg.paste(im.resize((im.width * S, im.height * S), 0), (i * (128 * S + 20) + 4, y))
    y += src.shape[0] * S + 6
pg.save(OUT + '/preview.png'); print(pg.size)
