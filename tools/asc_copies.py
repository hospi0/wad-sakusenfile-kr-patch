# -*- coding: utf-8 -*-
"""UI 번역표 각 줄의 «자리표에 없는 사본» 전수(읽기 전용) + 말풍선 칸 초과.  python tools/asc_copies.py"""
import sys, os, re, struct, collections, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B, asc_table as T, ko_audit as A
sys.stdout.reconfigure(encoding='utf-8')
S = T.SHEET; inv = collections.defaultdict(list)
for i, c in enumerate(S): inv[c].append(i + 2 if i >= 562 else i)
inv['　'] = [0]; inv[' '] = [0]
k, _, _ = A.load_ko()
J = [l.rstrip('\n').split('\t') for l in open('work/text/ui.tsv', encoding='utf-8') if l[0] != '#']
pos = collections.defaultdict(dict)
for l in open('work/text/ui_pos.tsv', encoding='utf-8'):
    i, tag, fn, o, n = l.rstrip('\n').split('\t')
    if tag == 'K': pos[fn][int(o, 16)] = i
iso, E = B.disc('K'); D = {}
for fn, e in E.items():
    if fn.endswith(('.MUS', '.CPK', '/', '.EP', '.DC', '.TXT', '.TSK')) or e[2] < 8 or fn.startswith(('/CDDA', '/VIEWMAP', '/VIEWCG', '/RBG', '/UNIT3D', '/DAI_SF', '/FIXPOL', '/EARTH', '/UNITPACK', '/UNITINIT')) or 'SAKU_F' in fn: continue
    try: D[fn] = iso.read(*e[1:3])
    except EOFError: pass
out = []; miss_enc = 0
for p in J:
    i, g, n, u, t = p[:5]
    if len(t) < 2 or i not in k: continue
    if any(c not in inv for c in t): miss_enc += 1; continue
    combos = list(itertools.islice(itertools.product(*[inv[c][:2] for c in t]), 8))
    for cb in combos:
        b = struct.pack('>%dH' % len(t), *cb) + b'\xff\xff'
        for fn, d in D.items():
            q = -1
            while True:
                q = d.find(b, q + 1)
                if q < 0: break
                if q % 2 == 0 and q not in pos[fn]: out.append((i, g, t, k[i][0][5], fn, q, d[max(0, q - 4):q].hex()))
print('사본', len(out), '인코딩 불가 줄', miss_enc)
open('work/text/asc_copies.tsv', 'w', encoding='utf-8', newline='\n').write(''.join('%s\t%s\t%s\t%s\t%s\t%X\t%s\n' % r for r in out))
c = collections.Counter(r[4] for r in out); print(c.most_common(12))
for r in out[:90]: print(r[0], r[2], '→', r[3], r[4], hex(r[5]), r[6])
g2 = D['/GAME2.BIN']
print('말풍선 구역'); o = 0x1A000
def line(o):
    e = o
    while struct.unpack_from('>H', g2, e)[0] != 0xFFFF and e - o < 60: e += 2
    return e
o = 0x1A00E; L = []
for _ in range(36):
    e = line(o); w = struct.unpack('>%dH' % ((e - o) // 2), g2[o:e]); t = ''.join(S[x - 2 if x >= 564 else x] if x < 1190 else '#' for x in w)
    tr = pos['/GAME2.BIN'].get(o); L.append('%X %s(%d)→%s' % (o, t, len(w), (k[tr][0][5] + '(%d)' % len(k[tr][0][5])) if tr else '없음')); o = e + 2
print(' | '.join(L))
