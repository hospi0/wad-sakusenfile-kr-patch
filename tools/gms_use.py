# -*- coding: utf-8 -*-
import sys, collections
sys.stdout.reconfigure(encoding='utf-8')
U = set()
for l in open('work/text/sprites.tsv', encoding='utf-8'):
    if l[0] == '#': continue
    p = l.rstrip('\n').split('\t')
    if p[5] == '/GMS2.BIN':
        try: o = int(p[6])
        except: o = int(p[6], 16)
        U.add((o, int(p[1]) * int(p[2]) * int(p[3]) // 8, p[1] + 'x' + p[2] + 'x' + p[3]))
U = sorted(U); print(len(U))
for a, n, t in U:
    if a < 0x40000: print(hex(a), hex(a + n), t)
for s, l in ((0x19802, 0x884), (0x1C026, 0x580), (0x39CA2, 0x408), (0x2F4E2, 0x204)):
    print(hex(s), hex(l), [hex(a) for a, n, t in U if a < s + l and a + n > s])
