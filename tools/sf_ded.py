# -*- coding: utf-8 -*-
"""작전 전용 글꼴 문자열 ↔ 번역 대응·칸 넘침 측정(읽기 전용)."""
import sys, re, collections
sys.path.insert(0, 'tools'); sys.stdout.reconfigure(encoding='utf-8')
import ko_audit as A
N = chr(92) + 'l'
FW = (('画?', '画面'), ('ラパウル', 'ラバウル'), ('ポウエイ', 'ボウエイ'), ('へンダ', 'ヘンダ'), ('パルジ', 'バルジ'), ('スラピア', 'スラビア'))
def nz(t):
    for a, b in FW: t = t.replace(a, b)
    return re.sub('[　 /?？]', '', t.replace(N, ''))
def table():
    J = {}
    k, _, _ = A.load_ko()
    for f in ('master', 'ui'):
        for l in open('work/text/%s.tsv' % f, encoding='utf-8'):
            if l[0] != '#':
                p = l.rstrip('\n').split('\t')
                if p[0] in k: J.setdefault(nz(p[4]), k[p[0]][0][5])
    K = {}
    for f in ('ko_extra', 'ko_extra2'):
        for l in open('work/text/%s.tsv' % f, encoding='utf-8'):
            if l[0] != '#':
                p = l.rstrip('\n').split('\t')
                if len(p) > 1: K[p[0]] = p[-1]
    for f in ('extra', 'extra2'):
        for l in open('work/text/%s.tsv' % f, encoding='utf-8'):
            if l[0] != '#':
                p = l.rstrip('\n').split('\t')
                if K.get(p[0]): J[nz(p[4])] = K[p[0]]
    return J
if __name__ == '__main__':
    J = table(); raw = [l.rstrip('\n').split('\t') for l in open('work/text/f_raw.tsv', encoding='utf-8')]
    C = collections.defaultdict(collections.Counter); over = collections.defaultdict(list); miss = collections.defaultdict(list); chars = collections.defaultdict(set)
    for nm, o, t in raw:
        n = nz(t)
        if n in J:
            v = J[n]; C[nm]['맞음'] += 1; chars[nm] |= set(v.replace(N, '').replace(' ', ''))
            if len(v.replace(N, '')) > len(t.replace('/', '')): C[nm]['넘침'] += 1; over[nm].append((o, len(t), len(v.replace(N, '')), t[:14], v[:18]))
        else: C[nm]['없음'] += 1; miss[nm].append((o, t))
    print({k: dict(v) for k, v in C.items()}, {k: len(v) for k, v in chars.items()})
    for nm in over: print('넘침', nm, over[nm][:40])
    for nm in miss:
        q = [x for x in miss[nm] if len(re.findall('[ぁ-ん一-龥]', x[1])) >= 2 and nm != '/TURNASC.BIN' or (nm == '/TURNASC.BIN' and re.search('[のはをにがでとし]', x[1]) and len(x[1]) > 6)]
        print('없음', nm, len(miss[nm]), [(o, t[:26]) for o, t in q][:60])
