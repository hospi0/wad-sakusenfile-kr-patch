# -*- coding: utf-8 -*-
"""작전 SAKU_DT 구조 조사(읽기 전용)."""
import sys, os, struct, collections, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B
import numpy as np
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8')
iso, E = B.disc('F'); d = iso.read(*E['/SAKUSEN/SAKU_DT.BIN'][1:3]); print(len(d))
print(sorted(k for k in E if 'SAKUSEN' in k)[:12], len([k for k in E if '/SAK_F' in k]))
pos = {}
for l in open('work/text/master_pos.tsv', encoding='utf-8'):
    if l[0] != '#':
        i, tag, s, o, n = l.rstrip('\n').split('\t')
        if tag == 'F': pos[int(o, 16)] = (i, int(n), int(s))
os_ = sorted(pos); print('F 줄', len(pos), hex(os_[0]), hex(os_[-1]), os_[:0])
print('시나리오 번호 분포', collections.Counter(v[2] for v in pos.values()).most_common(5), sorted(set(v[2] for v in pos.values()))[:45])
BASE = 0x2C0000
ptr = []
for i in range(0, len(d) - 3, 4):
    x = struct.unpack_from('>I', d, i)[0] - BASE
    if x in pos: ptr.append((i, x))
print('포인터', len(ptr), hex(ptr[0][0]) if ptr else None, hex(ptr[-1][0]) if ptr else None)
gaps = collections.Counter(b[0] - a[0] for a, b in zip(ptr, ptr[1:])); print(gaps.most_common(6))
print('연속 표 후보', [(hex(a), hex(b)) for a, b in zip([p[0] for p in ptr], [p[0] for p in ptr][1:]) if b - a > 4][:20])
k = {}
for l in open('work/text/ko_final.tsv', encoding='utf-8'):
    if l[0] != '#':
        i, g, v = l.rstrip('\n').split('\t', 2); k[i] = v
for i, (a, x) in enumerate(ptr[:18]): print(i, hex(a), hex(x), pos[x][1], pos[x][2], k.get(pos[x][0], '?')[:34])
print('...')
n0 = [p for p in ptr if p[0] >= ptr[len(ptr) // 2][0]][:6]
for a, x in n0: print(hex(a), hex(x), pos[x][1], pos[x][2], k.get(pos[x][0], '?')[:34])
miss = [o for o in os_ if o not in {p[1] for p in ptr}]; print('포인터 없는 줄', len(miss), [(hex(o), k.get(pos[o][0], '?')[:16]) for o in miss[:24]])
print('없는 번역', sum(1 for v in pos.values() if v[0] not in k))
fn = [x for x in sorted(E) if '/SAK_F' in x][0]; f = iso.read(*E[fn][1:3]); print(fn, len(f), len(f) / 128)
pg = np.zeros((18, 18 * 40), np.uint8)
for i in range(40):
    a = np.frombuffer(f[i * 128:i * 128 + 128], np.uint8); q = np.stack([a >> 4, a & 15], 1).reshape(4, 8, 8); o = np.zeros((16, 16), np.uint8); o[:8, :8], o[:8, 8:], o[8:, :8], o[8:, 8:] = q
    pg[1:17, i * 18 + 1:i * 18 + 17] = o * 17
Image.fromarray(pg).resize((18 * 40 * 2, 36), 0).save('work/view/audit/sf_sym.png')
for fn2 in sorted(x for x in E if '/SAK_F' in x)[:3]: print(fn2, E[fn2][2] / 128)
print('최대 칸', max(E[x][2] / 128 for x in E if '/SAK_F' in x), '최소', min(E[x][2] / 128 for x in E if '/SAK_F' in x))
