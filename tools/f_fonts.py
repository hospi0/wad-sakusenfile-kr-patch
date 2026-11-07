# -*- coding: utf-8 -*-
"""작전파일 전용 글꼴 파일 판독률과 내용(읽기 전용).  python tools/f_fonts.py"""
import sys, os, glob, struct, hashlib, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, asc_table, extract as X
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
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
        if c == '□': continue
        g = b''.join(cg[(t - 0x800) * 32:(t - 0x800) * 32 + 32] for t in w[i * 4:i * 4 + 4]); G.setdefault(hashlib.md5(g).hexdigest()[:10], c)
sf = X.sf_table(); G.update({k: v for k, v in sf.items() if k not in G})
mainf = dict(l.rstrip('\n').split('\t') for l in open('work/text/glyph_final.tsv', encoding='utf-8'))
for k, v in mainf.items(): G.setdefault(k, v)
print('글자 그림', len(G))
for fn in ('/TURNASC.BIN', '/GMSFONT.BIN', '/ENDFONT0.BIN'):
    d = rb(fn); n = len(d) // 128
    L = [G.get(hashlib.md5(d[i * 128:i * 128 + 128]).hexdigest()[:10], '?') for i in range(n)]
    print(fn, n, L.count('?'), ''.join(L)[:300])
for fn in ('/W_MAP2.BIN', '/KASOU.BIN', '/GMS1.BIN', '/GAMEOVER.BIN', '/UNITDATA.BIN', '/STAFF.BIN'):
    if fn not in eb: continue
    d = rb(fn); best = collections.Counter()
    for al in range(0, 128, 2):
        for i in range(al, len(d) - 128, 128):
            if hashlib.md5(d[i:i + 128]).hexdigest()[:10] in G: best[al] += 1
    if not best: print(fn, '없음'); continue
    al, c = best.most_common(1)[0]
    pos = [i for i in range(al, len(d) - 128, 128) if hashlib.md5(d[i:i + 128]).hexdigest()[:10] in G]
    s, e = pos[0], pos[-1]
    L = [G.get(hashlib.md5(d[i:i + 128]).hexdigest()[:10], '?') for i in range(s, e + 128, 128)]
    print(fn, len(d), hex(s), len(L), L.count('?'), ''.join(L)[:320])
