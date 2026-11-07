# -*- coding: utf-8 -*-
"""큰 이름(9칸) ↔ 같은 레코드 반각 이름 ↔ wad_008 번역 대응 → work/text/big.tsv 초안."""
import sys, struct, re, collections
sys.path.insert(0, 'tools'); sys.stdout.reconfigure(encoding='utf-8')
import asc_build as B, asc_table as T, unit_names as UN, ko_audit as A
S = T.SHEET; N = 9
k, _, _ = A.load_ko()
J2K = {}
for l in open('work/text/small.tsv', encoding='utf-8'):
    if l[0] != '#':
        p = l.split('\t')
        if p[0] in k: J2K[p[4]] = k[p[0]][0][5]
print('wad_008', len(J2K), list(J2K.items())[:4])
U = collections.OrderedDict(); pos = []; lat = collections.OrderedDict()
for tag in 'KF':
    iso, E = B.disc(tag)
    for fn in sorted(E):
        if not fn.startswith('/UNITPACK/UPK'): continue
        d = iso.read(*E[fn][1:3])
        for m in re.finditer(b'\xff\xff', d):
            o = m.start()
            if o < 40 or o % 2: continue
            w = struct.unpack('>%dH' % N, d[o - 2 * N:o])
            if not w[0] or max(w) >= 1200: continue
            t = ''.join(S[x] if x else '　' for x in w).rstrip('　')
            h = UN.dec(d[o - 2 * N - 10:o - 2 * N - 1]).rstrip(' 　') if hasattr(UN, 'dec') else ''
            if re.search('[ぁ-ヶ一-龥]', t): U.setdefault(t, collections.Counter())[h] += 1; pos.append((t, tag, fn, o - 2 * N))
            else: lat[t] = 1
print(len(U), '라틴', len(lat), list(lat)[:12])
rows = []; hit = 0
for t, c in U.items():
    h = c.most_common(1)[0][0]; ko = J2K.get(h, '')
    if ko: hit += 1
    rows.append((t, h, ko))
print('번역 찾음', hit, '없음', len(rows) - hit)
for r in rows[:14] + rows[200:206]: print(r)
print([ (t, h) for t, h, ko in rows if not ko][:30])
print('9칸 넘침', [(t, ko) for t, h, ko in rows if len(ko) > 9][:40])
if '--write' in sys.argv:
    H = '#번호\t구분\t글자수\t쓰임\tJP\tKO\n'; ids = {r[0]: '%05d' % (2240 + i) for i, r in enumerate(rows)}
    open('work/text/big.tsv', 'w', encoding='utf-8', newline='\n').write(H + ''.join('%s\tB\t9\t1\t%s\t%s\n' % (ids[t], t, ko) for t, h, ko in rows))
    open('work/text/big_pos.tsv', 'w', encoding='utf-8', newline='\n').write(''.join('%s\t%s\t%s\t%X\n' % (ids[t], g, f, o) for t, g, f, o in pos))
