# -*- coding: utf-8 -*-
"""반각 구역 덤프(읽기 전용). python tools/half_dump.py 파일 시작 끝 [폭]"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B, unit_names as UN
sys.stdout.reconfigure(encoding='utf-8')
N = dict(UN.names); N[1] = '_'; N[0] = '|'
iso, E = B.disc(sys.argv[5] if len(sys.argv) > 5 else 'K')
d = iso.read(*E[sys.argv[1]][1:3]); a = int(sys.argv[2], 16); b = int(sys.argv[3], 16); w = int(sys.argv[4]) if len(sys.argv) > 4 else 64
for o in range(a, b, w):
    print('%06X ' % o + ''.join(N.get(x, '<%02X>' % x) for x in d[o:o + w]))
