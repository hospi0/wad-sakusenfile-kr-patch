# -*- coding: utf-8 -*-
"""작전파일 병기 타입 메뉴 «선택된 줄 밝은 그림» 5장 한글화.
  GMS2 0x37BE0 + k*0xF00 (k=0 독일·1 일본·2 미국·3 소련·4 영국), 160×24 8비트, 색 은행 0x400.
  메뉴에서 VDP1 이 어두운 판(0x31A40, 176×142, x=160 y=56) 위 x=168 y=63+ 에 겹쳐 그림 → 글자 위치는 어두운 판 한글(ty2) 과 같은 화면 자리에 맞춘다.
  python tools/f_type_sel.py 폴더   → GMS2_37BE0.bin + 미리보기"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B, mstate, bdf
import numpy as np
from PIL import Image
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
G14 = bdf.Font(r'C:\claude\utils\font\Galmuri-v2.40.3\Galmuri11.bdf')
iso, E = B.disc('F'); g = iso.read(*E['/GMS2.BIN'][1:3]); O = 0x37BE0; W, H, N = 160, 24, 5
src = np.frombuffer(g[O:O + W * H * N], np.uint8).reshape(N * H, W); a = src.copy()
dark0 = np.frombuffer(g[0x31A40:0x31A40 + 176 * 142], np.uint8).reshape(142, 176)
dark1 = np.frombuffer(open('work/gfx/ty2/GMS2_31A40.bin', 'rb').read(), np.uint8).reshape(142, 176)
s, v = mstate.load('work/states_sf/typemenu.state'); co, cn = v['VDP2/CRAM']; cr = np.frombuffer(bytes(s[co:co + cn]), '<u2').astype(int)
def rgb(x, b):
    c = cr[(x.astype(int) + b) & 0x7FF]; return np.stack([(c & 31) << 3, (c >> 5 & 31) << 3, (c >> 10 & 31) << 3], 2).astype(np.uint8)
L = lambda i: (lambda c: (c & 31) + (c >> 5 & 31) + (c >> 10 & 31))(int(cr[(int(i) + 0x400) & 0x7FF]))
def glyphs(t):
    pts, _ = G14.draw(t); xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    m = np.zeros((max(ys) - min(ys) + 1, max(xs) - min(xs) + 1), bool)
    for x, y in pts: m[y - min(ys), x - min(xs)] = True
    return m
TX = ['독일 타입', '일본 타입', '미국 타입', '소련 타입', '영국 타입']
# 어두운 판 한글 글자 위치(바뀐 화소의 경계) → 밝은 판 좌표(x-8)
ch = np.argwhere(dark0 != dark1); print('어두운 판 변경 범위 y', ch[:, 0].min(), ch[:, 0].max())
X0, X1, Y0, Y1 = 33, 153, 5, 19          # 밝은 판 안쪽 판(테두리 제외) — 원본 화소 덤프로 실측
# 글자색은 5장 모두 한 색(하스피 지시) — 5장 전체 안쪽 판에서 한 번만 고른다
REG = np.vstack([src[k * H + Y0:k * H + Y1, X0:X1] for k in range(N)]); LV = np.vectorize(L)(REG)
ink = int(np.bincount(REG[LV >= LV.max() - 4]).argmax())               # 글자 몸(가장 밝은 무리)
sh = int(np.bincount(REG[(LV <= 35) & (LV >= 20)]).argmax())            # 오른쪽·아래 그림자
for k, t in enumerate(TX):
    sub = a[k * H:(k + 1) * H]
    for r in range(Y0, Y1): sub[r, X0:X1] = np.bincount(src[k * H + r, X0:X1]).argmax()
    m = glyphs(t); h, w = m.shape
    cx = 35 + (117 - w) // 2                                             # ty2 와 같은 가로 자리(43−8)
    cy = Y0 + (Y1 - Y0 - h) // 2
    for yy in range(h):
        for xx in range(w):
            if m[yy, xx] and cy + yy + 1 < Y1 and cx + xx + 1 < X1: sub[cy + yy + 1, cx + xx + 1] = sh
    for yy in range(h):
        for xx in range(w):
            if m[yy, xx]: sub[cy + yy, cx + xx] = ink
    print(t, '글자', w, 'x', h, '자리', cx, cy, '몸', ink, L(ink), '그림자', sh, L(sh))
open(OUT + '/GMS2_37BE0.bin', 'wb').write(a.tobytes())
Image.fromarray(np.hstack([rgb(src, 0x400), np.zeros((N * H, 8, 3), np.uint8), rgb(a, 0x400)])).resize(((W * 2 + 8) * 3, N * H * 3), 0).save(OUT + '/미리보기_선택줄_왼쪽원본_오른쪽한글.png')
