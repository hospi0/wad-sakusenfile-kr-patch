# -*- coding: utf-8 -*-
import sys, struct, re
sys.path.insert(0, 'tools'); sys.stdout.reconfigure(encoding='utf-8')
import mstate, asc_build as B
s, v = mstate.load('work/states/turn2.state')
def mem(k):
    o, n = v[k]; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; return bytes(b)
key = struct.pack('>3H', 133, 134, 135)
for k in ('MAIN/WorkRAML', 'MAIN/WorkRAMH', 'VDP2/VRAM'):
    m = mem(k); print(k, [hex(x.start()) for x in re.finditer(re.escape(key), m)][:8])
m = mem('MAIN/WorkRAML')
for x in re.finditer(re.escape(key), m):
    o = x.start(); print(hex(o), ' '.join('%X' % q for q in struct.unpack('>20H', m[o - 16:o + 24])))
iso, E = B.disc('K'); d = iso.read(*E['/GAME2.BIN'][1:3]); print(' '.join('%X' % q for q in struct.unpack('>40H', d[0x4D2A0:0x4D2F0])))
print('---')
m = mem('MAIN/WorkRAMH'); o = 0xC8EFE
print(' '.join('%X' % q for q in struct.unpack('>48H', m[o - 32:o + 64])))
seg = m[o - 8:o + 24]
hits = []
for f in iso.walk():
    if f[2] < 64 or f[0].startswith('/CDDA') or f[0].endswith(('.MUS', '.CPK', '.EP', '.DC')): continue
    try: d2 = iso.read(f[1], f[2])
    except EOFError: continue
    p = d2.find(seg)
    if p >= 0: hits.append((f[0], hex(p)))
print(hits[:8], len(hits))
