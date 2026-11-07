# -*- coding: utf-8 -*-
"""반각 글꼴 미리보기: work/gfx/h8/ (원본|새 시트, 줄 표본 1:1·3배)."""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import half_build as H
import numpy as np
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
F, M = H.patch('K', {})
com, rom, C, miss, iso, E, syl = H.plan('K')
print('남은 칸', len(H.FREE) - len(M), '표에 없는 진짜 가나', [t for t in miss if re.search('[ァ-ヴ]{3}', t)])
old = iso.read(*E['/VIEWCG/ASC8X8.BIN'][1:3]); new = F['/VIEWCG/ASC8X8.BIN']
def cell(b, i):
    a = np.frombuffer(b[i * 32:i * 32 + 32], np.uint8)
    return np.stack([a >> 4, a & 15], 1).reshape(8, 8) * 17
def sheet(b, W=24):
    n = 209; g = np.zeros((((n + W - 1) // W) * 9, W * 9), np.uint8) + 40
    for i in range(n):
        y, x = i // W * 9, i % W * 9; g[y:y + 8, x:x + 8] = cell(b, i)
    return g
os.makedirs('work/gfx/h8', exist_ok=True)
a, b = sheet(old), sheet(new)
Image.fromarray(np.hstack([a, np.zeros((a.shape[0], 16), np.uint8), b])).resize(((a.shape[1] * 2 + 16) * 3, a.shape[0] * 3), 0).save('work/gfx/h8/시트_원본_새것.png')
enc = dict(H.K8); enc.update(M)
S = ['도시', '붕괴 도시', '공항', '붕괴 항구', '다리', '동결 다리', '도로', '진지', '평지', '황무지', '습지', '사막', '고지', '산', '숲', '밭', '산림', '정글', '여울', '모래밭', '바다', '중립', '진창', '설원', '동결 강',
     '대도시', '중광산', '붕괴 광산', '로켓포', '105㎜포', '75㎜포 L48', '20㎜ 기관포', '155㎜ 카농포', '100㎜ 대공포', 'ASM 미사일', '대전차소총', 'P.슈레크', 'P.파우스트', '해안포', '어뢰', '기관단총', '자동소총', '돌격소총', '폭뢰', '바주카', '피아트', '보급물자', '기관총', '로켓탄', '250㎏폭탄',
     '자국', '동맹', '적국', '궤멸', '생존', '오디오', 'BGM 선택', 'SoundTest', '육상', '항공', '해상',
     'Germany', 'UK 8A', 'US TF58', 'Stalingrd', 'PearlHbr', 'T4 Chito', 'A6M5', 'Ki43-II', 'Marines']
W = 5; rows = (len(S) + W - 1) // W
g = np.zeros((rows * 11 + 2, W * 84), np.uint8)
for k, t in enumerate(S):
    y, x = k // W * 11 + 1, k % W * 84 + 2
    for j, c in enumerate(t): g[y:y + 8, x + j * 8:x + j * 8 + 8] = cell(new, enc[c] - 1)
Image.fromarray(g).save('work/gfx/h8/표본_1배.png')
Image.fromarray(g).resize((g.shape[1] * 3, g.shape[0] * 3), 0).save('work/gfx/h8/표본_3배.png')
print('완료', g.shape)
