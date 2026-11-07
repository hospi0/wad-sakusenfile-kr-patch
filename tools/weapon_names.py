# -*- coding: utf-8 -*-
"""UNITPACK 안 유닛 이름 외 작은 글자 문자열(무기 등) 전수(읽기 전용)."""
import sys, os, glob, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, unit_names as UN
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
units = {l.split('\t')[0] for l in open('work/text/unit_names.tsv', encoding='utf-8')}
U = collections.Counter(); L = collections.Counter()
for pat in (r'\*Koutetsu*', r'\*Sakusen*'):
    p = glob.glob(SS.B + pat)[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0])
    for f in iso.walk():
        if '/UNITPACK/UPK' not in f[0]: continue
        d = iso.read(f[1], f[2])
        for m in re.finditer(rb'[\x02-\xad][\x01-\xad]{3,18}', d):
            t = UN.dec(m.group(0))
            if '<' in t or t in units or not re.search('[ァ-ヴ㎜]', t): continue
            U[t] += 1; L[len(m.group(0))] += 1
print(len(U), L.most_common(8)); print(' / '.join(t for t, n in U.most_common(170))[:2600])
open('work/text/weapon_names.tsv', 'w', encoding='utf-8', newline='\n').write(''.join('%s\t%d\n' % x for x in U.most_common()))
