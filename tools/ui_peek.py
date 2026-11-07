# -*- coding: utf-8 -*-
"""지정 파일 위치 근처 글자 번호 풀어 보기(읽기 전용). python tools/ui_peek.py 파일 위치 개수"""
import sys, os, glob, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
import asc_table
ch = dict(enumerate(asc_table.CH))
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); ent = {f[0]: f for f in iso.walk()}
d = iso.read(*ent[sys.argv[1]][1:3]); o = int(sys.argv[2], 16); n = int(sys.argv[3])
w = struct.unpack('>%dH' % n, d[o:o + n * 2]); t = ''
for x in w: t += ch[x] if x < 1192 else '<%X>' % x
print(t)
