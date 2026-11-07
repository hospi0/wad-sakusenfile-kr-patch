# -*- coding: utf-8 -*-
import sys, os, struct, re, glob, collections
sys.path.insert(0, 'tools')
import asc_build as B, sh2dis, sprite_scan as SS, mstate
sys.stdout.reconfigure(encoding='utf-8')
iso, E = B.disc('K'); c = iso.read(*E['/00000000.BIN'][1:3]); d = iso.read(*E['/GMS2.BIN'][1:3])
base = 0x6010000; a = 0x3208; n = 0
while n < 70:
    t = sh2dis.disasm_one(c, a, base); print(hex(base + a), t[0] if isinstance(t, tuple) else t, t[1] if isinstance(t, tuple) and t[1] else ''); a += 2; n += 1
raw = os.path.getsize
# 파일 마지막 섹터 뒤쪽 원본 바이트
L = E['/GMS2.BIN'][1]; n = E['/GMS2.BIN'][2]; p = glob.glob(SS.B + r'\*Koutetsu*')[0]; t = sorted(glob.glob(p + r'\*(Track 1).bin'))[0]
f = open(t, 'rb'); last = L + n // 2048; f.seek(last * 2352 + 16); sec = f.read(2048); print('마지막 섹터 뒤', sec[n % 2048:n % 2048 + 80].hex(' '), '0 아닌', sum(1 for x in sec[n % 2048:] if x))
