# -*- coding: utf-8 -*-
"""글꼴 묶음 번호 기준 찾기: 연속 번호열 시작값을 찾아 문자열 풀기(읽기 전용).  python tools/block_str.py 파일 묶음위치 글자수"""
import sys, os, glob, struct, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, asc_table
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
fn, base, cnt = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3])
pk = glob.glob(SS.B + r'\*Koutetsu*')[0]; ik = Iso(sorted(glob.glob(pk + r'\*(Track 1).bin'))[0]); ek = {f[0]: f for f in ik.walk()}
rk = lambda n: ik.read(*ek[n][1:3])
mp = rk('/VIEWCG/ASC16MAP.BIN'); cg = rk('/VIEWCG/ASC16X16.BIN') + rk('/VIEWCG/ASC16_2.BIN')
w = struct.unpack('>%dH' % (len(mp) // 2), mp); G = {}
for i in range(len(w) // 4):
    g = b''.join(cg[(t - 0x800) * 32:(t - 0x800) * 32 + 32] for t in w[i * 4:i * 4 + 4]); G.setdefault(g, asc_table.SHEET[i])
d = rk(fn)
L = [G.get(d[base + i * 128:base + i * 128 + 128], '?') for i in range(cnt)]
print(''.join(L)[:200])
W = struct.unpack('>%dH' % (len(d) // 2), d[:len(d) // 2 * 2])
cand = collections.Counter()
for i in range(len(W) - 4):
    a = W[i]
    if 0 < a < 0x1000 and W[i + 1] == a + 1 and W[i + 2] == a + 2 and W[i + 3] == a + 3: cand[a] += 1
print('연속 시작값', cand.most_common(10))
for a in sorted(cand)[:6]:
    i = next(k for k in range(len(W) - 4) if W[k] == a and W[k + 1] == a + 1 and W[k + 2] == a + 2)
    print(hex(a), hex(i * 2), [hex(x) for x in W[max(0, i - 4):i + 10]])
