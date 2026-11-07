# -*- coding: utf-8 -*-
"""ASC 글자 번호 문자열 찾기(읽기 전용).  python tools/asc_find.py"""
import sys, os, glob, re, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate, sprite_scan as SS
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
s, v = mstate.load('work/states/7.state')
def mem(k):
    o, n = v[k]; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; return bytes(b)
wh = mem('MAIN/WorkRAMH'); wl = mem('MAIN/WorkRAML')
for nm, b in (('H', wh), ('L', wl)):
    for key, lab in ((struct.pack('>HH', 49, 35), 'u16'), (bytes((49, 35)), 'u8')):
        p = [m.start() for m in re.finditer(re.escape(key), b)]
        print(nm, lab, len(p), [(hex(x), b[x:x + 14].hex()) for x in p[:8]])
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); c = collections.Counter()
for f in iso.walk():
    if f[0].endswith(('.MUS', '.CPK', '/')) or f[2] < 64 or f[0].startswith('/CDDA') or 'UNIT3D' in f[0]: continue
    try: d = iso.read(f[1], f[2])
    except EOFError: continue
    n = d.count(struct.pack('>HH', 49, 35))
    if n: c[f[0]] = n
print(c.most_common(12))

print('=== 칸 값')
keys = {'b196': struct.pack('>HH', 0xB196, 0xB15E), '196': struct.pack('>HH', 0x196, 0x15E), 'x4': struct.pack('>HH', 49 * 4, 35 * 4), 'rel': struct.pack('>HH', 0xC4, 0x8C)}
for k, key in keys.items():
    for nm, b in (('H', wh), ('L', wl)):
        p = [m.start() for m in re.finditer(re.escape(key), b)]
        if p: print(k, nm, len(p), [(hex(x), b[x - 4:x + 16].hex()) for x in p[:5]])
ent = {f[0]: f for f in iso.walk()}
for n in ('/VIEWCG/ASC16MAP.BIN',):
    d = iso.read(*ent[n][1:3]); print(n, len(d), d[:96].hex(' '))
    w = struct.unpack('>%dH' % (len(d) // 2), d[:len(d) // 2 * 2]); print(w[:40], max(w), collections.Counter(w).most_common(5))
