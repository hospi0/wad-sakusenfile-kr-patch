# -*- coding: utf-8 -*-
import sys, os, re, glob, struct
sys.path.insert(0, 'tools')
import asc_build as B, mstate, collections
sys.stdout.reconfigure(encoding='utf-8')
L = [l.rstrip('\n').split('\t') for f in ('work/text/ko_extra.tsv', 'work/text/ko_extra2.tsv') for l in open(f, encoding='utf-8') if l[0] != '#']
K = {p[0]: p[-1] for p in L if len(p) > 1}
R = [l.split('\t') for f in ('work/text/extra.tsv', 'work/text/extra2.tsv') for l in open(f, encoding='utf-8') if l[0] != '#']
ids = [r for r in R if r[1] in ('M', 'KG')]
print([r[:5] for r in ids if not K.get(r[0])], [r[4] for r in ids[-8:]])
ch = collections.Counter(c for r in ids for c in K.get(r[0], '') if c != ' ')
print(len(ch), sorted(c for c in ch if ord(c) < 128))
iso, E = B.disc('K'); d = iso.read(*E['/GMS2.BIN'][1:3])
s, v = mstate.load('work/states/44.state')
o, n = v['MAIN/WorkRAML']; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; m = bytes(b)
R2 = sorted(((x.end() - x.start(), x.start()) for x in re.finditer(rb'\0{200,}', d[:0x40000])), reverse=True)
print([(hex(a), hex(l), not any(m[a:a + l])) for l, a in R2[:12]])
