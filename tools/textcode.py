# -*- coding: utf-8 -*-
"""화면 글자 → ASC16_2 글꼴 번호열 → 디스크·메모리에서 문장 찾기(읽기 전용).  python tools/textcode.py 스테이트"""
import sys, os, re, glob, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate
from iso9660 import Iso
import numpy as np
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
s, v = mstate.load(sys.argv[1])

def mem(k):
    o, n = v[k]; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; return bytes(b)

vr = mem('VDP2/VRAM'); wh = mem('MAIN/WorkRAMH'); wl = mem('MAIN/WorkRAML')
R = r'C:\claude\roms\ss\World Advanced Daisenryaku\World Advanced Daisenryaku - Koutetsu no Senpuu (Japan) (Rev A) (10M)'
iso = Iso(glob.glob(R + r'\*(Track 1).bin')[0]); fs = iso.walk(); ent = {f[0]: f for f in fs}
F = iso.read(*ent['/VIEWCG/ASC16_2.BIN'][1:3]); print(len(F), F[:32].hex(' '))
m = np.frombuffer(vr[0x1E000:0x1E000 + 0x2000], '>u2')
rows = []
for y in range(0, 64):
    r = m[y * 64:(y + 1) * 64]
    if r.any(): rows.append((y, [int(x) for x in r]))
print('맵 줄', [(y, sum(1 for x in r if x)) for y, r in rows])
pos = {}
seqs = []
for y, r in rows:
    seq = []
    for x in range(0, 64, 2):
        t = r[x]
        if not t or (t & 0xFFF) * 32 + 128 > len(vr): continue
        c = vr[(t & 0xFFF) * 32:(t & 0xFFF) * 32 + 128]
        if not c.strip(b'\0'): seq.append(-2); continue
        a = F.find(c[:64]); seq.append(a)
    seqs.append((y, seq))
    print(y, [hex(a) if a >= 0 else a for a in seq][:40])
# 글꼴 그려 보기: 시작 위치·간격
hdr = 0x20
n = (len(F) - hdr) // 128
a = np.frombuffer(F[hdr:hdr + n * 128], np.uint8); px = np.stack([a >> 4, a & 15], 1).reshape(n, 16, 16) * 17
C = 40; Rn = (n + C - 1) // C
pg = np.zeros((Rn * 17, C * 17), np.uint8)
for i in range(n): pg[(i // C) * 17:(i // C) * 17 + 16, (i % C) * 17:(i % C) * 17 + 16] = px[i]
Image.fromarray(pg).resize((C * 34, Rn * 34), 0).save('work/view/asc16.png'); print(n)
