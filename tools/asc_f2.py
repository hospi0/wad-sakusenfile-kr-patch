# -*- coding: utf-8 -*-
"""작전파일 스테이트 VRAM 에서 ASC16 두 파일 위치(읽기 전용)."""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B, mstate
sys.stdout.reconfigure(encoding='utf-8')
F = B.disc('F')
def rd(n): return F[0].read(*F[1][n][1:3])
fa, fb = rd('/VIEWCG/ASC16X16.BIN'), rd('/VIEWCG/ASC16_2.BIN')
pa = fa[0x4000:0x4040]; pa2 = fa[-0x400:-0x3C0]; pb = fb[0x4000:0x4040]; pb2 = fb[-0x4000:-0x3FC0]
fs = [f for f in glob.glob('work/states/**/*', recursive=True) + glob.glob('my files/**/*.state*', recursive=True) + glob.glob('my files/**/*.mc*', recursive=True) if os.path.isfile(f)]
seen = {}
for f in fs:
    try: s, v = mstate.load(f)
    except Exception: continue
    o, n = v['VDP2/VRAM']; m = bytearray(s[o:o + n]); m[0::2], m[1::2] = m[1::2], m[0::2]; m = bytes(m)
    a, a2, b, b2 = m.find(pa), m.find(pa2), m.find(pb), m.find(pb2)
    if b >= 0 or a2 >= 0:
        k = (a - 0x4000, a2 - (len(fa) - 0x400), b - 0x4000, b2 - (len(fb) - 0x4000))
        seen.setdefault(k, []).append(os.path.basename(f))
for k, v in seen.items(): print([hex(x) for x in k], len(v), v[:4])
print(hex(len(fa)), len(fs))
