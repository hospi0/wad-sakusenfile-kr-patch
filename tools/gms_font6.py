import sys, os, struct
sys.path.insert(0, 'tools')
import asc_build as B
iso, E = B.disc('K'); d = iso.read(*E['/GMS1.BIN'][1:3])
T = (0xB08, 0xB0C, 0xB10, 0xB14, 0xB18)
for i in range(0x600, 0x1000, 2):
    op = struct.unpack_from('>H', d, i)[0]
    if op >> 12 == 0xD:
        t = (i & ~3) + 4 + (op & 255) * 4
        if t in T: print(hex(i), 'mov.l', hex(t), 'R%d' % (op >> 8 & 15))
