# -*- coding: utf-8 -*-
"""화면 글자 그림(칸 4개)이 어느 파일에 있나(읽기 전용)."""
import sys, os, glob, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate, sprite_scan as SS
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
s, v = mstate.load('work/states/7.state')
def mem(k):
    o, n = v[k]; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; return bytes(b)
vr = mem('VDP2/VRAM')
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0])
keys = {'累': vr[0x29A * 32:0x29A * 32 + 128], '通': vr[0x2BE * 32:0x2BE * 32 + 128], '帝': vr[0x2EA * 32:0x2EA * 32 + 128], '累위': vr[0x29A * 32:0x29A * 32 + 32], '累아래': vr[0x29C * 32:0x29C * 32 + 32]}
for f in iso.walk():
    if f[0].endswith(('.MUS', '.CPK', '/', '.EP')) or f[2] < 16 or f[0].startswith('/CDDA') or 'UNIT3D' in f[0]: continue
    try: d = iso.read(f[1], f[2])
    except EOFError: continue
    for k, b in keys.items():
        o = d.find(b)
        if o >= 0: print(k, f[0], hex(o), f[2])
