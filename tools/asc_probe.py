# -*- coding: utf-8 -*-
"""ASC16 글꼴이 VDP2 VRAM 에 어떻게 있는지 스테이트별로(읽기 전용)."""
import sys, os, glob, struct, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, mstate
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); E = {f[0]: f for f in iso.walk()}
r = lambda n: iso.read(*E[n][1:3])
a, b = r('/VIEWCG/ASC16X16.BIN'), r('/VIEWCG/ASC16_2.BIN'); cg = a + b; mp = r('/VIEWCG/ASC16MAP.BIN')
print('크기', len(a), len(b), len(mp), E['/VIEWCG/ASC16X16.BIN'][1:3])
w = struct.unpack('>%dH' % (len(mp) // 2), mp); print('칸값 범위', hex(min(w)), hex(max(w)), '겹침', len(w) - len(set(w)))
print('처음', [hex(x) for x in w[:12]], [hex(x) for x in w[-8:]])
for f in sorted(glob.glob('work/states/*.state'), key=lambda x: int(re.sub(r'\D', '', os.path.basename(x)) or 0)):
    s, v = mstate.load(f)
    o, n = v['VDP2/VRAM']; m = bytearray(s[o:o + n]); m[0::2], m[1::2] = m[1::2], m[0::2]; m = bytes(m)
    hit = {}
    for ci in range(0, len(cg) // 32):
        t = cg[ci * 32:ci * 32 + 32]
        if t.count(0) > 26: continue
        q = m.find(t)
        if q >= 0:
            k = (q - ci * 32); hit[k] = hit.get(k, 0) + 1
    top = sorted(hit.items(), key=lambda x: -x[1])[:3]
    print(os.path.basename(f), [(hex(k), c) for k, c in top])
