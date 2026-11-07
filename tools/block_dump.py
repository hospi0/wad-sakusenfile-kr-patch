# -*- coding: utf-8 -*-
"""글꼴 묶음 번호 문자열 덤프(읽기 전용).  python tools/block_dump.py"""
import sys, os, glob, struct, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, asc_table
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
pk = glob.glob(SS.B + r'\*Koutetsu*')[0]; ik = Iso(sorted(glob.glob(pk + r'\*(Track 1).bin'))[0]); ek = {f[0]: f for f in ik.walk()}
rk = lambda n: ik.read(*ek[n][1:3])
mp = rk('/VIEWCG/ASC16MAP.BIN'); cg = rk('/VIEWCG/ASC16X16.BIN') + rk('/VIEWCG/ASC16_2.BIN')
w = struct.unpack('>%dH' % (len(mp) // 2), mp); G = {}
for i in range(len(w) // 4):
    g = b''.join(cg[(t - 0x800) * 32:(t - 0x800) * 32 + 32] for t in w[i * 4:i * 4 + 4]); G.setdefault(g, asc_table.SHEET[i])
def dump(fn, base, cnt, a, b, idb, sp=0):
    d = rk(fn); L = [G.get(d[base + i * 128:base + i * 128 + 128], '?') for i in range(cnt)]
    v = struct.unpack('>%dH' % ((b - a) // 2), d[a:b]); out = []; cur = ''
    for x in v:
        if x == 0xFFFF: out.append(cur.strip('　')); cur = ''
        elif x == 0xFFFE: cur += '/'
        elif x == sp: cur += '　'
        elif 0 <= x - idb < cnt: cur += L[x - idb]
        else: cur += '<%X>' % x
    out.append(cur.strip('　'))
    return out
g = dump('/GMS2.BIN', 0xD95C, 99, 0x14A0, 0x1A00, 1); print(len(g)); print(' | '.join(g)[:2200])
r = dump('/RMC2.BIN', 0x44, 88, 0x2C48, 0x2F00, 1); print(len(r)); print(' | '.join(r)[:900])
d = rk('/W_MAP2.BIN'); W = struct.unpack('>%dH' % (len(d) // 2), d[:len(d) // 2 * 2])
for st in range(20, 34):
    for i in range(len(W) - 6):
        if W[i] == st and all(W[i + k] == st + k for k in range(6)):
            print('연표 번호 시작', st, hex(i * 2), [hex(x) for x in W[i - 6:i + 12]]); break

print('=== 연표')
d = rk('/W_MAP2.BIN'); base = 0x4E128; cnt = 428; L = [G.get(d[base + i * 128:base + i * 128 + 128], '?') for i in range(cnt)]
a = 0x4A040; n = (base - a) // 2; v = struct.unpack('>%dH' % n, d[a:a + n * 2])
s = ''
for x in v:
    if x == 0: s += '|'
    elif x == 1: s += '　'
    elif 2 <= x < cnt + 2: s += L[x - 2]
    else: s += '<%X>' % x
s = re.sub(r'\|{2,}', ' ‖ ', s); s = re.sub('　{2,}', ' ¦ ', s)
print(len(s)); print(s[:2400])
