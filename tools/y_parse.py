# -*- coding: utf-8 -*-
"""연표 스트림 구조 분석(읽기 전용)."""
import sys, os, struct, re, collections, glob
sys.path.insert(0, 'tools'); sys.stdout.reconfigure(encoding='utf-8')
import asc_build as B, ded_build as D, mstate
NL = D.NL
iso, E = B.disc('K'); m = iso.read(*E['/W_MAP2.BIN'][1:3]); G = D.gm(iso, E)
src = open('tools/extract2.py', encoding='utf-8').read()
FX = eval(re.search(r'FX = (\{.*?\})\n', src).group(1))
L = [FX.get(i, G.get(m[0x4E128 + i * 128:0x4E128 + i * 128 + 128], '?')) for i in range(428)]
c = lambda x: L[x - 2] if 2 <= x < 430 else '#'
s, v = mstate.load('work/states/27.state')
for k in ('MAIN/WorkRAML', 'MAIN/WorkRAMH'):
    o, n = v[k]; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; p = bytes(b).find(m[0x4A0A0:0x4A0E0])
    print(k, hex(p), hex(p - 0x4A0A0))
a = 0x4A040; n = (0x4E128 - a) // 2; w = struct.unpack('>%dH' % n, m[a:a + n * 2])
st = next(i for i in range(n) if w[i:i + 5] == (3, 0xB, 3, 0xB, 0x11)); ff = w.index(0xFFFF); print('시작', st, hex(a + st * 2), '끝', ff, hex(a + ff * 2))
# 토큰
t = w[st:ff]; ent = []; i = 0; line = []; lines = []
for x in t:
    if x == 1:
        lines.append(line); line = []
    else: line.append(x)
lines.append(line)
def show(l):
    z = 0
    while z < len(l) and l[z] == 0: z += 1
    return z, ''.join('　' if x == 0 else c(x) for x in l[z:])
sh = [show(l) for l in lines]
print(len(sh), collections.Counter(z for z, q in sh).most_common(), '최대 폭', max(z + len(q) for z, q in sh))
print(sh[:14])
print(sh[-8:])
# 뒷부분 조각
q = ff + 1; fr = []
while q < n:
    e = q
    while e < n and w[e] != 0xFFFF: e += 1
    fr.append((hex(a + q * 2), e - q, ''.join('|' if x == 0 else ('·' if x == 1 else c(x)) for x in w[q:e])[:40])); q = e + 1
print(len(fr)); print(fr[:12]); print(fr[-6:]); print(collections.Counter(f[1] for f in fr).most_common(8))
print('=====')
K = {}
for l in open('work/text/ko_extra.tsv', encoding='utf-8'):
    if l[0] != '#':
        p = l.rstrip('\n').split('\t')
        if len(p) > 1: K[p[0]] = p[-1]
R = [l.rstrip('\n').split('\t') for l in open('work/text/extra.tsv', encoding='utf-8') if l[0] != '#' and l.split('\t')[1] == 'Y']
first = [r for r in R if NL in r[4]]; sent = [r for r in R if NL not in r[4]]; print('줄 있는 행', len(first), '문장 행', len(sent))
# 연도별 그룹
years = []; cur = None
for z, q in sh:
    if z == 0 and q.endswith('年'): cur = [q, []]; years.append(cur)
    elif z == 1: cur[1].append([q, []])
    elif z == 5: cur[1][-1][1].append(q)
print(len(years), sum(len(y[1]) for y in years))
ri = 0; tot = 0; bad = 0; W = 12
def wrap(t, w):
    o = []; c_ = ''
    for x in t.split(' '):
        while len(x) > w: 
            if c_: o.append(c_); c_ = ''
            o.append(x[:w]); x = x[w:]
        if c_ and len(c_) + 1 + len(x) > w: o.append(c_); c_ = x
        else: c_ = c_ + ' ' + x if c_ else x
    if c_: o.append(c_)
    return o
for y, gs in years:
    tot += len(y) + 3 + 2
    r = first[ri] if ri < len(first) else None
    need = sum(1 + (1 if b else 0) for t, b in gs)
    kl = K[r[0]].split(NL) if r else []
    jl = r[4].split(NL) if r else []
    ok = jl and jl[0].replace('　', '') == gs[0][0].replace('　', '').replace('ピ', 'ビ').replace('パ', 'バ') or True
    if len(kl) != need:
        bad += 1; print(y, '그룹', need, '번역 줄', len(kl), [t for t, b in gs], kl[:3] if kl else '')
    ri += 1
    i = 0
    for t, b in gs:
        if i < len(kl): tot += 1 + len(kl[i]) + 1; i += 1
        if b and i < len(kl):
            ls = wrap(kl[i], W); i += 1; tot += sum(5 + len(x) + 1 for x in ls)
print('행 소모', ri, len(first), '불일치', bad, '새 워드', tot, '가능', ff - st)
idx = collections.defaultdict(list)
for i in range(0, len(m) - 3, 2):
    x = struct.unpack_from('>I', m, i)[0] - 0x210000
    if 0 <= x < len(m): idx[x].append(i)
print('스트림 포인터', [hex(q) for q in idx.get(0x4A08C, [])], [(hex(o), idx.get(o, [])[:2]) for o in (0x4A040, 0x4A080, 0x4A088)])
pp = [(f[0], len(idx.get(int(f[0], 16), []))) for f in fr if f[1] > 10][:8]; print(pp, sum(1 for f in fr if f[1] > 10), sum(1 for f in fr if f[1] > 10 and idx.get(int(f[0], 16))))
