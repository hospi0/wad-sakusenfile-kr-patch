# -*- coding: utf-8 -*-
"""작전파일 전용 글꼴 문자열 + 본편 GMS2 화면 제목 → work/text/extra2.tsv, my files/tsv/wad_013.tsv.  python tools/extract3.py [--write]"""
import sys, os, glob, struct, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, asc_table
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
N = chr(92) + 'l'
old = set()
for f in ('work/text/master.tsv', 'work/text/ui.tsv', 'work/text/small.tsv', 'work/text/place.tsv', 'work/text/ending.tsv', 'work/text/small2.tsv', 'work/text/extra.tsv'):
    for l in open(f, encoding='utf-8'):
        if l[0] != '#': old.add(re.sub('[　 ]', '', l.split('\t')[4]))
rows = collections.OrderedDict()
PART = re.compile('[のはをにがでとし、。]')
for l in open('work/text/f_raw.tsv', encoding='utf-8'):
    nm, o, t = l.rstrip('\n').split('\t'); t = t.replace('/', N).replace('？', N) if nm == '/KASOU' else t.replace('/', N)
    if nm == '/KASOU': t = t.replace('?', N)
    if '?' in t and nm != '/GMSFONT.BIN': continue
    k = re.sub('[　 ]', '', t)
    if k in old: continue
    if nm == '/TURNASC.BIN' and (len(t) < 7 or not PART.search(t)): continue
    if len(t) < 2: continue
    g = {'/TURNASC.BIN': 'FT', '/GMSFONT.BIN': 'FG', '/KASOU': 'FS', '/GAMEOVER': 'FO'}[nm]
    rows.setdefault(t, g)
# 본편 GMS2 화면 제목
pk = glob.glob(SS.B + r'\*Koutetsu*')[0]; ik = Iso(sorted(glob.glob(pk + r'\*(Track 1).bin'))[0]); ek = {f[0]: f for f in ik.walk()}
rk = lambda n: ik.read(*ek[n][1:3])
mp = rk('/VIEWCG/ASC16MAP.BIN'); cg = rk('/VIEWCG/ASC16X16.BIN') + rk('/VIEWCG/ASC16_2.BIN')
w = struct.unpack('>%dH' % (len(mp) // 2), mp); G = {}
for i in range(len(w) // 4):
    g = b''.join(cg[(t - 0x800) * 32:(t - 0x800) * 32 + 32] for t in w[i * 4:i * 4 + 4]); G.setdefault(g, asc_table.SHEET[i])
d = rk('/GMS2.BIN'); L = [G.get(d[0xD95C + i * 128:0xD95C + i * 128 + 128], '?') for i in range(99)]
W = struct.unpack('>%dH' % (len(d) // 2), d[:len(d) // 2 * 2]); ff = [i for i, x in enumerate(W) if x == 0xFFFF]
kt = []
for a, b in zip(ff, ff[1:]):
    q = W[a + 1:b]
    if 2 <= len(q) <= 30 and all(v <= 99 for v in q):
        t = ''.join(L[v - 1] if v else '　' for v in q).strip('　')
        if re.search('[ァ-ヶ一-龥]', t) and re.sub('　', '', t) not in old: kt.append(((a + 1) * 2, t))
print('본편 화면 글', kt[:40])
print(collections.Counter(rows.values()), sum(len(t) for t in rows))
for g in ('FT', 'FG', 'FS', 'FO'):
    print(g, [t[:30] for t, x in rows.items() if x == g][:14])
if '--write' in sys.argv:
    H = '#번호\t구분\t글자수\t쓰임\tJP\tKO\n'; n0 = 1769; b = ''; i = 0
    FW = (('画?', '画面'), ('ラパウル', 'ラバウル'), ('ポウエイ', 'ボウエイ'), ('へンダ', 'ヘンダ'), ('パルジ', 'バルジ'), ('スラピア', 'スラビア'))
    def fx(t):
        for x, y in FW: t = t.replace(x, y)
        return t
    seen = set(old)
    for o, t in kt:
        t = fx(t)
        if '?' in t or len(t) < 3 or re.sub('　', '', t) in seen: continue
        seen.add(re.sub('　', '', t)); i += 1; b += '%05d\tKG\t%d\t1\t%s\t\n' % (n0 + i, len(t), t)
    for t, g in rows.items():
        t = fx(t)
        if re.sub('[　 ]', '', t) in seen: continue
        seen.add(re.sub('[　 ]', '', t)); i += 1; b += '%05d\t%s\t%d\t1\t%s\t\n' % (n0 + i, g, max(len(x) for x in t.split(N)), t)
    open('work/text/extra2.tsv', 'w', encoding='utf-8', newline='\n').write(H + b)
    print(i, len(b.encode()))
