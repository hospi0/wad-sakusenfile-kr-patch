# -*- coding: utf-8 -*-
"""16×16 글꼴 번호 문자열(u16 BE, 끝 FFFF) 전 파일 전수 — 번역 자리표에 없는 줄(읽기 전용).  python tools/asc_census.py K"""
import sys, os, re, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B, asc_table as T
sys.stdout.reconfigure(encoding='utf-8')
TAG = sys.argv[1] if len(sys.argv) > 1 else 'K'
S = T.SHEET
def ch(v):
    if v == 0: return '　'
    v2 = v - 2 if v >= 564 else v
    return S[v2] if v2 < len(S) else '#'
done = collections.defaultdict(set)
for l in open('work/text/ui_pos.tsv', encoding='utf-8'):
    i, tag, fn, o, n = l.rstrip('\n').split('\t')
    if tag == TAG: done[fn].add(int(o, 16))
JK = re.compile('[ぁ-ヶ一-龥]')
iso, E = B.disc(TAG); out = []; per = collections.Counter()
SKIP = ('.MUS', '.CPK', '/', '.EP', '.DC', '.TXT', '.TSK')
for fn, e in E.items():
    if fn.endswith(SKIP) or e[2] < 8 or fn.startswith(('/CDDA', '/DAI_SF', '/VIEWMAP', '/RBG', '/FIXPOL', '/VIEWCG', '/UNIT3D', '/UNITPACK', '/EARTH')) or 'SAKU_F' in fn: continue
    try: d = iso.read(*e[1:3])
    except EOFError: continue
    n = len(d) // 2 * 2
    w = struct.unpack('>%dH' % (n // 2), d[:n]); i = 0; st = None
    ff = [k for k, x in enumerate(w) if x == 0xFFFF]
    for a, b in zip(ff, ff[1:]):
        q = w[a + 1:b]
        if not 1 <= len(q) <= 40 or max(q) >= 1192 or (a + 1) * 2 in done[fn]: continue
        t = ''.join(ch(x) for x in q).strip('　')
        if len(JK.findall(t)) >= 1 and len(set(q)) >= min(2, len(q)) and sum(1 for x in q if x < 60) * 2 <= len(q) + 2:
            out.append((fn, (a + 1) * 2, len(q), t)); per[fn] += 1
open('work/text/asc_census_%s.tsv' % TAG, 'w', encoding='utf-8', newline='\n').write(''.join('%s\t%X\t%d\t%s\n' % r for r in out))
print(len(out), per.most_common(30))
for fn, c in per.most_common(14):
    print(fn, ' | '.join('%s@%X' % (r[3], r[1]) for r in out if r[0] == fn)[:1500])
