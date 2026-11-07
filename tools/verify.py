# -*- coding: utf-8 -*-
"""빌드 트랙 되읽기 검산: 포인터 → 글자 번호 → 글꼴 칸 그림이 번역 글자와 같은가(읽기 전용).  python tools/verify.py"""
import sys, os, glob, struct, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso9660 import Iso
import build as Bd
sys.stdout.reconfigure(encoding='utf-8')
iso = Iso(glob.glob('work/disc/*(Track 1).bin')[0]); ent = {f[0]: f for f in iso.walk()}
o = Iso(Bd.T1); eo = {f[0]: f for f in o.walk()}
d = iso.read(*ent['/SAKUSEN/SAKU_DT.BIN'][1:3])
ptr = [struct.unpack_from('>I', d, Bd.TBL + i * 4)[0] - Bd.BASE for i in range(Bd.NPTR)]
bad = sum(1 for p in ptr if not Bd.TXT0 <= p < Bd.TBL); print('포인터 범위 밖', bad)
ko = {}
for l in open('work/text/ko_final.tsv', encoding='utf-8'):
    if l[0] != '#': i, g, v = l.rstrip('\n').split('\t', 2); ko[i] = v
inv = {}
for c in set(''.join(ko.values())):
    inv[Bd.glyph(c)] = c
F = {k: iso.read(*ent['/SAKUSEN/SAKU_F%02d.BIN' % k][1:3]) for k in range(1, 55)}
titles = [ptr[i * 5] for i in range(54)]
def dec(p, k):
    s = ''; q = p
    while True:
        x = struct.unpack_from('>H', d, q)[0]; q += 2
        if x == 0xFFFF: break
        if x == 0: s += ' '
        elif x == 1: s += '/'
        elif x < 25: s += '#'
        else: s += inv.get(F[k][x * 128:x * 128 + 128], '?')
    return s
print(dec(ptr[0], 1)); print(dec(ptr[1], 1)[:120]); print(dec(ptr[5], 2)[:60]); print(dec(ptr[265], 54)[:60])
q = sum(dec(p, 1 + i // 5 if i < 270 else 1).count('?') for i, p in enumerate(ptr[:270])); print('못 푼 글자', q)
diff = 0
for f in iso.walk():
    if f[0].endswith('/') or f[2] == 0 or f[0].endswith(('.MUS', '.CPK')): continue
    try:
        if iso.read(f[1], f[2]) != o.read(f[1], f[2]) and 'SAKU_' not in f[0]: diff += 1; print('바뀜', f[0])
    except EOFError: pass
print('SAKU 밖 바뀐 파일', diff)
