# -*- coding: utf-8 -*-
"""GAME2 등 16×16 번호 문자열 후보 전수: FFFF 로 끝나는 연속 값(앞 경계 무관), 일본어 비율로 거름, 자리표 표시.  python tools/asc_runs.py 파일 [시작 끝]"""
import sys, os, re, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B, asc_table as T
sys.stdout.reconfigure(encoding='utf-8')
S = T.SHEET
TAG = os.environ.get('TAG', 'K')
def ch(v):
    if v == 0: return '　'
    v2 = v - 2 if v >= 564 else v
    return S[v2] if v2 < len(S) else '#'
pos = collections.defaultdict(dict)
for l in open('work/text/ui_pos.tsv', encoding='utf-8'):
    i, tag, fn, o, n = l.rstrip('\n').split('\t')
    if tag == TAG: pos[fn][int(o, 16)] = int(n)
iso, E = B.disc(TAG)
fn = sys.argv[1]; d = iso.read(*E[fn][1:3]); a = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0; b = int(sys.argv[3], 16) if len(sys.argv) > 3 else len(d)
a &= ~1; W = struct.unpack('>%dH' % ((b - a) // 2), d[a:a + (b - a) // 2 * 2])
ff = [i for i, x in enumerate(W) if x == 0xFFFF]; R = []
for e in ff:
    s = e
    while s > 0 and W[s - 1] < 1190 and e - s < 40: s -= 1
    q = W[s:e]
    if not q: continue
    # 앞쪽 잡음 빼기: 끝에서 거꾸로 일본어 글자가 이어지는 데까지
    t = ''.join(ch(x) for x in q)
    m = re.search('[ぁ-ヶ一-龥Ａ-Ｚ０-９A-Za-z0-9・、。ー？！　]*$', t)
    t2 = m.group()
    if not re.search('[ぁ-ヶ一-龥]', t2): continue
    o = a + (e - len(t2)) * 2
    cov = any(p <= o < p + 2 * n + 2 for p, n in pos[fn].items())
    if not cov: R.append((o, t2))
seen = set()
for o, t in R:
    print('%X %s' % (o, t.strip('　')))
print(len(R))
