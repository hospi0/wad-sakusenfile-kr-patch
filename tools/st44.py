# -*- coding: utf-8 -*-
"""44번 스테이트 스프라이트 출처(읽기 전용)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS
sys.stdout.reconfigure(encoding='utf-8')
import bisect
K, ki = SS.blob(r'\*Koutetsu*')
for a, w, h, bits, d in SS.sprites('work/states/44.state'):
    if w * h < 400 or len(set(d)) < 3: continue
    o = len(d) // 3; p = K.find(d[o:o + 48]); r = '-'
    if p >= 0:
        i = bisect.bisect_right([x[0] for x in ki], p) - 1; r = '%s %X' % (ki[i][1], p - ki[i][0] - o)
    print(w, h, bits, r)
