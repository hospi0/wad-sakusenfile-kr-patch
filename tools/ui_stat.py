# -*- coding: utf-8 -*-
"""ASC16 쪽 번역 글자 수·칸 넘침 집계(읽기 전용)."""
import sys, os, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ko_audit as A, asc_table as T
sys.stdout.reconfigure(encoding='utf-8')
k, _, _ = A.load_ko()
ids = [l.split('\t')[0] for l in open('work/text/ui.tsv', encoding='utf-8') if l[0] != '#']
print('ui 줄', len(ids), '번역 있음', sum(i in k for i in ids))
print(repr(k[ids[0]])[:120])
pos = collections.defaultdict(list)
for l in open('work/text/ui_pos.tsv', encoding='utf-8'):
    i, tag, fn, o, n = l.rstrip('\n').split('\t'); pos[i].append((tag, fn, int(o, 16), int(n)))
ch = collections.Counter(); over = []
for i in ids:
    if i not in k: continue
    t = k[i][0][5]; ch.update(c for c in t if '가' <= c <= '힣')
    m = min(p[3] for p in pos[i]) if pos[i] else 0
    if A.cells(t) > m: over.append((i, m, A.cells(t), t))
print('음절', len(ch)); print('넘침', len(over), over[:14])
S = T.SHEET; print('시트', len(S), '가나한자 칸', sum(bool(re.match('[ぁ-ヶ一-龥々]', c)) for c in S), '□', S.count('□'), collections.Counter('latin' if c.isascii() else '' for c in S).most_common(2))
print(collections.Counter(p[1] for v in pos.values() for p in v).most_common(), collections.Counter(p[0] for v in pos.values() for p in v))
