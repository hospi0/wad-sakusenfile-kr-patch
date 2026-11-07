# -*- coding: utf-8 -*-
"""반각 글자 추가분(지형·SHINARIO 나라/부대·㎏ 무기) → my files/tsv/wad_011.tsv.  python tools/small2_tsv.py [--write]"""
import sys, os, glob, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, unit_names as UN
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
KANA = re.compile('[ァ-ヴ]')
old = set()
for f in ('work/text/small.tsv', 'work/text/place.tsv'):
    for l in open(f, encoding='utf-8'):
        if l[0] != '#': old.add(l.split('\t')[4].strip('()'))
T = collections.OrderedDict(); S = collections.OrderedDict(); W = collections.OrderedDict(); pos = []
for pat, tag, t0 in ((r'\*Koutetsu*', 'K', 0x19D50), (r'\*Sakusen*', 'F', 0x1A260)):
    p = glob.glob(SS.B + pat)[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); ent = {f[0]: f for f in iso.walk()}
    d = iso.read(*ent['/GAME2.BIN'][1:3])
    o = d.find(bytes(UN_K := [k + 1 for k, v in UN.S.items() if v == 'ダ'][:1] + [k + 1 for k, v in UN.S.items() if v == 'ミ'][:1]), t0 - 0x40)
    print(tag, '지형 시작', hex(o))
    n = 0
    q = o - 2
    while q + 10 <= len(d) and n < 90:
        f = d[q:q + 10]
        if not all(1 <= x <= 0xAD for x in f): break
        t = UN.dec(f); n += 1
        t = t.strip(); (KANA.search(t) and (T.setdefault(t, []).append((tag, q)), pos.append(('G', t, tag, '/GAME2.BIN', q, 10))))
        q += 10
    print(' 칸', n, hex(q))
    s = iso.read(*ent['/SHINARIO.BIN'][1:3])
    for i in range(0, len(s) - 9):
        f = s[i:i + 9]
        if all(1 <= x <= 0xAD for x in f) and f[0] != 1 and (i == 0 or not 1 <= s[i - 1] <= 0xAD or s[i - 1] < 0x36) and s[i + 9] == 0:
            t = UN.dec(f)
            if len(KANA.findall(t)) >= 2 and ' ' not in t.strip() or re.fullmatch('[0-9a-zA-Z]*[ァ-ヴー]+', t):
                S.setdefault(t, []).append((tag, i)); pos.append(('S', t, tag, '/SHINARIO.BIN', i, 9))
    a = d.find(bytes([0x7F, 0x50, 1, 1])); st = a
    while st > 0 and (d[st - 1] == 0 or 1 <= d[st - 1] <= 0xAD): st -= 1
    e = a
    while e < len(d) and (d[e] == 0 or 1 <= d[e] <= 0xAD): e += 1
    for x in d[st:e].split(b'\0'):
        t = UN.dec(x)
        if '㎏' in t and KANA.search(t): W.setdefault(t, [])
print('지형', len(T), list(T)[:60]); print('이름', len(S), list(S)[:80]); print('㎏', list(W))
rows = [('G', 10, t) for t in T if t not in old] + [('S', 9, t) for t in S if t not in old] + [('W', 9, t) for t in W if t not in old]
print('새 줄', len(rows))
if '--write' in sys.argv:
    H = '#번호\t구분\t글자수\t쓰임\tJP\tKO\n'; n0 = 1504
    b = ''.join('%05d\t%s\t%d\t1\t%s\t\n' % (n0 + i, g, c, t) for i, (g, c, t) in enumerate(rows, 1))
    open('work/text/small2.tsv', 'w', encoding='utf-8', newline='\n').write(H + b); open('my files/tsv/wad_011.tsv', 'w', encoding='utf-8', newline='\n').write(H + b)
    open('work/text/small2_pos.tsv', 'w', encoding='utf-8', newline='\n').write(''.join('%s\t%s\t%s\t%s\t%X\t%d\n' % r for r in pos))
    print(os.path.getsize('my files/tsv/wad_011.tsv'))
