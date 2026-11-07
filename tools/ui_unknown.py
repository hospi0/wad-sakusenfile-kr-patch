# -*- coding: utf-8 -*-
"""□ 글자 번호와 문맥(읽기 전용)."""
import sys, os, glob, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, asc_table
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
CH = asc_table.CH
rows = [l.rstrip('\n').split('\t') for l in open('work/text/ui_raw.tsv', encoding='utf-8')]
isos = {}
for pat, tag in ((r'\*Koutetsu*', 'K'), (r'\*Sakusen*', 'F')):
    p = glob.glob(SS.B + pat)[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); isos[tag] = (iso, {f[0]: f for f in iso.walk()})
ctx = collections.defaultdict(set)
for tag, fn, o, n, t in rows:
    if '□' not in t or fn in ('/W_MAP2.BIN', '/BTS3DPRM.BIN', '/GMS2.BIN'): continue
    iso, ent = isos[tag]; d = iso.read(*ent[fn][1:3]); o = int(o, 16); n = int(n)
    w = struct.unpack('>%dH' % n, d[o:o + n * 2])
    s = ''.join(CH[x] if x else '　' for x in w)
    for i, x in enumerate(w):
        if CH[x] == '□': ctx[x].add(s[max(0, i - 7):i + 7])
for k in sorted(ctx): print(k, sorted(ctx[k])[:4])
print(len(ctx))
