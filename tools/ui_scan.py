# -*- coding: utf-8 -*-
"""UI 문자열(ASC 글자 번호 u16 BE, 끝 FFFF, 0 = 빈칸) 전수 검색(읽기 전용).  python tools/ui_scan.py"""
import sys, os, glob, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
import asc_table
ch = dict(enumerate(asc_table.CH))
out = []
for pat, tag in ((r'\*Koutetsu*', 'K'), (r'\*Sakusen*', 'F')):
    p = glob.glob(SS.B + pat)[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); c = collections.Counter(); ct = collections.Counter()
    for f in iso.walk():
        if f[0].endswith(('.MUS', '.CPK', '/', '.EP', '.DC')) or f[2] < 64 or f[0].startswith('/CDDA') or 'UNIT3D' in f[0] or '/SAK' in f[0] or 'VIEWCG' in f[0] or 'EARTH' in f[0] or 'VIEWMAP' in f[0]: continue
        try: d = iso.read(f[1], f[2])
        except EOFError: continue
        for al in (0, 1):
            n = (len(d) - al) // 2; w = struct.unpack('>%dH' % n, d[al:al + n * 2]); prev = None
            ff = [i for i, x in enumerate(w) if x == 0xFFFF]
            for a, b in zip(ff, ff[1:]):
                seq = w[a + 1:b]
                if not 2 <= len(seq) <= 120 or any(x >= 1192 for x in seq): continue
                if sum(1 for x in seq if x) < 2: continue
                t = ''.join(ch[x] for x in seq).strip('　')
                if not t: continue
                c[f[0]] += 1; ct[f[0]] += len(t); out.append((tag, f[0], al + (a + 1) * 2, len(seq), t))
    print(tag, c.most_common(24), flush=True)
open('work/text/ui_raw.tsv', 'w', encoding='utf-8', newline='\n').write(''.join('%s\t%s\t%X\t%d\t%s\n' % r for r in out))
print(len(out), len({r[4] for r in out}), sum(len(t) for t in {r[4] for r in out}))
