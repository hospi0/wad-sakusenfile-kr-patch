# -*- coding: utf-8 -*-
"""받은 번역 + 고침표 → work/text/ko_final.tsv(부호 뒤 공백·말줄임 정리) + 칸·글자 수 보고.  python tools/ko_merge.py"""
import sys, os, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ko_audit as A
sys.stdout.reconfigure(encoding='utf-8')
N = chr(92) + 'l'


def tidy(s):
    s = s.replace('・・・', '…').replace('...', '…').replace('……', '…')
    s = re.sub(r'([,.!?…:;、。，．！？：；])[ 　]+(?=\S)', r'\1', s)      # 문장부호 뒤 공백 삭제
    return s


def main():
    m = A.load_master(); k, _, _ = A.load_ko()
    drop = {l.strip() for l in open('work/text/drop_ids.txt', encoding='utf-8')}
    out = {}
    for i, c in m.items():
        if i in drop: continue
        out[i] = tidy(k[i][0][5])
    with open('work/text/ko_final.tsv', 'w', encoding='utf-8', newline='\n') as f:
        f.write('#번호\t구분\tKO\n')
        for i, v in out.items(): f.write('%s\t%s\t%s\n' % (i, m[i][1], v))
    print('최종', len(out), '뺀 잡음', len(drop))
    # 시나리오별 글자 종류
    sc = collections.defaultdict(set); ln = collections.Counter(); rows = collections.defaultdict(list)
    for l in open('work/text/master_pos.tsv', encoding='utf-8'):
        if l[0] == '#': continue
        i, tag, s, o, n = l.rstrip('\n').split('\t')
        t = re.sub('<[0-9A-F]+>', '', out[i].replace(N, '')); sc[(tag, int(s))] |= set(t); ln[(tag, int(s))] += len(t); rows[(tag, int(s))].append((int(o, 16), i))
    v = sorted((len(x), key) for key, x in sc.items())
    print('시나리오', len(sc), '글자 종류 최소', v[0], '최대', v[-1], '평균', sum(a for a, _ in v) // len(v), '상위', v[-5:])
    # 제목·조건 줄 폭
    T = []; C = []
    for key, r in rows.items():
        r.sort()
        for o, i in r:
            n = len(out[i].replace(N, ''))
            if n < 26 and re.search('破壊|防衛', m[i][4]): C.append((n, i, m[i][4][:18], out[i][:26]))
    C.sort(reverse=True); print('조건 줄 최대', C[:6])
    tt = sorted(((len(out[i]), i, m[i][4], out[i]) for i, c in m.items() if i in out and c[1][:1] in 'KF' and len(c[4]) <= 16 and not re.search('破壊|防衛', c[4]) and len(out[i]) > len(c[4])), reverse=True)
    print('제목류 원문보다 긴 줄', len(tt), tt[:14])


if __name__ == '__main__':
    main()
