# -*- coding: utf-8 -*-
"""반각 가나 낱말 정밀 전수(읽기 전용): 가나 3자 이상(같은 글자 연속 없음) + 앞이 00/01/라틴·숫자 + 뒤가 00/01/라틴·숫자.
   아는 표(small·small2·small3·place·romaji)와 대조.  python tools/half_census2.py K"""
import sys, os, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B, unit_names as UN
sys.stdout.reconfigure(encoding='utf-8')
TAG = sys.argv[1] if len(sys.argv) > 1 else 'K'
N = dict(UN.names); N[1] = ' '
KV = bytes(sorted(k for k, c in N.items() if re.match('[ァ-ヴー]', c)))
AL = bytes(sorted(k for k, c in N.items() if re.match('[0-9A-Za-z. ]', c))) + b'\0\xff'
rx = re.compile(b'[' + re.escape(KV) + b']{3,}')
K = set(); P = set()
for f in ('small', 'small2', 'small3'):
    for l in open('work/text/%s.tsv' % f, encoding='utf-8'):
        if l[0] != '#': K.add(l.split('\t')[4])
for l in open('work/text/place.tsv', encoding='utf-8'):
    if l[0] != '#': P.add(l.split('\t')[4].strip('()'))
ks = '|'.join(K); ps = '|'.join(P)
SK = ('.MUS', '.CPK', '/', '.EP', '.DC', '.TXT', '.TSK')
iso, E = B.disc(TAG); H = collections.defaultdict(lambda: collections.defaultdict(list))
for fn, e in E.items():
    if fn.endswith(SK) or e[2] < 8 or fn.startswith(('/CDDA', '/DAI_SF', '/VIEWMAP', '/RBG', '/FIXPOL', '/VIEWCG', '/UNIT3D')) or 'SAKU_F' in fn or 'LOAD' in fn: continue
    try: d = iso.read(*e[1:3])
    except EOFError: continue
    for m in rx.finditer(d):
        a, b = m.span()
        if a == 0 or b >= len(d) or d[b] not in AL: continue
        w = ''.join(N[x] for x in m.group())
        if re.search(r'(.)\1', w): continue
        st = 'K' if w in ks else 'P' if w in ps else '?'
        H[fn.split('/')[-1][:3] if 'UPK' in fn else fn][(st, w)].append(a)
out = []
for fn, v in H.items():
    c = collections.Counter(k[0] for k in v)
    print(fn, dict(c), '| ?:', ' '.join('%s@%X' % (k[1], p[0]) for k, p in sorted(v.items(), key=lambda x: -len(x[1])) if k[0] == '?')[:1400])
    for k, p in v.items(): out.append('%s\t%s\t%s\t%d\t%X\n' % (fn, k[0], k[1], len(p), p[0]))
open('work/text/half_census2_%s.tsv' % TAG, 'w', encoding='utf-8', newline='\n').write(''.join(out))
