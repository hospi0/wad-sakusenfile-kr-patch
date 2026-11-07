# -*- coding: utf-8 -*-
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ko_audit as A
sys.stdout.reconfigure(encoding='utf-8')
m = A.load_master(); k, _, _ = A.load_ko()
for j, w in (('ギンワシ', 'ギンワシ'), ('ホクダル', 'ホクダル'), ('アントワープ', 'アントワープ'), ('シリー', 'シリー'), ('チラチャップ', 'チラチャップ'), ('ビシェンプール', 'ビシェンプール'), ('アーメダバード', 'アーメダバード')):
    for i, c in m.items():
        if c[1][:1] in 'KFE' and j in c[4]:
            p = c[4].index(j); r = p / len(c[4]); ko = k[i][0][5]; q = int(r * len(ko))
            print(j, i, ko[max(0, q - 12):q + 12]); break
for i in ('00115', '01493', '00298', '00427'):
    print(i, m[i][4][:70], '→', k[i][0][5][:90])
for w in ('궤멸', '군집단', '정면군', '우리나라'):
    print(w, [i for i in m if w in k[i][0][5]][:30])
