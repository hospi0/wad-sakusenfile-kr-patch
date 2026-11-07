# -*- coding: utf-8 -*-
"""부대 번호 앞 «제» 빼기(하스피 2026-11-07). 제N제국·제N차·제N진지·제N비행장 은 그대로."""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
P = re.compile(r'(?<![가-힣])제(?=\d+(?!\d)(?!제국|차|진지|비행장))')
log = []
def sub(t): return P.sub('', t)
# ko_final + fix_ko
F = {}; head = None; order = []
for l in open('work/text/fix_ko.tsv', encoding='utf-8'):
    if l[0] == '#': head = l; continue
    i, v = l.rstrip('\n').split('\t', 1); F[i] = v
out = []
for l in open('work/text/ko_final.tsv', encoding='utf-8'):
    if l[0] == '#': out.append(l); continue
    p = l.rstrip('\n').split('\t', 2); n = sub(p[2])
    if n != p[2]: log.append((p[0], p[2][:40], n[:40])); F[p[0]] = sub(F.get(p[0], p[2])); p[2] = n
    out.append('\t'.join(p) + '\n')
open('work/text/ko_final.tsv', 'w', encoding='utf-8', newline='\n').write(''.join(out))
open('work/text/fix_ko.tsv', 'w', encoding='utf-8', newline='\n').write(head + ''.join('%s\t%s\n' % (i, F[i]) for i in sorted(F)))
for f in ('ko_extra', 'ko_extra2', 'ko_small2', 'ko_small3'):
    L = open('work/text/%s.tsv' % f, encoding='utf-8').readlines(); o = []
    for l in L:
        if l[0] != '#':
            n = sub(l)
            if n != l: log.append((l[:5], l[6:46].rstrip(), n[6:46].rstrip())); l = n
        o.append(l)
    open('work/text/%s.tsv' % f, 'w', encoding='utf-8', newline='\n').write(''.join(o))
print(len(log))
for x in log[:6] + log[-6:]: print(x)
left = set()
for f in ('ko_final', 'ko_extra', 'ko_extra2', 'ko_small2', 'ko_small3'):
    for l in open('work/text/%s.tsv' % f, encoding='utf-8'):
        left |= set(re.findall(r'제\d+[가-힣]{0,2}', l))
print(sorted(left))
