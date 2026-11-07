# -*- coding: utf-8 -*-
"""UPK 레코드 큰 이름 전수(읽기 전용)."""
import sys, struct, re, collections, os
sys.path.insert(0, 'tools'); sys.stdout.reconfigure(encoding='utf-8')
import asc_build as B, asc_table as T, unit_names as UN
S = T.SHEET
iso, E = B.disc('K')
d = iso.read(*E['/UNITPACK/UPK01C.BIN'][1:3]); print(len(d))
print(d[0xA00:0xA90].hex(' '))
print(d[0x6A0:0x710].hex(' '))
for tag in 'KF':
    iso, E = B.disc(tag)
    U = collections.Counter(); P = collections.defaultdict(list); nf = 0
    for fn in sorted(E):
        if not fn.startswith('/UNITPACK/UPK'): continue
        nf += 1; d = iso.read(*E[fn][1:3])
        for o in range(0, len(d) - 24, 2):
            if d[o:o + 2] == b'\xff\xff' and o >= 40:
                q = o - 2; w = []
                while q >= 2 and len(w) < 14:
                    x = struct.unpack_from('>H', d, q)[0]
                    if x == 0xFFFF or x >= 1200: break
                    w.insert(0, x); q -= 2
                t = ''.join(S[x] if x else '　' for x in w).strip('　')
                if t and len(t) >= 1 and re.search('[ぁ-ヶ一-龥]', t): U[t] += 1; P[t].append((fn, q + 2, len(w)))
    print(tag, nf, len(U), sum(U.values())); print(' / '.join(list(U)[:80]))
    print(collections.Counter(n for v in P.values() for _, _, n in v).most_common(6))
