# -*- coding: utf-8 -*-
"""한자·가타카나 전용 SJIS 문자열 찾기(읽기 전용)."""
import sys, os, glob, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
W = ['累積度', '記録日時', '国選択', '画面', 'ファイル', 'セレクト', '条約', 'ベルサイユ', '天候']
for pat, tag in ((r'\*Koutetsu*', 'K'),):
    p = glob.glob(SS.B + pat)[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0])
    for f in iso.walk():
        if f[0].endswith(('.MUS', '.CPK', '/', '.EP')) or f[2] < 16 or f[0].startswith('/CDDA') or 'UNIT3D' in f[0]: continue
        try: d = iso.read(f[1], f[2])
        except EOFError: continue
        for w in W:
            for enc in ('cp932', 'euc_jp', 'utf-16-be', 'iso2022_jp'):
                b = w.encode(enc)
                if enc == 'iso2022_jp': b = b[3:-3]
                o = d.find(b)
                if o >= 0: print(f[0], w, enc, hex(o))
