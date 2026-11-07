# -*- coding: utf-8 -*-
"""작전파일 W_MAP2 글꼴 찾기(읽기 전용): 본편 연표 글자 그림과 대조."""
import sys, os, glob, struct, hashlib, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, asc_table, mstate
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
def op(pat):
    p = glob.glob(SS.B + pat)[0]; i = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); return i, {f[0]: f for f in i.walk()}
a, ea = op(r'\*Koutetsu*'); b, eb = op(r'\*Sakusen*')
d = b.read(*eb['/W_MAP2.BIN'][1:3]); k = a.read(*ea['/W_MAP2.BIN'][1:3])
print(len(d), len(k))
s, v = mstate.load('work/states_sf/3.state')
o, n = v['VDP2/VRAM']; bb = bytearray(s[o:o + n]); bb[0::2], bb[1::2] = bb[1::2], bb[0::2]; vr = bytes(bb)
off = collections.Counter()
for i in range(1, 500):
    g = vr[(0xD2 + i * 4) * 32:(0xD2 + i * 4) * 32 + 128]
    if len(set(g)) < 6: continue
    q = d.find(g)
    if q >= 0: off[q - i * 128] += 1
print([(hex(x), c) for x, c in off.most_common(4)])
for f in b.walk():
    if f[0].endswith(('.MUS', '.CPK', '/')) or f[2] < 4000 or 'UNIT' in f[0] or f[0].startswith('/SAKUSEN'): continue
    x = b.read(f[1], f[2]); g = vr[(0xD2 + 40 * 4) * 32:(0xD2 + 40 * 4) * 32 + 128]
    if g in x: print('출처', f[0], hex(x.find(g)))

print('=== 연표 비교')
ks = k[0x4A0A0:0x4E0A8]; fs_ = d[0x2CC1C - (0x4E0A8 - 0x4A0A0):0x2CC1C]
print(len(ks), ks == fs_, sum(1 for x, y in zip(ks, fs_) if x == y) / len(ks))
kf = k[0x4E0A8:0x4E0A8 + 428 * 128]; ff = d[0x2CC1C:0x2CC1C + 428 * 128]
print('글꼴 같은 칸', sum(kf[i * 128:i * 128 + 128] == ff[i * 128:i * 128 + 128] for i in range(428)))
p = d.find(ks[:64]); print('본편 첫머리 위치', hex(p))
n = 0
while n < len(ks) and ks[n] == d[0x2A864 + n]: n += 1
print('처음부터 같은 바이트', n, len(ks))
