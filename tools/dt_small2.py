# -*- coding: utf-8 -*-
"""SAKU_DT·GAME2 반각 문자열 구조 보기(읽기 전용)."""
import sys, os, glob, re, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, unit_names as UN
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); ent = {f[0]: f for f in iso.walk()}
d = iso.read(*ent['/SAKUSEN/SAKU_DT.BIN'][1:3])
print(d[0x14380:0x14420].hex(' '))
print(UN.dec(d[0x14380:0x14440]).replace('<00>', '|'))
g = iso.read(*ent['/GAME2.BIN'][1:3])
print(UN.dec(g[0x1AF90:0x1B040]).replace('<00>', '|'))
print(UN.dec(g[0x7B5B0:0x7B680]).replace('<00>', '|'))
