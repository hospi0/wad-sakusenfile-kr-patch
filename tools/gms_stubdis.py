import sys
sys.path.insert(0,'tools'); sys.stdout.reconfigure(encoding='utf-8')
import gms_build as G, sh2dis, struct
out,bad=G.patch(log=lambda *a:None); d=out['/GMS2.BIN']
for a in range(G.STUB,G.STUB+G.patch.stub,2):
    t=sh2dis.disasm_one(d,a,0x200000); print(hex(a),t[0] if isinstance(t,tuple) else t)
g=out['/GMS1.BIN']; print(g[0x8E0:0x8EC].hex(' '),hex(struct.unpack_from('>I',g,0xB10)[0]))
