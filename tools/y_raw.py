# -*- coding: utf-8 -*-
import sys, os, struct, re, collections
sys.path.insert(0, 'tools')
import asc_build as B
sys.stdout.reconfigure(encoding='utf-8')
iso, E = B.disc('K'); m = iso.read(*E['/W_MAP2.BIN'][1:3]); print(hex(len(m)))
src = open('tools/f_year.py', encoding='utf-8').read()
a = 0x4A040; n = (0x4E128 - a) // 2; v = struct.unpack('>%dH' % n, m[a:a + n * 2])
print(' '.join('%X' % x for x in v[:140]))
print(collections.Counter(x for x in v if x > 430).most_common(8), v.count(0), v.count(1))
# FFFF 위치별 조각 길이
ff = [i for i, x in enumerate(v) if x == 0xFFFF]; print(len(ff), ff[:30], ff[-10:])
print(' '.join('%X' % x for x in v[ff[0] - 30:ff[0] + 40]))
idx = collections.Counter()
for i in range(0, len(m) - 3, 2):
    x = struct.unpack_from('>I', m, i)[0]
    if 0x200000 <= x < 0x300000 or 0x6000000 <= x < 0x6100000: idx[x] += 1
print(len(idx), [hex(k) for k, c in idx.most_common(6)])
print('앞', m[a - 64:a].hex(' '))
