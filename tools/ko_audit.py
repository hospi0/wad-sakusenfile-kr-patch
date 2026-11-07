# -*- coding: utf-8 -*-
"""받은 번역 검사(읽기 전용).  python tools/ko_audit.py
  빠짐·원문 변경·토큰(\\l, <..>, 괄호, 부호)·남은 가나 한자·길이 초과·용어 후보."""
import sys, os, re, glob, collections
sys.stdout.reconfigure(encoding='utf-8')
SRC = ['work/text/master.tsv', 'work/text/ui.tsv', 'work/text/small.tsv', 'work/text/place.tsv', 'work/text/ending.tsv']


def load_master():
    m = collections.OrderedDict()
    for f in SRC:
        for l in open(f, encoding='utf-8'):
            if l[0] == '#' or not l.strip(): continue
            c = l.rstrip('\n').split('\t'); m[c[0]] = c
    return m


def load_ko():
    k = {}; dup = []; bad = []
    for fn in sorted(glob.glob('my files/번역/*.tsv')):
        for n, l in enumerate(open(fn, encoding='utf-8-sig'), 1):
            if l[0] == '#' or not l.strip(): continue
            c = l.rstrip('\r\n').split('\t')
            if len(c) < 6: bad.append((os.path.basename(fn), n, len(c), l[:50])); continue
            if c[0] in k: dup.append(c[0])
            k[c[0]] = (c, os.path.basename(fn))
    if os.path.exists('work/text/fix_ko.tsv'):
        for l in open('work/text/fix_ko.tsv', encoding='utf-8'):
            if l[0] != '#' and l.strip():
                i, v = l.rstrip('\n').split('\t', 1); c = list(k[i][0]); c[5] = v; k[i] = (c, k[i][1])
    return k, dup, bad


def cells(s):
    """전각 칸 기준(줄바꿈 코드 빼고)."""
    return len(s.replace('\\l', ''))


def main():
    m = load_master(); k, dup, bad = load_ko()
    print('원문', len(m), '번역', len(k), '중복', len(dup), '열 모자람', len(bad), bad[:4])
    miss = [i for i in m if i not in k]; extra = [i for i in k if i not in m]
    empty = [i for i in k if i in m and not k[i][0][5].strip()]
    chg = [i for i in k if i in m and k[i][0][4] != m[i][4]]
    print('빠짐', len(miss), miss[:12], '| 남는 번호', len(extra), extra[:8], '| 빈 번역', len(empty), empty[:12], '| 원문 바뀜', len(chg), chg[:8])
    R = collections.defaultdict(list)
    for i, c in m.items():
        if i not in k: continue
        jp = c[4]; ko = k[i][0][5]
        if jp.count('\\l') != ko.count('\\l'): R['줄바꿈 수'].append((i, jp.count('\\l'), ko.count('\\l')))
        tj = re.findall(r'<[0-9A-F]+>', jp); tk = re.findall(r'<[0-9A-F]+>', ko)
        if tj != tk: R['<코드>'].append((i, tj, tk))
        if re.search('[ぁ-ヶ一-龥]', ko): R['가나 한자 남음'].append((i, ko[:40]))
        for a, b in (('(', ')'), ('（', '）'), ('「', '」'), ('『', '』'), ('［', '］')):
            if (a in jp) != (a in ko) and (a in jp or a in ko): R['괄호'].append((i, jp[:24], ko[:24])); break
        if re.search(r'을\(를\)|이\(가\)|은\(는\)|와\(과\)|\(으\)', ko): R['괄호 조사'].append((i, ko[:40]))
        if '  ' in ko or ko != ko.strip(): R['공백'].append((i, ko[:40]))
        if re.search(r'[,.!?。、，．！？:：] ', ko): R['부호 뒤 공백'].append((i, ko[:40]))
    for t, v in R.items(): print(t, len(v), v[:6])
    g = collections.Counter()
    for i, c in m.items():
        if i in k: g[re.sub(r'_.*', '', c[1])] += 1
    print(g.most_common())
    # 길이
    over = collections.defaultdict(list)
    for i, c in m.items():
        if i not in k: continue
        ko = k[i][0][5]; b = int(c[2]); n = cells(ko)
        tag = c[1][:1] if c[1][0] in 'UNWPE' else 'T'
        if tag in 'UNW' and n > b: over[tag].append((i, b, n, c[4][:14], ko[:18]))
    for t, v in over.items(): print('칸 초과', t, len(v), v[:10])


if __name__ == '__main__':
    main()
