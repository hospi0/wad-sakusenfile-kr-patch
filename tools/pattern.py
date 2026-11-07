# -*- coding: utf-8 -*-
"""자체 코드 문장 찾기: 같은 낱말이 되풀이되는 모양을 메모리에서 찾는다(읽기 전용).  python tools/pattern.py"""
import sys, os, re, collections, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso9660 import Iso
import state as ST
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
R = r'C:\claude\roms\ss\World Advanced Daisenryaku\World Advanced Daisenryaku - Koutetsu no Senpuu (Japan) (Rev A) (10M)'
iso = Iso(glob.glob(R + r'\*(Track 1).bin')[0])
fs = iso.walk()
print([f[0] for f in fs if f[0].count('/') == 1 and not f[0].endswith(('.CPK', '.MUS', '.EP'))][38:])

def scan(a, name, step):
    """a: 코드 배열. 5코드 낱말(서로 다름, 0 아님)이 16~120 코드 안에 다시 나오고, 한 칸 뒤 2코드도 같은 곳"""
    n = len(a); out = []
    idx = collections.defaultdict(list)
    for i in range(n - 8):
        k = (a[i], a[i + 1], a[i + 2], a[i + 3], a[i + 4])
        if len(set(k)) == 5 and 0 not in k: idx[k].append(i)
    for k, v in idx.items():
        for x, y in zip(v, v[1:]):
            if 8 <= y - x <= 120 and a[x + 6] == a[y + 6] and a[x + 7] == a[y + 7] and a[x + 5] != a[y + 5]:
                out.append((x * step, y * step, [hex(c) for c in a[x:x + 8]], hex(a[y + 5])))
    print(name, '후보', len(out), out[:6])

s = bytes(ST.unrzip(open('work/states/31.state', 'rb').read()))
print(len(s))
scan(np.frombuffer(s, np.uint8).tolist(), '8비트', 1)
for off in (0, 1):
    b = s[off:]; b = b[:len(b) // 2 * 2]
    scan(np.frombuffer(b, '>u2').tolist(), '16비트 앞%d' % off, 2)
