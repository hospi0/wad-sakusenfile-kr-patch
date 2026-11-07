# -*- coding: utf-8 -*-
"""구역 FFFF 줄 목록: 위치·칸·포인터 수·번역 여부(읽기 전용).  python tools/asc_lines.py 파일 시작 끝"""
import sys, os, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B, asc_table as T, ko_audit as A
sys.stdout.reconfigure(encoding='utf-8')
S = T.SHEET
k, _, _ = A.load_ko()
def ch(v):
    if v == 0: return '　'
    v2 = v - 2 if v >= 564 else v
    return S[v2] if v2 < len(S) else '<%X>' % v
pos = {}
for l in open('work/text/ui_pos.tsv', encoding='utf-8'):
    i, tag, fn, o, n = l.rstrip('\n').split('\t')
    if tag == 'K' and fn == sys.argv[1]: pos[int(o, 16)] = (i, int(n))
iso, E = B.disc('K'); fn = sys.argv[1]; d = iso.read(*E[fn][1:3]); a = int(sys.argv[2], 16); b = int(sys.argv[3], 16); base = B.BASE.get(fn)
idx = collections.Counter()
if base is not None:
    for i in range(0, len(d) - 3, 2):
        x = struct.unpack_from('>I', d, i)[0] - base
        if a <= x < b: idx[x] += 1
o = a
while o < b:
    e = o
    while e < len(d) - 1 and struct.unpack_from('>H', d, e)[0] != 0xFFFF and e - o < 120: e += 2
    w = struct.unpack('>%dH' % ((e - o) // 2), d[o:e])
    t = ''.join(ch(x) for x in w)
    p = pos.get(o)
    print('%X n=%d ptr=%d %s %s' % (o, len(w), idx[o], t, ('→ %s %s' % (p[0], k[p[0]][0][5])) if p else ''))
    o = e + 2
