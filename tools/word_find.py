# -*- coding: utf-8 -*-
"""화면 낱말을 16×16 번호·전용 글꼴 번호로 전 파일 검색(읽기 전용).  python tools/word_find.py 낱말..."""
import sys, os, re, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B, asc_table as T
sys.stdout.reconfigure(encoding='utf-8')
S = T.SHEET
inv = collections.defaultdict(list)
for i, c in enumerate(S):
    inv[c].append(i + 2 if i >= 562 else i)
iso, E = B.disc('K')
pos = collections.defaultdict(set)
for l in open('work/text/ui_pos.tsv', encoding='utf-8'):
    i, tag, fn, o, n = l.rstrip('\n').split('\t')
    if tag == 'K': pos[fn].add(int(o, 16))
D = {}
for fn, e in E.items():
    if fn.endswith(('.MUS', '.CPK', '/')) or e[2] < 8 or fn.startswith('/CDDA'): continue
    try: D[fn] = iso.read(*e[1:3])
    except EOFError: pass
for w in sys.argv[1:]:
    print('==', w, [inv[c][:3] for c in w])
    import itertools
    hit = []
    for combo in itertools.product(*[inv[c][:3] or [0xFFF0] for c in w]):
        b = struct.pack('>%dH' % len(w), *combo)
        for fn, d in D.items():
            for m in re.finditer(re.escape(b), d):
                if m.start() % 2 == 0: hit.append((fn, hex(m.start()), m.start() in pos[fn], d[max(0, m.start() - 4):m.start()].hex(), d[m.end():m.end() + 4].hex()))
    print(len(hit), hit[:24])
