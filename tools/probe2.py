# -*- coding: utf-8 -*-
"""스테이트 메모리 문구 검색 + 이름 있는 파일 머리(읽기 전용).  python tools/probe2.py"""
import sys, os, re, collections, glob, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso9660 import Iso
import state as ST
sys.stdout.reconfigure(encoding='utf-8')
R = r'C:\claude\roms\ss\World Advanced Daisenryaku\World Advanced Daisenryaku - Koutetsu no Senpuu (Japan) (Rev A) (10M)'
iso = Iso(glob.glob(R + r'\*(Track 1).bin')[0])
ent = {f[0]: f for f in iso.walk()}

def swap(b):
    b = bytearray(b + (b'\0' if len(b) & 1 else b''))
    b[0::2], b[1::2] = b[1::2], b[0::2]
    return bytes(b)

W = {'35': ['本作戦は', '我が国に', 'イギリス', '宣戦布告'], '30': ['フランス侵攻作戦', '開始'], '13': ['どちらにセーブしますか', 'セーブ'], '11': ['移動後不可能なコマンド', 'コマンド'], '12': ['急降下爆撃機', '移動', '燃料']}
for k, ws in W.items():
    s = ST.unrzip(open('work/states/%s.state' % k, 'rb').read()); s = bytes(s)
    print(k, len(s), s[:16])
    for t in ws:
        for enc in ('cp932', 'euc_jp', 'utf-16-be'):
            b = t.encode(enc)
            a = [m.start() for m in re.finditer(re.escape(b), s)][:4]; c = [m.start() for m in re.finditer(re.escape(swap(b)), s)][:4]
            if a or c: print(' ', t, enc, '그대로', [hex(x) for x in a], '뒤집힘', [hex(x) for x in c])
for f in ('/DAI_MES.DC', '/DAI_SYS.DC', '/DAI_ASC.DC', '/DAI_SL.DC', '/DAI_MOV.DC', '/DAI_M0D.DC', '/GMS1.BIN', '/GAME1.BIN', '/00000000.BIN', '/0.TSK' ):
    if f in ent:
        d = iso.read(ent[f][1], min(ent[f][2], 1 << 20)); import math
        c = collections.Counter(d); e = -sum(v / len(d) * math.log2(v / len(d)) for v in c.values())
        print(f, ent[f][2], round(e, 2), d[:32].hex(' '))
sk = [f for f in ent if f.startswith('/SAKUSEN/')][:4]; print(sk)
for f in sk:
    d = iso.read(ent[f][1], ent[f][2]); print(f, len(d), d[:64].hex(' '))
print(collections.Counter(f.split('/')[-1][:3] for f in ent if f.startswith('/SAKUSEN/')).most_common(10))
