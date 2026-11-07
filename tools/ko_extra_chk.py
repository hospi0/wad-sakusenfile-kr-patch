# -*- coding: utf-8 -*-
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
N = chr(92) + 'l'
ko = dict(l.rstrip('\n').split('\t', 1) for l in open('work/text/ko_extra.tsv', encoding='utf-8') if l[0] != '#')
jp = {}
for l in open('work/text/extra.tsv', encoding='utf-8'):
    if l[0] != '#': c = l.rstrip('\n').split('\t'); jp[c[0]] = c
print(len(ko), len(jp), sorted(set(jp) - set(ko)))
print('T 줄바꿈 다름', [i for i, c in jp.items() if c[1] == 'T' and i in ko and c[4].count(N) != ko[i].count(N)])
print('M 칸 초과 12', [(i, ko[i], len(ko[i])) for i, c in jp.items() if c[1] == 'M' and i in ko and len(ko[i]) > 12])
print('가나 한자', [i for i, v in ko.items() if re.search('[ぁ-ヶ一-龥]', v)])
