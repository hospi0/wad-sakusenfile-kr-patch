# -*- coding: utf-8 -*-
import sys, struct, re
sys.path.insert(0, 'tools'); sys.stdout.reconfigure(encoding='utf-8')
import asc_build as B, mstate
iso, E = B.disc('K')
s, v = mstate.load('work/states/t1.state')
def mem(k):
    o, n = v[k]; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; return bytes(b)
for nm, d in (('RAML', mem('MAIN/WorkRAML')), ('RAMH', mem('MAIN/WorkRAMH'))):
    for pat, tag in ((struct.pack('>4H', 0x259, 0x25A, 0x25B, 0x25C), '칸'), (struct.pack('>4H', 0xA259, 0xA25A, 0xA25B, 0xA25C), 'A칸'), (struct.pack('>2H', 0x259, 0x25A), '2칸'), (struct.pack('>2H', 0xA030, 0xC000), 'A030')):
        h = [hex(m.start()) for m in re.finditer(re.escape(pat), d)][:6]
        if h: print(nm, tag, h)
