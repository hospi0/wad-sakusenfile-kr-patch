import sys, os, struct
sys.path.insert(0, 'tools')
import asc_build as B
iso, E = B.disc('K'); d = iso.read(*E['/GMS1.BIN'][1:3])
print(d[0x8C0:0x930].hex(' '))
E2 = iso.read(*E['/00000000.BIN'][1:3]); print(E2[0x770:0x7C0].hex(' '))
