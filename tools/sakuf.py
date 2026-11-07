# -*- coding: utf-8 -*-
"""SAKU_F 글꼴 조각과 맵 번호열(읽기 전용).  python tools/sakuf.py 스테이트"""
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

def cell(t):
    a = np.frombuffer(vr[t * 32:t * 32 + 32], np.uint8)
    return np.stack([a >> 4, a & 15], 1).reshape(8, 8)

m = np.frombuffer(vr[0x1E000:0x1E000 + 0x2000], '>u2').reshape(-1, 64)
H = 8; img = np.zeros((H * 8, 64 * 8), np.uint8)
for y in range(H):
    for x in range(64):
        t = int(m[y, x]) & 0xFFF
        if m[y, x]: img[y * 8:y * 8 + 8, x * 8:x * 8 + 8] = cell(t) * 17
Image.fromarray(img).resize((1024, 128), 0).save('work/view/map_text.png')
print([hex(int(x)) for x in m[0, :24]]); print([hex(int(x)) for x in m[1, :24]])
# 번호열을 파일에서 찾기
keys = {}
r0 = [int(x) for x in m[0] if x]
for name, seq in (('맵값', r0[:6]), ('맵값-0x1000', [x - 0x1000 for x in r0[:6]]), ('칸', [x & 0xFFF for x in r0[0:12:2]]), ('칸/2', [(x & 0xFFF) // 2 for x in r0[0:12:2]]), ('칸/4', [(x & 0xFFF) // 4 for x in r0[0:12:2]])):
    keys[name + ' BE'] = b''.join(struct.pack('>H', x) for x in seq); keys[name + ' LE'] = b''.join(struct.pack('<H', x) for x in seq)
hit = collections.Counter()
for f in fs:
    if f[0].endswith(('.MUS', '.CPK')) or f[2] < 16 or f[0].endswith('/'): continue
    try: d = iso.read(f[1], f[2])
    except EOFError: continue
    for k, b in keys.items():
        p = d.find(b)
        if p >= 0: hit[(k, f[0], hex(p))] += 1
print(list(hit)[:12])
for nm, mm in (('H', wh), ('L', wl)):
    for k, b in keys.items():
        p = mm.find(b)
        if p >= 0: print(nm, k, hex(p), mm[max(0, p - 16):p + 48].hex(' '))
# SAKU_F 를 글자로
d = iso.read(*ent['/SAKUSEN/SAKU_F01.BIN'][1:3]); print('F01', len(d), d[:32].hex(' '))
a = np.frombuffer(d, np.uint8); px = np.stack([a >> 4, a & 15], 1).reshape(-1, 8, 8) * 17
n = len(px) // 4; C = 40; pg = np.zeros((((n + C - 1) // C) * 17, C * 17), np.uint8)
for i in range(n):
    g = np.block([[px[i * 4], px[i * 4 + 1]], [px[i * 4 + 2], px[i * 4 + 3]]])
    pg[(i // C) * 17:(i // C) * 17 + 16, (i % C) * 17:(i % C) * 17 + 16] = g
Image.fromarray(pg).resize((C * 34, pg.shape[0] * 2), 0).save('work/view/sakuf.png'); print(n)
