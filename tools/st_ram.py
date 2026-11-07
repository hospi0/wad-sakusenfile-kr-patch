# -*- coding: utf-8 -*-
import sys, os, struct
sys.path.insert(0, 'tools')
import mstate, asc_build as B
sys.stdout.reconfigure(encoding='utf-8')
s, v = mstate.load('work/states/crash2.state')
def mem(k):
    o, n = v[k]; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; return bytes(b)
Lo = mem('MAIN/WorkRAML'); print('스텁 자리', Lo[0x39CA0:0x39CD0].hex(' '))
n = open(sorted(__import__('glob').glob('work/disc/*Koutetsu*Track 1*.bin'))[0], 'rb')
from iso9660 import Iso
import glob
iso = Iso(glob.glob('work/disc/*Koutetsu*Track 1*.bin')[0]); E = {f[0]: f for f in iso.walk()}
d = iso.read(*E['/GMS2.BIN'][1:3]); print('디스크 스텁', d[0x39CA0:0x39CD0].hex(' '))
# 램이 파일과 어디까지 같은가
last = 0; bad = []
for i in range(0, len(d), 0x800):
    if Lo[i:i + 0x800] == d[i:i + 0x800]: last = i
    else: bad.append(i)
print('같은 끝', hex(last), '다른 섹터 수', len(bad), [hex(x) for x in bad[:10]])
for o in (0x10ADC, 0x199A6, 0x1C026): print(hex(o), Lo[o:o + 16].hex(' '), d[o:o + 16].hex(' '))
print('머리', d[:8].hex(' '), Lo[:8].hex(' '))
