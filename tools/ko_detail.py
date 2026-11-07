# -*- coding: utf-8 -*-
"""검사 상세 출력(읽기 전용)."""
import sys, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ko_audit as A
sys.stdout.reconfigure(encoding='utf-8')
m = A.load_master(); k, _, _ = A.load_ko()
print('=== 코드'); print(m['00075'][4], '→', k['00075'][0][5])
print('=== 괄호')
for i, c in m.items():
    jp = c[4]; ko = k[i][0][5]
    for a in '(（「『［':
        if (a in jp) != (a in ko):
            for mm in re.finditer('[「『（(［」』）)］]', jp + ' || ' + ko): pass
            g = lambda s: ''.join(re.findall('.{0,5}[「『（(［].{0,8}', s))[:44]
            print(i, g(jp), '→', g(ko)); break
print('=== 가나 한자')
for i, c in m.items():
    ko = k[i][0][5]
    if re.search('[ぁ-ヶ一-龥]', ko):
        print(i, c[1], repr(c[4][:30]), '→', repr(ko[:50]) if len(ko) < 60 else [x for x in re.findall('.{0,6}[ぁ-ヶ一-龥]+.{0,6}', ko)])
print('=== 앞 공백 원문 대조')
d = [(i) for i, c in m.items() if k[i][0][5].startswith('　') != c[4].startswith('　')]
print(len(d), d[:10], [k[i][0][5][:12] for i in d[:4]])
print('=== 칸 초과')
for i, c in m.items():
    ko = k[i][0][5]; b = int(c[2])
    if c[1][:1] in 'UNW' and A.cells(ko) > b: print(i, c[1], b, A.cells(ko), c[4][:18], '→', ko[:26])
