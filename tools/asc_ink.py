import sys,glob,struct,collections
sys.path.insert(0,'tools')
import sprite_scan as SS
from iso9660 import Iso
for pat in (r'\*Koutetsu*', r'\*Sakusen*'):
    p=glob.glob(SS.B+pat)[0]; iso=Iso(sorted(glob.glob(p+r'\*(Track 1).bin'))[0]); E={f[0]:f for f in iso.walk()}
    r=lambda n: iso.read(*E[n][1:3])
    import hashlib
    print({n:(E[n][2],hashlib.md5(r(n)).hexdigest()[:6]) for n in ('/VIEWCG/ASC16X16.BIN','/VIEWCG/ASC16_2.BIN','/VIEWCG/ASC16MAP.BIN','/VIEWCG/ASC8X8.BIN')})
    mp=r('/VIEWCG/ASC16MAP.BIN'); cg=r('/VIEWCG/ASC16X16.BIN')+r('/VIEWCG/ASC16_2.BIN')
    w=struct.unpack('>%dH'%(len(mp)//2),mp)
    for i in (1,60,150):
        rows=[]
        g=[cg[(t-0x800)*32:(t-0x800)*32+32] for t in w[i*4:i*4+4]]
        for y in range(16):
            s=''
            for x in range(16):
                c=g[(y//8)*2+x//8]; b=c[(y%8)*4+(x%8)//2]; s+='%X'%((b>>4) if x%2==0 else b&15)
            rows.append(s.replace('0','.'))
        print('\n'.join(rows)); print()
    c=collections.Counter()
    for b in cg[:70912]: c[b>>4]+=1; c[b&15]+=1
    print(c.most_common(8))
