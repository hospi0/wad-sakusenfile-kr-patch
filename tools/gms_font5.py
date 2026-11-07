# -*- coding: utf-8 -*-
import sys, os, struct, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B
sys.stdout.reconfigure(encoding='utf-8')
iso, E = B.disc('K'); d = iso.read(*E['/GMS1.BIN'][1:3]); print(len(d))
for a in range(0x9C0, 0xB60, 16): print(hex(a), d[a:a + 16].hex(' '))
# 위에서 쓰는 긴 값
c = [(hex(i), hex(struct.unpack_from('>I', d, i)[0])) for i in range(0xA00, 0xB80, 4) if (struct.unpack_from('>I', d, i)[0] >> 20) in (0x002, 0x060, 0x25E, 0x25C)]
print(c)
