# -*- coding: utf-8 -*-
"""KASOU 이야기 창 흉내(KASOU 0x79C 규칙: 열 18 이상이면 줄바꿈, 단 번호 2·3·4 는 19칸째 허용, 1 = 줄바꿈).
   python tools/kasou_sim.py → 빌드 결과 전 문장을 화면 줄로 찍고 넘침·줄머리 공백·부호 뒤 공백 검사"""
import sys, os, struct, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')
import asc_build as B, ded_f, build as BD
iso, E = B.disc('F'); k = ded_f.patch(iso, E, {}, log=lambda *a: None)['/KASOU.BIN']
FB = 0x12CFC; base = 0x6060000
G = {}
for f in ('work/text/ko_extra2.tsv', 'work/text/ko_extra.tsv', 'work/text/ko_final.tsv'):
    for c in set(open(f, encoding='utf-8').read()):
        try: G.setdefault(BD.glyph(c), c)
        except Exception: pass
cell = lambda x: '　' if x == 0 else G.get(k[FB + (x + 40) * 128:FB + (x + 41) * 128], '#')
raw = [int(l.split('\t')[1], 16) for l in open('work/text/f_raw.tsv', encoding='utf-8') if l.startswith('/KASOU\t')]
tg = {}
for a in range(0, 0x12000, 4):
    x = struct.unpack_from('>I', k, a)[0]
    if base <= x < base + len(k): tg.setdefault(a, x - base)
bad = 0
for o in raw:
    q = o
    # 옮긴 줄은 포인터를 따라감
    for a, t in tg.items():
        if struct.unpack_from('>I', iso.read(*E['/KASOU.BIN'][1:3]), a)[0] == base + o: q = t; break
    lines = ['']; col = 0
    while True:
        x = struct.unpack_from('>H', k, q)[0]; q += 2
        if x == 0xFFFF: break
        if x == 1: lines.append(''); col = 0; continue
        if col >= 18 and not (x in (2, 3, 4) and col == 18): lines.append(''); col = 0
        lines[-1] += cell(x); col += 1
    for L in lines:
        prob = []
        if len(L) > 18 and not (len(L) == 19 and L[-1] in '.,'): prob.append('넘침')
        if L.startswith('　') and L.strip('　'): prob.append('줄머리 공백')
        L = L.rstrip('　')
        for p_ in ',.!?': 
            if p_ + '　' in L: prob.append('부호 뒤 공백')
        if prob: bad += 1
        if prob or '-v' in sys.argv: print('%05X' % o, '|' + L + '|', ' '.join(prob))
print('문장', len(raw), '문제 줄', bad)
