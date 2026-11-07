# -*- coding: utf-8 -*-
"""SAKU_DT 안 반각 문자열 구역 보기(읽기 전용)."""
import sys, os, glob, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, unit_names as UN
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); ent = {f[0]: f for f in iso.walk()}
d = iso.read(*ent['/SAKUSEN/SAKU_DT.BIN'][1:3]); c = 0
for m in re.finditer(rb'[\x02-\x9f][\x01-\x9f]{7,15}', d[:0x17E00]):
    t = UN.dec(m.group(0))
    if re.search('[ァ-ヴ]{3}', t): c += 1; print(hex(m.start()), t) if c < 30 else None
print(c)
