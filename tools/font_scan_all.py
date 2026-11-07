# -*- coding: utf-8 -*-
"""두 디스크 전 파일에서 글꼴 묶음 찾기(읽기 전용).  python tools/font_scan_all.py → work/text/font_blocks.tsv"""
import sys, os, glob, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, asc_table
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
pk = glob.glob(SS.B + r'\*Koutetsu*')[0]; ik = Iso(sorted(glob.glob(pk + r'\*(Track 1).bin'))[0]); ek = {f[0]: f for f in ik.walk()}
rk = lambda n: ik.read(*ek[n][1:3])
mp = rk('/VIEWCG/ASC16MAP.BIN'); cg = rk('/VIEWCG/ASC16X16.BIN') + rk('/VIEWCG/ASC16_2.BIN')
w = struct.unpack('>%dH' % (len(mp) // 2), mp); G = {}
for i in range(len(w) // 4):
    c = asc_table.SHEET[i]
    if c in '□　': continue
    g = b''.join(cg[(t - 0x800) * 32:(t - 0x800) * 32 + 32] for t in w[i * 4:i * 4 + 4]); G.setdefault(g, c)
K = {g[:16]: 1 for g in G}
out = []
for pat, tag in ((r'\*Koutetsu*', 'K'), (r'\*Sakusen*', 'F')):
    p = glob.glob(SS.B + pat)[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0])
    for f in iso.walk():
        if f[0].endswith(('.MUS', '.CPK', '/', '.EP', '.DC')) or f[2] < 2000 or f[0].startswith('/CDDA') or 'UNIT3D' in f[0] or '/SAK' in f[0] or 'UNITPACK' in f[0] or 'UNITINIT' in f[0] or 'VIEWMAP' in f[0] or 'ASC16' in f[0]: continue
        try: d = iso.read(f[1], f[2])
        except EOFError: continue
        hits = collections.Counter()
        for i in range(0, len(d) - 128, 2):
            if d[i:i + 16] in K and d[i:i + 128] in G: hits[i % 128] += 1
        for al, c in hits.most_common(3):
            if c < 12: continue
            pos = [i for i in range(al, len(d) - 128, 128) if d[i:i + 128] in G]
            a, b = pos[0], pos[-1]
            L = ''.join(G.get(d[i:i + 128], '?') for i in range(a, b + 128, 128))
            out.append((tag, f[0], f[2], a, len(L), c, L[:70])); print(tag, f[0], hex(a), len(L), c, L[:50], flush=True)
open('work/text/font_blocks.tsv', 'w', encoding='utf-8', newline='\n').write(''.join('%s\t%s\t%d\t%X\t%d\t%d\t%s\n' % r for r in out))
