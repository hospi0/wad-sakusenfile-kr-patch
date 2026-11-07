# -*- coding: utf-8 -*-
"""시나리오별 반각 음절 수요(읽기 전용)."""
import sys, re, struct, collections
sys.path.insert(0, 'tools'); sys.stdout.reconfigure(encoding='utf-8')
import asc_build as B, ko_audit as A, unit_names as UN
k, _, _ = A.load_ko()
J = {}
for l in open('work/text/small.tsv', encoding='utf-8'):
    if l[0] != '#':
        p = l.split('\t')
        if p[0] in k: J[p[4]] = k[p[0]][0][5]
syl = lambda t: {c for c in t if '가' <= c <= '힣'}
def ko(f, kf):
    K = dict(l.rstrip('\n').split('\t', 1) for l in open(kf, encoding='utf-8') if l[0] != '#' and '\t' in l)
    return {l.split('\t')[4]: K.get(l.split('\t')[0], '') for l in open(f, encoding='utf-8') if l[0] != '#'}
D3 = ko('work/text/small3.tsv', 'work/text/ko_small3.tsv')
common = set()
for l in open('work/text/small.tsv', encoding='utf-8'):
    if l[0] != '#' and l.split('\t')[1] == 'W':
        i = l.split('\t')[0]; common |= syl(k[i][0][5]) if i in k else set()
for t in ko('work/text/small2.tsv', 'work/text/ko_small2.tsv').values(): common |= syl(t)
for t in ('자국', '동맹', '적국', '궤멸', '생존', '오디오', 'BGM 선택', '사운드 테스트'): common |= syl(t)
print('공통', len(common))
iso, E = B.disc('K'); dt = iso.read(*E['/SAKUSEN/SAKU_DT.BIN'][1:3])
pos = collections.defaultdict(set)
for l in open('work/text/small3_pos.tsv', encoding='utf-8'):
    t, g, o = l.rstrip('\n').split('\t')
    if g == 'K': pos[int(o, 16)].add(t)
ks = sorted(pos); res = []
for n in range(1, 55):
    fn = '/UNITPACK/UPK%02dC.BIN' % n
    if fn not in E: continue
    d = iso.read(*E[fn][1:3]); s = set()
    for m in re.finditer(b'\xff\xff', d):
        o = m.start()
        if o >= 40 and o % 2 == 0:
            h = UN.dec(d[o - 28:o - 19]).rstrip(' 　')
            if h in J: s |= syl(J[h])
    res.append((n, len(s), len(s | common)))
print(res[:12], '최대', max(r[2] for r in res), '평균', sum(r[2] for r in res) // len(res))
print('지명·부대(시나리오별 나눔 미확인) 전체', len({c for v in pos.values() for t in v for c in syl(D3.get(t, ''))}))
