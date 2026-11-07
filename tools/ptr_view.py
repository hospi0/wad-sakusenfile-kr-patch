# -*- coding: utf-8 -*-
"""포인터 표 배치 보기(읽기 전용)."""
import sys, os, glob, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\claude\roms\ss\World Advanced Daisenryaku'
for tag, pat, a0 in (('K', r'\*Koutetsu*', 0x25DC0), ('F', r'\*Sakusen*', 0x1C000)):
    p = glob.glob(B + pat)[0]
    iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); ent = {f[0]: f for f in iso.walk()}
    d = iso.read(*ent['/SAKUSEN/SAKU_DT.BIN'][1:3])
    v = struct.unpack('>%dI' % ((len(d) - a0) // 4), d[a0:a0 + (len(d) - a0) // 4 * 4])
    print(tag, hex(len(d)), [hex(x - 0x2C0000) if 0x2C0000 <= x < 0x2C0000 + len(d) else hex(x) for x in v[:56]])
    good = [i for i, x in enumerate(v) if 0x2C0000 <= x < 0x2C0000 + len(d)]
    print(len(v), len(good), hex(a0 + good[0] * 4), hex(a0 + good[-1] * 4))
