# -*- coding: utf-8 -*-
"""화면 전용 글자 번호 문자열 파일 찾기(읽기 전용)."""
import sys, os, glob, struct, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate, sprite_scan as SS
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
s, v = mstate.load('work/states/7.state')
def mem(k):
    o, n = v[k]; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; return bytes(b)
wl = mem('MAIN/WorkRAML')
print(wl[0x310a0:0x31120].hex(' ')); print(wl[0x31520:0x31600].hex(' '))
key = wl[0x310d0:0x310f0]
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0])
for f in iso.walk():
    if f[0].endswith(('.MUS', '.CPK', '/', '.EP')) or f[2] < 16 or f[0].startswith('/CDDA') or 'UNIT3D' in f[0]: continue
    try: d = iso.read(f[1], f[2])
    except EOFError: continue
    o = d.find(key)
    if o >= 0: print('파일', f[0], hex(o), f[2], '적재 추정', hex(0x2310d0 - o))
