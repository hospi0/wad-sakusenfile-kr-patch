# -*- coding: utf-8 -*-
"""EP 왼쪽·오른쪽 판 차이 측정 + 작전파일 엔딩 그림 보기(읽기 전용)."""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS
from iso9660 import Iso
import numpy as np
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0])
f = [f for f in iso.walk() if f[0].endswith('A_W_G.EP')][0]; a = np.frombuffer(iso.read(f[1], f[2]), '>u2').reshape(336, 704)
L, R = a[:, :352].astype(int), a[:, 352:].astype(int); print('왼오 다른 화소 비율', (L != R).mean())
q = glob.glob(SS.B + r'\*Sakusen*')[0]; i2 = Iso(sorted(glob.glob(q + r'\*(Track 1).bin'))[0]); ent = {x[0]: x for x in i2.walk()}
print([(x[0], x[2]) for x in i2.walk() if 'END' in x[0] or x[0].endswith('.EP') or 'GAMEOVER' in x[0]])
for n in ('/ENDFONT0.BIN', '/ENDFONT1.BIN'):
    d = i2.read(*ent[n][1:3]); c = len(d) // 128
    W = 24; H = (c + W - 1) // W; im = np.zeros((H * 18, W * 18), np.uint8)
    for i in range(c):
        x = np.frombuffer(d[i * 128:i * 128 + 128], np.uint8); t = np.stack([x >> 4, x & 15], 1).reshape(4, 8, 8)
        o = np.zeros((16, 16), np.uint8); o[:8, :8], o[:8, 8:], o[8:, :8], o[8:, 8:] = t
        im[i // W * 18:i // W * 18 + 16, i % W * 18:i % W * 18 + 16] = o * 17
    Image.fromarray(im).resize((W * 54, H * 54), 0).save('work/view/sf%s.png' % n[1:-4]); print(n, c)
d = i2.read(*ent['/END_DT0.BIN'][1:3]); print(d[:48].hex(' '), len(d))
