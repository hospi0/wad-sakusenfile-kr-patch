# -*- coding: utf-8 -*-
"""시나리오별 번역 글자 종류 수(글꼴 칸 예산, 읽기 전용).  python tools/saku_font_need.py"""
import sys, os, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ko_audit as A
sys.stdout.reconfigure(encoding='utf-8')
m = A.load_master(); k, _, _ = A.load_ko()
sc = collections.defaultdict(set); cnt = collections.Counter()
for l in open('work/text/master_pos.tsv', encoding='utf-8'):
    if l[0] == '#': continue
    i, tag, s, o, n = l.rstrip('\n').split('\t')
    t = re.sub(r'\l|<[0-9A-F]+>', '', k[i][0][5]); sc[(tag, int(s))] |= set(t); cnt[(tag, int(s))] += len(t)
v = sorted((len(x), key) for key, x in sc.items())
print(len(sc), '글자 종류 최소·최대', v[0], v[-1], '평균', sum(a for a, _ in v) // len(v))
print('상위', v[-8:]); print('250 넘음', sum(1 for a, _ in v if a > 250))
print('긴 시나리오 칸', cnt.most_common(4))
