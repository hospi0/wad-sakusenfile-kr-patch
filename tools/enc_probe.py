# -*- coding: utf-8 -*-
"""글자 저장 형식 시험: 글꼴 번호 여러 변환으로 전 파일·RAM 검색(읽기 전용).  python tools/enc_probe.py"""
import sys, os, glob, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate, sprite_scan as SS, asc_table
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); fs = iso.walk(); ent = {f[0]: f for f in iso.walk()}
mp = iso.read(*ent['/VIEWCG/ASC16MAP.BIN'][1:3]); w = struct.unpack('>%dH' % (len(mp) // 2), mp)
idx = {}
for i, c in enumerate(asc_table.SHEET):
    if c != '□': idx.setdefault(c, i)
W = ['累積度', '記録日時', '国選択']
tr = {'id': lambda i: i, 'id+1': lambda i: i + 1, 'id*2': lambda i: i * 2, 'id*4': lambda i: i * 4, 'id*8': lambda i: i * 8, 'tile': lambda i: w[i * 4], 'tile-800': lambda i: w[i * 4] - 0x800, 'id+0x100': lambda i: i + 0x100}
keys = {}
for t in W:
    ids = [idx[c] for c in t]
    for n, f in tr.items():
        v = [f(i) & 0xFFFF for i in ids]
        keys[(t, n, 'BE16')] = struct.pack('>%dH' % len(v), *v); keys[(t, n, 'LE16')] = struct.pack('<%dH' % len(v), *v); keys[(t, n, 'BE32')] = struct.pack('>%dI' % len(v), *v)
print({t: [idx[c] for c in t] for t in W})
hit = collections.defaultdict(list)
for f in fs:
    if f[0].endswith(('.MUS', '.CPK', '/', '.EP')) or f[2] < 16 or f[0].startswith('/CDDA') or 'UNIT3D' in f[0]: continue
    try: d = iso.read(f[1], f[2])
    except EOFError: continue
    for k, b in keys.items():
        o = d.find(b)
        if o >= 0: hit[k].append((f[0], hex(o)))
s, v = mstate.load('work/states/7.state')
def mem(k):
    o, n = v[k]; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; return bytes(b)
for nm in ('MAIN/WorkRAML', 'MAIN/WorkRAMH'):
    b = mem(nm)
    for k, kb in keys.items():
        o = b.find(kb)
        if o >= 0: hit[k].append((nm, hex(o)))
print(len(hit))
for k, h in hit.items(): print(k, h[:4])
