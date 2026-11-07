# -*- coding: utf-8 -*-
"""VDP2 VRAM 셀 펼쳐 보기(읽기 전용).  python tools/vdp2.py 스테이트 [bpp 4|8]"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate
import numpy as np
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
s, v = mstate.load(sys.argv[1]); bpp = int(sys.argv[2]) if len(sys.argv) > 2 else 4
o, n = v['VDP2/VRAM']; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; vr = bytes(b)
open('work/view/vdp2.bin', 'wb').write(vr)
print([k for k in v if k.startswith('VDP2/')][:60])
rr = [k for k in v if 'RawRegs' in k]; print(rr)
if rr:
    a, c = v[rr[0]]; r = np.frombuffer(s[a:a + c], '<u2'); print([hex(x) for x in r[:0x90]])
nz = [(i, int(np.count_nonzero(np.frombuffer(vr[i:i + 0x4000], np.uint8)))) for i in range(0, n, 0x4000)]; print([(hex(i), c) for i, c in nz])
cs = 32 if bpp == 4 else 64
a = np.frombuffer(vr, np.uint8)
if bpp == 4: px = np.stack([a >> 4, a & 15], 1).reshape(-1, 8, 8) * 17
else: px = a.reshape(-1, 8, 8)
C = 128; R = len(px) // C
img = px[:R * C].reshape(R, C, 8, 8).transpose(0, 2, 1, 3).reshape(R * 8, C * 8).astype(np.uint8)
Image.fromarray(img).save('work/view/vdp2_%d.png' % bpp); print(img.shape)
