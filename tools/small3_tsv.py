# -*- coding: utf-8 -*-
"""SAKU_DT 세력·거점 반각 이름(9칸+00)·GAME2 반각 낱말 → work/text/small3.tsv.  python tools/small3_tsv.py [--write]"""
import sys, os, glob, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, unit_names as UN
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
old = set()
for f in ('small', 'small2', 'place'):
    for l in open('work/text/%s.tsv' % f, encoding='utf-8'):
        if l[0] != '#': old.add(l.split('\t')[4].strip('()'))
U = collections.OrderedDict(); pos = []
for pat, tag, a, b in ((r'\*Koutetsu*', 'K', 0x13C00, 0x17E98), (r'\*Sakusen*', 'F', 0x13000, 0x1401C)):
    p = glob.glob(SS.B + pat)[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); ent = {f[0]: f for f in iso.walk()}
    d = iso.read(*ent['/SAKUSEN/SAKU_DT.BIN'][1:3])
    for i in range(a, b - 10):
        f = d[i:i + 9]
        if d[i + 9] == 0 and d[i - 1] == 0 and all(1 <= x <= 0xAD for x in f) and f[0] != 1:
            t = UN.dec(f)
            if re.search('[ァ-ヴ]{2}', t) and '<' not in t:
                U.setdefault(t, 0); U[t] += 1; pos.append((t, tag, i))
print(len(U), len(pos)); new = [t for t in U if t not in old]; print(len(new)); print(' / '.join(new)[:2500])
if '--write' in sys.argv:
    W = ['ジコク', 'ドウメイ', 'テキコク', 'カイメツ', 'セイゾン', 'オーディオ', 'BGMセレクト', 'サウンドテスト']
    rows = [(t, 4 if len(t) <= 4 else 10) for t in W] + [(t, 9) for t in new if t not in W]
    H = '#번호\t구분\t글자수\t쓰임\tJP\tKO\n'; n0 = 1871
    b = ''.join('%05d\tD\t%d\t1\t%s\t\n' % (n0 + i, c, t) for i, (t, c) in enumerate(rows, 1))
    open('work/text/small3.tsv', 'w', encoding='utf-8', newline='\n').write(H + b)
    open('work/text/small3_pos.tsv', 'w', encoding='utf-8', newline='\n').write(''.join('%s\t%s\t%X\n' % r for r in pos))
    print(len(rows))
