# -*- coding: utf-8 -*-
"""UPK 큰 유닛 이름(ASC16 번호 10칸, 레코드 FFFF 앞) → work/text/big.tsv, big_pos.tsv, my files/tsv/wad_015.tsv.  --write"""
import sys, struct, re, collections
sys.path.insert(0, 'tools'); sys.stdout.reconfigure(encoding='utf-8')
import asc_build as B, asc_table as T
S = T.SHEET; N = 10
U = collections.OrderedDict(); pos = []; lat = set()
for tag in 'KF':
    iso, E = B.disc(tag)
    for fn in sorted(E):
        if not fn.startswith('/UNITPACK/UPK'): continue
        d = iso.read(*E[fn][1:3])
        for m in re.finditer(b'\xff\xff', d):
            o = m.start()
            if o < 2 * N or o % 2: continue
            w = struct.unpack('>%dH' % N, d[o - 2 * N:o])
            if not w[0] or max(w) >= 1200: continue
            if any(a == 0 and b for a, b in zip(w, w[1:])) and not re.search('[ァ-ヶ一-龥]', ''.join(S[x] for x in w if x)): continue
            t = ''.join(S[x] if x else '　' for x in w).rstrip('　')
            if not t or '□' in t and 0: continue
            if re.search('[ぁ-ヶ一-龥]', t): U.setdefault(t, 0); U[t] += 1; pos.append((t, tag, fn, o - 2 * N))
            else: lat.add(t)
print(len(U), '영문만', len(lat), sum(len(t) for t in U), '□ 있는 줄', [t for t in U if '□' in t][:10])
print(' / '.join(list(U)[:60]))
print('라틴 예', sorted(lat)[:30])
if '--write' in sys.argv:
    H = '#번호\t구분\t글자수\t쓰임\tJP\tKO\n'; b = ''
    ids = {t: '%05d' % (2240 + i) for i, t in enumerate(U)}
    for t, c in U.items(): b += '%s\tB\t10\t%d\t%s\t\n' % (ids[t], c, t)
    open('work/text/big.tsv', 'w', encoding='utf-8', newline='\n').write(H + b)
    open('my files/tsv/wad_015.tsv', 'w', encoding='utf-8', newline='\n').write(H + b)
    open('work/text/big_pos.tsv', 'w', encoding='utf-8', newline='\n').write(''.join('%s\t%s\t%s\t%X\n' % (ids[t], g, f, o) for t, g, f, o in pos))
    print(len(b.encode()))
