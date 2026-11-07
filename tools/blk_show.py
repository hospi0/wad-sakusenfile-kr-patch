# -*- coding: utf-8 -*-
import sys, os, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B, asc_table as T
sys.stdout.reconfigure(encoding='utf-8')
iso, E = B.disc('K'); d = iso.read(*E['/GAME2.BIN'][1:3]); S = T.SHEET; base = 0x217000
idx = collections.defaultdict(list)
for i in range(0, len(d) - 3, 2):
    x = struct.unpack_from('>I', d, i)[0] - base
    if 0 <= x < len(d): idx[x].append(i)
o = 0x1A036
for k in range(26):
    st = o; W = []
    while struct.unpack_from('>H', d, o)[0] != 0xFFFF: W.append(struct.unpack_from('>H', d, o)[0]); o += 2
    o += 2
    print(k, hex(st), [hex(x) for x in idx.get(st, [])][:4], ''.join(S[x] if x < len(S) else '?' for x in W))
tb = 0x950 - 0x40
print([hex(struct.unpack_from('>I', d, q)[0] - base) for q in range(0x900, 0x9A0, 4)])
print('---')
for st in (0x1a0da, 0x1a106, 0x1a10c, 0x1a11a):
    q = st; W = []
    while struct.unpack_from('>H', d, q)[0] != 0xFFFF: W.append(struct.unpack_from('>H', d, q)[0]); q += 2
    print(hex(st), ''.join(S[x] if x < len(S) else '?' for x in W), [(k, [hex(a) for a in idx.get(st + k, [])]) for k in range(-4, (len(W) + 1) * 2, 2) if idx.get(st + k)])
print(hex(struct.unpack_from('>I', d, 0x814)[0] - base), hex(struct.unpack_from('>I', d, 0x818)[0]), d[0x7f0:0x830].hex(' '))
import ko_audit as A
k, _, _ = A.load_ko()
for r in open('work/text/ui_pos.tsv', encoding='utf-8'):
    i, tag, fn, o, n = r.rstrip('\n').split('\t')
    if tag == 'K' and fn == '/GAME2.BIN' and int(o, 16) in (0x1a0da, 0x1a106, 0x1a10c, 0x1a11a): print(i, o, n, k.get(i, [[0] * 6])[0][4:6])
