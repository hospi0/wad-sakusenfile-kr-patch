# -*- coding: utf-8 -*-
"""작전파일 연표 풀기: 본편 연표와 다른 줄 찾기(읽기 전용).  python tools/f_year.py"""
import sys, os, glob, struct, re, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, asc_table
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
src = open('tools/extract2.py', encoding='utf-8').read()
FX = eval(re.search(r'FX = (\{.*?\})\n', src).group(1))
def op(pat):
    p = glob.glob(SS.B + pat)[0]; i = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); return i, {f[0]: f for f in i.walk()}
a, ea = op(r'\*Koutetsu*'); b, eb = op(r'\*Sakusen*')
ra = lambda n: a.read(*ea[n][1:3]); rb = lambda n: b.read(*eb[n][1:3])
mp = ra('/VIEWCG/ASC16MAP.BIN'); w = struct.unpack('>%dH' % (len(mp) // 2), mp)
FIX = {283: 'ヘ', 317: 'バ', 322: 'ボ', 463: 'ビ', 438: 'ピ'}
G = {}
for cg in (ra('/VIEWCG/ASC16X16.BIN') + ra('/VIEWCG/ASC16_2.BIN'), rb('/VIEWCG/ASC16X16.BIN') + rb('/VIEWCG/ASC16_2.BIN')):
    for i in range(len(w) // 4):
        c = FIX.get(i, asc_table.SHEET[i])
        if c != '□':
            g = b''.join(cg[(t - 0x800) * 32:(t - 0x800) * 32 + 32] for t in w[i * 4:i * 4 + 4]); G.setdefault(g, c)
km = ra('/W_MAP2.BIN')
for i in range(428):
    g = km[0x4E128 + i * 128:0x4E128 + i * 128 + 128]
    if i in FX: G[g] = FX[i]
d = rb('/W_MAP2.BIN'); base = 0x2CC1C
L = []
for i in range(600):
    if base + i * 128 + 128 > len(d): break
    L.append(G.get(d[base + i * 128:base + i * 128 + 128], '?'))
KL = [FX.get(i, G.get(km[0x4E128 + i * 128:0x4E128 + i * 128 + 128], '?')) for i in range(428)]
same = sum(1 for x, y in zip(L, KL) if x == y or x == '?')
print('글자 번호 순서 일치', same, 428, ''.join(KL[28:60]))
L = KL + L[428:]
a0 = 0x2A864; n = (base - a0) // 2; v = struct.unpack('>%dH' % n, d[a0:a0 + n * 2])
s = ''
for x in v:
    if x == 0: s += '|'
    elif x == 1: s += '　'
    elif 2 <= x < len(L) + 2: s += L[x - 2]
    else: s += '#'
old = {l.split('\t')[4] for l in open('work/text/extra.tsv', encoding='utf-8') if l[0] != '#'}
parts = [p.strip('|　').replace('|', '　') for p in s.split('#')]
new = [p for p in parts if len(p) >= 8 and re.search('[ぁ-ん]', p) and p not in old]
print('문장', len(parts), '새 줄', len(new), sum(len(p) for p in new))
new = [re.sub('　{2,}', ' / ', p) for p in new]
print(' ## '.join(new)[:3000])
NLc = chr(10)
open('work/text/f_year.txt', 'w', encoding='utf-8', newline=NLc).write(NLc.join(new) + NLc)
