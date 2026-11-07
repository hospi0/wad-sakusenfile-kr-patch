# -*- coding: utf-8 -*-
"""ASC16 파일 이름 참조와 적재 주소 찾기(읽기 전용)."""
import sys, os, struct, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B
sys.stdout.reconfigure(encoding='utf-8')
for tag in 'KF':
    iso, E = B.disc(tag)
    for fn in ('/GAME2.BIN', '/GMS1.BIN', '/GMS2.BIN', '/0.BIN', '/00000000.BIN', '/1ST_READ.BIN', '/A0.BIN'):
        if fn not in E: continue
        d = iso.read(*E[fn][1:3])
        for m in re.finditer(rb'ASC16[A-Z0-9_]*\.?[A-Z]*', d):
            o = m.start(); print(tag, fn, hex(o), m.group(0), d[max(0, o - 24):o + 28].hex(' '))
    print(tag, sorted(n for n in E if re.search('ASC|VIEWCG/[A-Z0-9_]*\.BIN', n))[:12])
