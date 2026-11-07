# -*- coding: utf-8 -*-
"""반각 자리 전수(읽기 전용): 자리 (태그, 파일, 위치, 칸, 원문) 목록.  from half_scan import scan"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B, unit_names as UN
N = dict(UN.names); N[1] = ' '
def dec(b): return ''.join(N.get(x, '<%02X>' % x) for x in b).rstrip(' ')
HASK = re.compile('[ァ-ヴ]')
GEO = {'K': dict(dt=(0x13C00, 0x17E98), scn=0x1B6C8), 'F': dict(dt=(0x13000, 0x1401C), scn=None)}

KNOWN = {l.rstrip('\n').split('\t')[1] for l in open('work/text/romaji.tsv', encoding='utf-8')} | {l.split('\t')[0] for l in open('work/text/romaji2.tsv', encoding='utf-8')}


def scan(tag):
    iso, E = B.disc(tag); R = []
    rd = lambda n: iso.read(*E[n][1:3])
    # SHINARIO: 36 B 레코드, 9칸 이름(앞 1 B = 번호)
    s = rd('/SHINARIO.BIN')
    for i in range(0, len(s) - 9):
        f = s[i:i + 9]
        if all(1 <= x <= 0xAD for x in f) and i >= 1 and s[i + 9] == 0 and (s[i:i + 9] != b'\x01' * 9):
            t = dec(f)
            if HASK.search(t) and '<' not in t and (i + 9 - 0x24 < 0 or True):
                R.append(('S', '/SHINARIO.BIN', i, 9, t))
    # SAKU_DT
    d = rd('/SAKUSEN/SAKU_DT.BIN'); a, b = GEO[tag]['dt']
    for i in range(a, b - 10):
        f = d[i:i + 9]
        if d[i + 9] == 0 and (d[i - 1] == 0 or dec(f) in KNOWN) and all(1 <= x <= 0xAD for x in f) and f[0] != 1:
            t = dec(f)
            if HASK.search(t) and '<' not in t: R.append(('D', '/SAKUSEN/SAKU_DT.BIN', i, 9, t))
    return R, iso, E

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    R, iso, E = scan(sys.argv[1] if len(sys.argv) > 1 else 'K')
    import collections
    print(collections.Counter(r[0] for r in R))
    for g in 'SD':
        U = collections.Counter(r[4] for r in R if r[0] == g); print(g, len(U), ' / '.join(U)[:3000])
    P = [r[2] for r in R if r[0] == 'S']; print(collections.Counter((b - a) for a, b in zip(P, P[1:])).most_common(6), [hex(x) for x in P[:8]])
