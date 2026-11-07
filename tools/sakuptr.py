# -*- coding: utf-8 -*-
"""SAKU_DT 문장 위치를 가리키는 포인터 찾기(읽기 전용)."""
import sys, os, glob, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
R = r'C:\claude\roms\ss\World Advanced Daisenryaku\World Advanced Daisenryaku - Koutetsu no Senpuu (Japan) (Rev A) (10M)'
iso = Iso(glob.glob(R + r'\*(Track 1).bin')[0]); fs = iso.walk(); ent = {f[0]: f for f in fs}
L = [l.split('\t') for l in open('work/text/saku.tsv', encoding='utf-8')]
offs = [int(l[2], 16) for l in L]
d = iso.read(*ent['/SAKUSEN/SAKU_DT.BIN'][1:3])
hit = collections.Counter()
for base in (0, 0x60C0000, 0x200000 + 0xC0000, 0x2C0000, 0x06000000):
    for fmt, nm in (('>I', 'BE32'),):
        keys = {struct.pack(fmt, o + base) for o in offs}
        idx = [i for i in range(0, len(d) - 3, 2) if d[i:i + 4] in keys]
        print('DT 안', hex(base), nm, len(idx), [hex(i) for i in idx[:6]])
ks = {struct.pack('>H', o & 0xFFFF) for o in offs}
for f in fs:
    if not f[0].endswith(('.BIN', '.PRG', '.DAT', '.TBL')) or f[2] > 3000000 or f[2] < 64: continue
    try: b = iso.read(f[1], f[2])
    except EOFError: continue
    for base in (0, 0x200000 + 0xC0000, 0x60C0000):
        c = sum(1 for o in offs[:60] if struct.pack('>I', o + base) in b)
        if c >= 6: print(f[0], f[2], hex(base), c)
print('머리 앞 표', [hex(x) for x in struct.unpack('>24I', d[0x17E98 - 96:0x17E98])][:8])
sizes = sorted(collections.Counter(int(l[3]) for l in L).items())[-4:]; print(sizes)
