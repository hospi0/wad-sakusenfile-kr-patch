# -*- coding: utf-8 -*-
"""SENSHI.TXT·지형 이름·SHINARIO 나라 이름 확인(읽기 전용)."""
import sys, os, glob, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, unit_names as UN
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); ent = {f[0]: f for f in iso.walk()}
t = iso.read(*ent['/SENSHI.TXT'][1:3]).decode('cp932', 'replace')
L = t.splitlines(); print(len(t), len(L)); print(L[:14]); print(L[40:46]); print(L[-4:])
d = iso.read(*ent['/GAME2.BIN'][1:3])
print(UN.dec(d[0x19D30:0x19F40]).replace('<00>', '|')[:900])
s = iso.read(*ent['/SHINARIO.BIN'][1:3]); print(len(s)); print(UN.dec(s[:0x180]).replace('<00>', '|')[:700])
