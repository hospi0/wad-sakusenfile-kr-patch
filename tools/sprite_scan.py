# -*- coding: utf-8 -*-
"""받은 스테이트의 VDP1 스프라이트 → 디스크 파일 위치 찾기(읽기 전용).  python tools/sprite_scan.py
  결과: work/text/sprites.tsv, 파일별 그림 모음 work/view/spr_NN.png"""
import sys, os, glob, struct, hashlib, bisect, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate
from iso9660 import Iso
import numpy as np
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\claude\roms\ss\World Advanced Daisenryaku'


def blob(pat):
    p = glob.glob(B + pat)[0]
    iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); parts = []; idx = []; n = 0
    for f in iso.walk():
        if f[0].endswith(('.MUS', '.CPK', '/')) or f[2] < 64 or 'UNIT3D' in f[0] or f[0].startswith('/CDDA'): continue
        try: d = iso.read(f[1], f[2])
        except EOFError: continue
        parts.append(d); idx.append((n, f[0])); n += len(d)
    return b''.join(parts), idx


def sprites(path):
    s, v = mstate.load(path)
    o, n = v['VDP1/VRAM']; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; vram = bytes(b)
    p = 0; seen = set(); out = []
    for _ in range(4000):
        if p in seen or p + 32 > len(vram): break
        seen.add(p)
        c = struct.unpack_from('>16H', vram, p)
        ctrl, link, mode, col, src, size = c[0:6]; jp = ctrl >> 12 & 7; cm = ctrl & 15
        if ctrl & 0x8000: break
        if not ctrl & 0x4000 and cm in (0, 1, 2):
            w, h = (size >> 8) * 8, size & 255; m = mode >> 3 & 7; bits = {0: 4, 1: 4, 2: 8, 3: 8, 4: 8, 5: 16}.get(m, 4)
            nb = w * h * bits // 8
            if 0 < nb <= 0x40000: out.append((src * 8, w, h, bits, vram[src * 8:src * 8 + nb]))
        p = link * 8 if jp in (1, 2) else p + 32
    return out


def main():
    fs = sorted(glob.glob('work/states/*.state')) + sorted(glob.glob('work/states_sf/*.state'))
    K, ki = blob(r'\*Koutetsu*'); F, fi = blob(r'\*Sakusen*'); print('블롭', len(K), len(F), flush=True)
    U = {}
    for f in fs:
        try: sp = sprites(f)
        except Exception as e: print('실패', f, e); continue
        for a, w, h, bits, d in sp:
            if len(set(d)) < 3 or w * h < 96: continue
            U.setdefault(hashlib.md5(d).hexdigest()[:10], (w, h, bits, d, os.path.basename(f)))
    print('고유 스프라이트', len(U), flush=True)
    def where(bl, ix, d):
        o = len(d) // 3; q = d[o:o + 48] if len(d) >= 200 else d
        p = bl.find(q)
        if p < 0: return None
        i = bisect.bisect_right([x[0] for x in ix], p) - 1
        return ix[i][1], p - ix[i][0] - o if len(d) >= 200 else p - ix[i][0]
    rows = []; hit = collections.Counter(); miss = 0
    for h_, (w, h, bits, d, st) in U.items():
        a = where(K, ki, d); b = where(F, fi, d)
        r = a or b
        if r: hit[r[0]] += 1
        else: miss += 1
        rows.append((h_, w, h, bits, st, a[0] if a else '-', '%X' % a[1] if a else '-', b[0] if b else '-', '%X' % b[1] if b else '-'))
    with open('work/text/sprites.tsv', 'w', encoding='utf-8', newline='\n') as f:
        f.write('#해시\t폭\t높이\t비트\t스테이트\t본편 파일\t위치\t작전 파일\t위치\n')
        for r in rows: f.write('\t'.join(map(str, r)) + '\n')
    print('찾음', sum(hit.values()), '못 찾음', miss); print(hit.most_common(50))
    # 그림 모음
    def img(w, h, bits, d):
        if bits == 4:
            a = np.frombuffer(d, np.uint8); p = (np.stack([a >> 4, a & 15], 1).reshape(-1) * 17).astype(np.uint8)
        elif bits == 8: p = np.frombuffer(d, np.uint8)
        else:
            a = np.frombuffer(d, '>u2'); p = ((a >> 5 & 31) << 3).astype(np.uint8)
        return Image.fromarray(p[:w * h].reshape(h, w))
    order = sorted(U.items(), key=lambda kv: (kv[1][1], kv[1][0]))
    pg = None; k = 0; x = y = hh = 0
    for h_, (w, h, bits, d, st) in order:
        if w > 340 or h > 240: continue
        if pg is None: pg = Image.new('L', (1600, 1000), 50); x = y = 2; hh = 0
        if x + w + 4 > 1600: x = 2; y += hh + 4; hh = 0
        if y + h > 996:
            pg.save('work/view/spr_%02d.png' % k); k += 1; pg = Image.new('L', (1600, 1000), 50); x = y = 2; hh = 0
        pg.paste(img(w, h, bits, d), (x, y)); x += w + 4; hh = max(hh, h)
    if pg: pg.save('work/view/spr_%02d.png' % k); k += 1
    print('모음', k)


if __name__ == '__main__':
    main()
