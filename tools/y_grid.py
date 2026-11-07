# -*- coding: utf-8 -*-
import sys, os, struct, re
sys.path.insert(0, 'tools'); sys.stdout.reconfigure(encoding='utf-8')
import asc_build as B, ded_build as D
iso, E = B.disc('K'); m = iso.read(*E['/W_MAP2.BIN'][1:3]); G = D.gm(iso, E)
src = open('tools/extract2.py', encoding='utf-8').read()
FX = eval(re.search(r'FX = (\{.*?\})\n', src).group(1))
L = [FX.get(i, G.get(m[0x4E128 + i * 128:0x4E128 + i * 128 + 128], '?')) for i in range(428)]
a = 0x4A040 + 40; n = 1474 - 20; v = struct.unpack('>%dH' % n, m[a:a + n * 2])
def c(x):
    if x == 0: return '_'
    if x == 1: return '·'
    if 2 <= x < 430: return L[x - 2]
    return '#'
for st in range(0, 17 * 34, 17): print('%4d' % st, ''.join(c(x) for x in v[st:st + 17]))
print(' '.join('%X' % x for x in struct.unpack('>24H', m[0x4A040:0x4A070])))
