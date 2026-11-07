# -*- coding: utf-8 -*-
"""화면별 글자 그림(칸 4개 연속)의 출처 파일 통계(읽기 전용).  python tools/font_homes.py 스테이트번호…"""
import sys, os, glob, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate, sprite_scan as SS
from iso9660 import Iso
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0])
blobs = []
for f in iso.walk():
    if f[0].endswith(('.MUS', '.CPK', '/', '.EP')) or f[2] < 512 or f[0].startswith('/CDDA') or 'UNIT3D' in f[0] or '/SAKU_' in f[0] or 'EARTH' in f[0]: continue
    try: blobs.append((f[0], iso.read(f[1], f[2])))
    except EOFError: pass
for st in sys.argv[1:]:
    fn = 'work/states/%s.state' % st if os.path.exists('work/states/%s.state' % st) else 'work/states_sf/%s.state' % st[2:]
    s, v = mstate.load(fn)
    o, n = v['VDP2/VRAM']; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; vr = bytes(b)
    rr = [k for k in v if 'RawRegs' in k]; R = [int(x) for x in np.frombuffer(s[v[rr[0]][0]:v[rr[0]][0] + v[rr[0]][1]], '<u2')]
    tiles = collections.Counter()
    for nb, ab in enumerate((0x40, 0x44, 0x48, 0x4C)):
        if not R[0x20 // 2] >> nb & 1: continue
        hi = R[0x3C // 2] >> (nb * 4) & 7
        for ps in (0x2000,):
            m = (((hi << 6) | (R[ab // 2] & 0x3F)) * ps) & 0x7FFFF
            if m + 0x2000 > len(vr): continue
            a = np.frombuffer(vr[m:m + 0x2000], '>u2').astype(int) & 0xFFF
            for i in range(0, 4095):
                if a[i] and a[i + 1] == a[i] + 1: tiles[int(a[i])] += 1
    home = collections.Counter(); seen = 0
    for t, c in tiles.most_common(120):
        g = vr[t * 32:t * 32 + 128]
        if len(set(g)) < 6: continue
        seen += 1
        for nm, d in blobs:
            if g in d: home[nm] += 1
    print(st, '칸', seen, home.most_common(6), flush=True)
