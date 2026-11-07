# -*- coding: utf-8 -*-
"""화면 판독 중 아직 번역표에 없는 진짜 글자(읽기 전용)."""
import re, sys, collections, glob
sys.stdout.reconfigure(encoding='utf-8')
known = set()
for f in ('master', 'ui', 'small', 'small2', 'place', 'extra', 'extra2'):
    for l in open('work/text/%s.tsv' % f, encoding='utf-8'):
        if l[0] != '#': known.add(re.sub('[ 　]', '', l.split('\t')[4]).replace(chr(92) + 'l', ''))
big = ''.join(known)
c = collections.OrderedDict()
for l in open('work/text/screens.tsv', encoding='utf-8'):
    st, m, y, t, ok = l.rstrip('\n').split('\t')
    k = re.sub('[ 　]', '', t)
    if 'セ' in k[:1] or re.search('[a-z]{1}[ァ-ン]|[0-9][ァ-ン]セ', k): continue
    if k in known or k in big: continue
    c.setdefault(k, st)
print(len(c)); print(' / '.join('%s(%s)' % x for x in c.items())[:2500])
