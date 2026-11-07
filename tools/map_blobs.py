# -*- coding: utf-8 -*-
"""지도 층 글자 덩어리 찾기·같은 그림 묶기(읽기 전용).  python tools/map_blobs.py
  결과 work/text/map_blobs.tsv(고유번호·디스크·파일·층·x·y·w·h), work/view/blob_N.png"""
import sys, os, glob, collections, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS
from iso9660 import Iso
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.stdout.reconfigure(encoding='utf-8')
INK = 108


def leaders(m):
    """긴 가로·세로 선(지시선)은 글자에서 뺀다."""
    o = np.zeros_like(m)
    for y in range(m.shape[0]):
        x = 0
        while x < m.shape[1]:
            if m[y, x]:
                e = x
                while e < m.shape[1] and m[y, e]: e += 1
                if e - x >= 10: o[y, x:e] = True
                x = e
            else: x += 1
    for x in range(m.shape[1]):
        y = 0
        while y < m.shape[0]:
            if m[y, x]:
                e = y
                while e < m.shape[0] and m[e, x]: e += 1
                if e - y >= 10: o[y:e, x] = True
                y = e
            else: y += 1
    return o


def blobs(L):
    m = L == INK; m = m & ~leaders(m)
    H, W = m.shape; seen = np.zeros_like(m); out = []
    ys, xs = np.nonzero(m)
    for y0, x0 in zip(ys, xs):
        if seen[y0, x0]: continue
        st = [(y0, x0)]; seen[y0, x0] = True; pts = []
        while st:
            y, x = st.pop(); pts.append((y, x))
            for dy in range(-2, 3):
                for dx in range(-7, 8):
                    a, b = y + dy, x + dx
                    if 0 <= a < H and 0 <= b < W and m[a, b] and not seen[a, b]: seen[a, b] = True; st.append((a, b))
        py = [p[0] for p in pts]; px = [p[1] for p in pts]
        if len(pts) >= 6: out.append((min(px), min(py), max(px) + 1, max(py) + 1, pts))
    return out


def main():
    U = collections.OrderedDict(); rows = []
    for pat, tag in ((r'\*Koutetsu*', 'K'), (r'\*Sakusen*', 'F')):
        p = glob.glob(SS.B + pat)[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0])
        for f in sorted((f for f in iso.walk() if '/SAKU_M' in f[0] or '/SAK_M' in f[0]), key=lambda f: f[0]):
            d = iso.read(f[1], f[2]); n = len(d) // 0x4000
            for l in range(n):
                L = np.frombuffer(d[l * 0x4000:(l + 1) * 0x4000], np.uint8).reshape(128, 128)
                for x0, y0, x1, y1, pts in blobs(L):
                    b = np.zeros((y1 - y0, x1 - x0), bool)
                    for y, x in pts: b[y - y0, x - x0] = True
                    k = (b.shape, b.tobytes())
                    if k not in U: U[k] = (len(U), b)
                    rows.append((U[k][0], tag, f[0], l, x0, y0, x1 - x0, y1 - y0))
    with open('work/text/map_blobs.tsv', 'w', encoding='utf-8', newline='\n') as f:
        for r in rows: f.write('\t'.join(map(str, r)) + '\n')
    cnt = collections.Counter(r[0] for r in rows)
    print('덩어리', len(rows), '고유', len(U))
    N = ImageFont.truetype(r'C:\Windows\Fonts\msgothic.ttc', 12)
    items = sorted(U.values(), key=lambda v: v[0]); x = y = 0; pg = None; k = 0; hh = 0
    for i, b in items:
        h, w = b.shape; S = 2
        if pg is None: pg = Image.new('L', (1500, 980), 25); d = ImageDraw.Draw(pg); x = y = 2; hh = 0
        cw = max(w * S, 44) + 8
        if x + cw > 1500: x = 2; y += hh + 18; hh = 0
        if y + h * S + 18 > 980:
            pg.save('work/view/blob_%d.png' % k); k += 1; pg = Image.new('L', (1500, 980), 25); d = ImageDraw.Draw(pg); x = y = 2; hh = 0
        d.text((x, y), '%d' % i, font=N, fill=160)
        pg.paste(Image.fromarray((b * 255).astype(np.uint8)).resize((w * S, h * S), 0), (x, y + 13)); x += cw; hh = max(hh, h * S)
    if pg: pg.save('work/view/blob_%d.png' % k); k += 1
    print('장', k, '작은 조각', sum(1 for i, b in items if b.shape[1] < 8))


if __name__ == '__main__':
    main()


def grid():
    rows = [l.rstrip('\n').split('\t') for l in open('work/text/map_blobs.tsv', encoding='utf-8')]
    first = {}
    for r in rows: first.setdefault(int(r[0]), r)
    cache = {}
    N = ImageFont.truetype(r'C:\Windows\Fonts\msgothic.ttc', 13)
    C = 6; CW, CH = 250, 46; per = C * 26
    ids = sorted(first)
    isos = {}
    for pat, tag in ((r'\*Koutetsu*', 'K'), (r'\*Sakusen*', 'F')):
        p = glob.glob(SS.B + pat)[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); isos[tag] = (iso, {f[0]: f for f in iso.walk()})
    for s in range(0, len(ids), per):
        pg = Image.new('L', (C * CW, 26 * CH), 25); d = ImageDraw.Draw(pg)
        for j, i in enumerate(ids[s:s + per]):
            r = first[i]; iso, ent = isos[r[1]]; key = (r[1], r[2])
            if key not in cache: cache[key] = iso.read(*ent[r[2]][1:3])
            l, x, y, w, h = map(int, r[3:8]); L = np.frombuffer(cache[key][l * 0x4000:(l + 1) * 0x4000], np.uint8).reshape(128, 128)
            b = (L[y:y + h, x:x + w] == INK)
            cx, cy = j % C * CW, j // C * CH
            d.text((cx + 2, cy + 14), str(i), font=N, fill=255)
            hh = min(h, 21); pg.paste(Image.fromarray((b[:hh] * 255).astype(np.uint8)).resize((min(w, 100) * 2, hh * 2), 0).crop((0, 0, 200, 44)), (cx + 40, cy + 1))
        pg.save('work/view/bgrid_%d.png' % (s // per))
    print(len(ids))


if __name__ == '__main__' and len(sys.argv) > 1: grid()
