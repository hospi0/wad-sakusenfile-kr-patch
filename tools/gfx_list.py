# -*- coding: utf-8 -*-
"""글자 있는 스프라이트 후보를 실제 색으로 모아 보기(읽기 전용).  python tools/gfx_list.py
  결과 work/gfx/v1/list_N.png + work/gfx/v1/list.tsv(번호·파일·위치·크기·비트·스테이트·col)"""
import sys, os, glob, struct, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate
import numpy as np
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8')
OUT = 'work/gfx/v1'; os.makedirs(OUT, exist_ok=True)
rows = [l.rstrip('\n').split('\t') for l in open('work/text/sprites.tsv', encoding='utf-8') if l[0] != '#']
want = [r for r in rows if r[5] in ('/SAKUSEN/SAKU_DT.BIN', '/GMS2.BIN', '/GAME2.BIN', '/DAI_TIT1.DC', '/00000000.BIN') and int(r[1]) * int(r[2]) >= 500]
want.sort(key=lambda r: (r[5], int(r[6], 16)))


def state_sprites(path):
    s, v = mstate.load(path)
    def mem(k):
        o, n = v[k]; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; return bytes(b)
    vram = mem('VDP1/VRAM'); cram = mem('VDP2/CRAM') if 'VDP2/CRAM' in v else None
    if cram is None:
        k = [x for x in v if 'CRAM' in x]; cram = mem(k[0])
    p = 0; seen = set(); out = {}
    for _ in range(4000):
        if p in seen or p + 32 > len(vram): break
        seen.add(p)
        c = struct.unpack_from('>16H', vram, p); ctrl, link, mode, col, src, size = c[0:6]; jp = ctrl >> 12 & 7; cm = ctrl & 15
        if ctrl & 0x8000: break
        if not ctrl & 0x4000 and cm in (0, 1, 2):
            w, h = (size >> 8) * 8, size & 255; m = mode >> 3 & 7; bits = {0: 4, 1: 4, 2: 8, 3: 8, 4: 8, 5: 16}.get(m, 4); nb = w * h * bits // 8
            d = vram[src * 8:src * 8 + nb]
            if nb: out[hashlib.md5(d).hexdigest()[:10]] = (d, w, h, bits, m, col, vram)
        p = link * 8 if jp in (1, 2) else p + 32
    return out, cram


cache = {}
def rgb(d, w, h, bits, m, col, vram, cram):
    c = np.frombuffer(cram, '>u2').astype(int)
    if bits == 16:
        a = np.frombuffer(d, '>u2').astype(int)
    else:
        if bits == 4:
            x = np.frombuffer(d, np.uint8); px = np.stack([x >> 4, x & 15], 1).reshape(-1).astype(int)
        else: px = np.frombuffer(d, np.uint8).astype(int)
        if m == 1:      # 색표: col*8 위치 16색 표
            t = np.frombuffer(vram[col * 8:col * 8 + 32], '>u2').astype(int); v = t[px]
            a = np.where(v & 0x8000, v, c[v & 0x7FF]);
        elif m == 0: a = c[(px + (col & 0xFFF0)) & 0x7FF]
        else: a = c[(px + (col & 0xFF00)) & 0x7FF]
    im = np.stack([(a & 31) << 3, (a >> 5 & 31) << 3, (a >> 10 & 31) << 3], 1).reshape(h, w, 3).astype(np.uint8)
    return Image.fromarray(im)


items = []
for r in want:
    st = r[4]
    f = 'work/states/' + st if os.path.exists('work/states/' + st) else 'work/states_sf/' + st
    if f not in cache: cache[f] = state_sprites(f)
    sp, cram = cache[f]
    if r[0] not in sp: continue
    d, w, h, bits, m, col, vram = sp[r[0]]
    items.append((r, rgb(d, w, h, bits, m, col, vram, cram), m, col))
print(len(items))
with open(OUT + '/list.tsv', 'w', encoding='utf-8', newline='\n') as f:
    for i, (r, im, m, col) in enumerate(items): f.write('%d\t%s\t%s\t%s\t%s\t%s\t%s\t%d\t%04X\n' % (i, r[5], r[6], r[1], r[2], r[3], r[4], m, col))
pg = None; k = 0; x = y = hh = 0; W = 1500
for i, (r, im, m, col) in enumerate(items):
    w, h = im.size; S = 2 if w <= 200 else 1
    if pg is None: pg = Image.new('RGB', (W, 1000), (70, 40, 70)); d = ImageDraw.Draw(pg); x = y = 4; hh = 0
    if x + max(w * S, 30) + 6 > W: x = 4; y += hh + 18; hh = 0
    if y + h * S + 16 > 1000:
        pg.save('%s/list_%d.png' % (OUT, k)); k += 1; pg = Image.new('RGB', (W, 1000), (70, 40, 70)); d = ImageDraw.Draw(pg); x = y = 4; hh = 0
    d.text((x, y), str(i), fill=(255, 255, 0)); pg.paste(im.resize((w * S, h * S), 0), (x, y + 12)); x += max(w * S, 30) + 6; hh = max(hh, h * S)
if pg: pg.save('%s/list_%d.png' % (OUT, k)); k += 1
print('장', k)
