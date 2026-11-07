# -*- coding: utf-8 -*-
import sys, os, re, glob, struct
sys.path.insert(0, 'tools')
import asc_build as B, sprite_scan as SS, mstate
sys.stdout.reconfigure(encoding='utf-8')
for tag, pat in (('K', r'\*Koutetsu*'), ('F', r'\*Sakusen*')):
    iso, E = B.disc(tag); p = glob.glob(SS.B + pat)[0]; t = sorted(glob.glob(p + r'\*(Track 1).bin'))[0]
    F = sorted((f[1], (f[2] + 2047) // 2048, f[0]) for f in iso.walk()); sz = os.path.getsize(t) // 2352
    print(tag, '트랙 섹터', sz, '마지막 파일', F[-1], '끝', F[-1][0] + F[-1][1])
    gaps = [(a[0] + a[1], b[0] - a[0] - a[1], a[2]) for a, b in zip(F, F[1:]) if b[0] > a[0] + a[1]]; print(' 빈틈', sorted(gaps, key=lambda x: -x[1])[:5])
iso, E = B.disc('K'); d = iso.read(*E['/GMS2.BIN'][1:3])
for st in ('44', '5', '25', '26', '6'):
    s, v = mstate.load('work/states/%s.state' % st)
    o, n = v['MAIN/WorkRAML']; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; m = bytes(b)
    print(st, '파일 일치', m[:0x1000] == d[:0x1000], m[0xE0000:0xE0010] == d[0xE0000:0xE0010], m[0xE2170:0xE21A0].hex(' ')[:100])
    q = len(d)
    while q < len(m) and m[q:q + 2] == b'\x80\0': q += 2
    print('   8000 끝', hex(q), m[q:q + 16].hex(' '))
