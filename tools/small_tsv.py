# -*- coding: utf-8 -*-
"""작은 글자 이름(유닛·무기) → wad_008.tsv. 라틴·숫자만인 이름은 원어 그대로 두므로 뺀다.  python tools/small_tsv.py [--write]"""
import sys, os, glob, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, unit_names as UN
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); ent = {f[0]: f for f in iso.walk()}
d = iso.read(*ent['/GAME2.BIN'][1:3]); a = d.find(bytes([0x7F, 0x50, 1, 1]))
s = a
while s > 0 and (d[s - 1] == 0 or 1 <= d[s - 1] <= 0xAD): s -= 1
e = a
while e < len(d) and (d[e] == 0 or 1 <= d[e] <= 0xAD): e += 1
print('무기 표', hex(s), hex(e))
parts = [x for x in d[s:e].split(b'\0') if len(x) >= 3]
W = collections.Counter(UN.dec(x) for x in parts); print('무기', len(W), collections.Counter(len(x) for x in parts).most_common(4))
Wk = [t for t in W if re.fullmatch('[0-9A-Za-z.㎜/]*[ァ-ヴー]{2,}[0-9A-Za-z.]*', t) and 'ズズ' not in t and len(t) >= 4]; print(len(Wk), ' / '.join(Wk)[:1300])
units = [l.rstrip('\n').split('\t') for l in open('work/text/unit_names.tsv', encoding='utf-8')]
Uk = [u[0] for u in units if re.search('[ァ-ヴ]', u[0])]
print('유닛 가나', len(Uk))
if '--write' in sys.argv:
    n0 = sum(1 for l in open('work/text/master.tsv', encoding='utf-8')) - 1 + sum(1 for l in open('work/text/ui.tsv', encoding='utf-8')) - 1
    H = '#번호\t구분\t글자수\t쓰임\tJP\tKO\n'; rows = []
    for t in sorted(set(Uk)): rows.append(('N', 9, t))
    for t in sorted(set(Wk) - set(Uk)): rows.append(('W', 9, t))
    body = ''.join('%05d\t%s\t%d\t1\t%s\t\n' % (n0 + i, g, b, t) for i, (g, b, t) in enumerate(rows, 1))
    open('work/text/small.tsv', 'w', encoding='utf-8', newline='\n').write(H + body)
    open('my files/tsv/wad_008.tsv', 'w', encoding='utf-8', newline='\n').write(H + body)
    print('wad_008', len(rows), os.path.getsize('my files/tsv/wad_008.tsv'))
