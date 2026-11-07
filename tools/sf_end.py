# -*- coding: utf-8 -*-
"""작전파일 엔딩 그림·문자열 보기(읽기 전용)."""
import sys, os, glob, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS
from iso9660 import Iso
import numpy as np
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')
q = glob.glob(SS.B + r'\*Sakusen*')[0]; i2 = Iso(sorted(glob.glob(q + r'\*(Track 1).bin'))[0]); ent = {x[0]: x for x in i2.walk()}
for n in ('/END_DT0.BIN', '/END_DT1.BIN'):
    d = i2.read(*ent[n][1:3]); a = np.frombuffer(d, np.uint8)
    W = 704; H = len(a) // W
    Image.fromarray(a[:W * H].reshape(H, W)).resize((W, H // 2)).save('work/view/sf%s.png' % n[1:-4]); print(n, H)
for l in open('work/text/ui_raw.tsv', encoding='utf-8'):
    c = l.rstrip('\n').split('\t')
    if c[1] == '/ENDING.BIN': print(c[2], c[4][:60])

print('=== ENDING 번호열')
d = i2.read(*ent['/ENDING.BIN'][1:3])
for st in (0, 1, 2, 3, 0x20, 0x100):
    for fmt, nm in (('>4H', 'u16'),):
        k = struct.pack(fmt, st + 1, st + 2, st + 3, st + 4); p = d.find(k)
        if p >= 0: print(nm, st, hex(p), d[p - 8:p + 40].hex(' '))
    k = bytes((st + 1, st + 2, st + 3, st + 4)); p = d.find(k)
    if p >= 0: print('u8', st, hex(p), d[max(0, p - 8):p + 40].hex(' '))
