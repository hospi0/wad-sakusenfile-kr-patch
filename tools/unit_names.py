# -*- coding: utf-8 -*-
"""UNITPACK 유닛 이름(작은 글자 u8, 값 = 시트 번호+1, 9칸, 빈칸 01) 전수(읽기 전용).  python tools/unit_names.py"""
import sys, os, glob, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
S = {}
for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ'): S[1 + i] = c
for i, c in enumerate('abcdefghijklmnopqrstuvwxyz'): S[0x1C + i] = c
SEQ = "0123456789#.・'=/㎜㎏?!%ー:アイウエオカキクケコガギグゲゴサシスセソザジズゼゾタチツテトダヂヅデドナニヌネノバビブベボハヒフヘホパピプペポマミムメモァィゥェォヤユヨワヲッャュョラリルレロンヴ（）"
for i, c in enumerate(SEQ): S[0x36 + i] = c
S[0] = ' '
names = {i + 1: c for i, c in S.items()}
for k, c in zip(range(0xA1, 0xAD), ['Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ', 'Ⅴ', 'Ⅵ', 'Ⅶ', 'Ⅷ', 'Ⅸ', 'Ⅹ', 'Ⅺ', 'Ⅻ']): names[k] = c


def dec(b):
    return ''.join(names.get(x, '<%02X>' % x) for x in b).rstrip(' ')


def main():
    U = collections.Counter(); where = {}; strides = collections.Counter()
    for pat, tag in ((r'\*Koutetsu*', 'K'), (r'\*Sakusen*', 'F')):
        p = glob.glob(SS.B + pat)[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0])
        for f in iso.walk():
            if '/UNITPACK/UPK' not in f[0]: continue
            d = iso.read(f[1], f[2])
            pos = [m.start() for m in re.finditer(b'\xff\xff', d)]
            for a, b in zip(pos, pos[1:]): strides[b - a] += 1
            st = strides.most_common(1)[0][0] if strides else 0
            for q in pos:
                o = q - 0x1C                       # 이름 시작 = 표지 앞 0x1C
                if o < 0: continue
                n = d[o:o + 9]
                if not all(0 < x < 0xAE for x in n) or n[0] == 1: continue
                t = dec(n); U[t] += 1; where.setdefault(t, (tag, f[0], o))
    print('간격', strides.most_common(5)); print('고유', len(U))
    kana = [t for t in U if re.search('[ァ-ヴ]', t)]; print('가나 포함', len(kana), '영문만', len(U) - len(kana))
    print(' / '.join(sorted(kana))[:3500])
    print(' / '.join(sorted(t for t in U if t not in kana))[:900])
    with open('work/text/unit_names.tsv', 'w', encoding='utf-8', newline='\n') as f:
        for t, n in U.most_common(): f.write('%s\t%d\t%s\t%s\t%X\n' % ((t, n) + where[t]))


if __name__ == '__main__':
    main()
