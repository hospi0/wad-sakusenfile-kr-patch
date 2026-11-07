# -*- coding: utf-8 -*-
"""지도 지명 한글화: 덩어리 번호별 일본어 → ko_final(P) → 층에 다시 그리기.  python tools/map_kr.py 폴더
  폴더/K_nn.bin(층 전체) · 폴더/prev_N.png(왼쪽 원본, 오른쪽 새것). 디스크는 안 건드림."""
import sys, os, glob, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, bdf
from iso9660 import Iso
import numpy as np
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8')
OUT = sys.argv[1] if len(sys.argv) > 1 else 'work/gfx/m1'; os.makedirs(OUT, exist_ok=True)
INK = 108
G9 = bdf.Font(r'C:\claude\utils\font\Galmuri-v2.40.3\Galmuri7.bdf')
import map_ids
M = map_ids.M
ID = [v for v in M.values() if v not in '#-']
EX = {'アメリカキドウブタイ': '미국 기동부대', 'ヴォロネジ': '보로네시', 'ボロネジ': '보로네시', 'コタバル': '코타바루', 'ポルタノヴァ': '폴타바', 'オリョール': '오룔', 'ドイツカンタイ': '독일|함대', 'ニホンカンタイ': '일본|함대'}
P = {}
ko = {l.split('\t')[0]: l.rstrip('\n').split('\t')[2] for l in open('work/text/ko_final.tsv', encoding='utf-8') if l[0] != '#'}
for l in open('work/text/place.tsv', encoding='utf-8'):
    if l[0] != '#': c = l.rstrip('\n').split('\t'); P[c[4]] = ko[c[0]]
P.update(EX)
for j in set(x for v in ID for x in v.split('|')):
    if j != '-' and j not in P: print('번역 없음', j)


def put(a, t, x, y):
    pts, w = G9.draw(t)
    if not pts: return
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x = max(0, min(x, 127 - (max(xs) - min(xs))))
    for px, py in pts:
        X, Y = px - min(xs) + x, py - min(ys) + y
        if 0 <= X < 128 and 0 <= Y < 128: a[Y, X] = INK


rows = [l.rstrip('\n').split('\t') for l in open('work/text/map_blobs.tsv', encoding='utf-8')]
G = collections.defaultdict(list)
for r in rows: G[(r[1], r[2])].append(r)
pairs = []
for pat, tag in ((r'\*Koutetsu*', 'K'), (r'\*Sakusen*', 'F')):
    p = glob.glob(SS.B + pat)[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); ent = {f[0]: f for f in iso.walk()}
    for (t, fn), rs in sorted(G.items()):
        if t != tag: continue
        d = iso.read(*ent[fn][1:3]); n = len(d) // 0x4000
        L = np.frombuffer(d[:n * 0x4000], np.uint8).reshape(n, 128, 128).copy(); src = L.copy()
        for r in rs:
            i, l, x, y, w, h = int(r[0]), int(r[3]), int(r[4]), int(r[5]), int(r[6]), int(r[7])
            jp = M.get(i)
            if jp is None or jp in ('-', '#'): continue
            a = L[l]
            if i == 94:                                   # 점선 경로와 붙은 덩어리: 글자만
                x0 = x + w - 42; box = a[y:y + 10, x0:x + w]; box[box == INK] = 0; put(a, P[jp], x0, y); continue
            box = a[y:y + h, x:x + w]; box[box == INK] = 0
            names = [q for j in jp.split('|') for q in P[j].split('|')]
            if len(names) == 1:
                tw = G9.draw(names[0])[1]; put(a, names[0], x + (w - tw) // 2, y + max(0, (h - 8)) // 2 if h <= 12 else y + h - 8)
            else:
                for k, t in enumerate(names):
                    tw = G9.draw(t)[1]
                    put(a, t, x + (0 if k == 0 else max(0, w - tw)), y + (h - 8) * k // max(1, len(names) - 1))
        name = fn.split('/')[-1][:-4]
        L.tofile('%s/%s_%s.bin' % (OUT, tag, name)); pairs.append((tag + name[-3:], src, L))
C = 6; S = 2
for s in range(0, len(pairs), 12):
    part = pairs[s:s + 12]; pg = Image.new('L', (C * (128 * S + 6), ((len(part) + 2) // 3) * (128 * S + 6)), 40); d = ImageDraw.Draw(pg)
    for i, (n, a, b) in enumerate(part):
        for k, q in enumerate((a, b)):
            m = (np.isin(q, [INK]).any(0) * 255).astype(np.uint8)
            x = (i % 3 * 2 + k) * (128 * S + 6); y = i // 3 * (128 * S + 6)
            pg.paste(Image.fromarray(m).resize((128 * S, 128 * S), 0), (x, y)); d.text((x + 2, y + 2), n, fill=180)
    pg.save('%s/prev_%d.png' % (OUT, s // 12))
print('지도', len(pairs))
