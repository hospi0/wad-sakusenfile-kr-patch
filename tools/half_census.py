# -*- coding: utf-8 -*-
"""반각(8×8 u8) 가나 문자열 전 파일 전수(읽기 전용). 값 = 시트 번호+1, 01 = 빈칸.  python tools/half_census.py [K|F]
   표에 아는 줄/모르는 줄을 파일별로 센다. 결과 work/text/half_census_<K|F>.tsv"""
import sys, os, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B, unit_names as UN
sys.stdout.reconfigure(encoding='utf-8')
TAG = sys.argv[1] if len(sys.argv) > 1 else 'K'
N = dict(UN.names); N[1] = ' '
KV = {k for k, c in N.items() if re.match('[ァ-ヴー]', c)}
known = set()
for f in ('small', 'small2', 'small3'):
    for l in open('work/text/%s.tsv' % f, encoding='utf-8'):
        if l[0] != '#': known.add(l.split('\t')[4])
OK = bytes(sorted(N))
rx = re.compile(b'[' + re.escape(OK) + b']{2,}')
iso, E = B.disc(TAG)
rows = []; per = collections.Counter(); unk = collections.Counter()
for fn, e in E.items():
    if fn.endswith(('.MUS', '.CPK', '/', '.EP', '.DC')) or e[2] < 8 or fn.startswith('/CDDA') or 'UNIT3D' in fn or 'ASC' in fn: continue
    try: d = iso.read(*e[1:3])
    except EOFError: continue
    for m in rx.finditer(d):
        b = m.group()
        if sum(x in KV for x in b) < 2 or max(map(lambda r: len(r.group()), re.finditer(b'[' + re.escape(bytes(sorted(KV))) + b']+', b)), default=0) < 2: continue
        t = ''.join(N[x] for x in b).strip()
        if len(b) > 20: continue                        # 표 조각·잡음
        k = t in known
        rows.append((fn, m.start(), len(b), k, t)); per[fn] += 1
        if not k: unk[t] += 1
open('work/text/half_census_%s.tsv' % TAG, 'w', encoding='utf-8', newline='\n').write(''.join('%s\t%X\t%d\t%d\t%s\n' % r for r in rows))
print('줄', len(rows), '모름 고유', len(unk))
print(per.most_common(30))
fk = collections.Counter(r[0] for r in rows if not r[3]); print('모름 파일별', fk.most_common(30))
print(' / '.join(t for t, n in unk.most_common(150)))
