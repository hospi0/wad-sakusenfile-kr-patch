# -*- coding: utf-8 -*-
"""받은 스테이트 화면별 글자 전수: VDP2 면의 ASC16 글자·8×8 글자를 읽어 문자열로(읽기 전용).
  python tools/screen_audit.py → work/text/screens.tsv(스테이트·면·줄·칸·문자열·번역표 유무)"""
import sys, os, glob, struct, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate, sprite_scan as SS, asc_table, unit_names as UN
from iso9660 import Iso
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); ent = {f[0]: f for f in iso.walk()}
rd = lambda n: iso.read(*ent[n][1:3])
mp = rd('/VIEWCG/ASC16MAP.BIN'); cg = rd('/VIEWCG/ASC16X16.BIN') + rd('/VIEWCG/ASC16_2.BIN'); a8 = rd('/VIEWCG/ASC8X8.BIN')
w = struct.unpack('>%dH' % (len(mp) // 2), mp)
G = {}
for i in range(len(w) // 4):
    g = b''.join(cg[(t - 0x800) * 32:(t - 0x800) * 32 + 32] for t in w[i * 4:i * 4 + 4])
    ch = asc_table.SHEET[i]
    if ch != '□' and g not in G: G[g] = ch
T8 = {a8[i * 32:i * 32 + 32]: UN.S[i] for i in range(1, 0x9F) if i in UN.S and len(set(a8[i * 32:i * 32 + 32])) > 1}
known = set()
for f in ('work/text/ui.tsv', 'work/text/small.tsv', 'work/text/master.tsv'):
    for l in open(f, encoding='utf-8'):
        if l[0] != '#':
            known.add(re.sub('[ 　]', '', l.split('\t')[4]))
JP = re.compile('[ぁ-ヶ一-龥]')
out = []; miss = collections.Counter(); where = {}
fs = sorted(glob.glob('work/states/*.state'), key=lambda f: (len(f), f)) + sorted(glob.glob('work/states_sf/*.state'))
for f in fs:
    st = os.path.basename(f)[:-6]
    try: s, v = mstate.load(f)
    except Exception as e: print('실패', st); continue
    o, n = v['VDP2/VRAM']; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; vr = bytes(b)
    seen = set()
    rr = [k for k in v if 'RawRegs' in k]; R = [int(x) for x in np.frombuffer(s[v[rr[0]][0]:v[rr[0]][0] + v[rr[0]][1]], '<u2')]
    planes = set()
    for nb, (ab, cd) in enumerate(((0x40, 0x42), (0x44, 0x46), (0x48, 0x4A), (0x4C, 0x4E))):
        if not R[0x20 // 2] >> nb & 1: continue
        hi = R[0x3C // 2] >> (nb * 4) & 7; pn = R[(0x30 + nb * 2) // 2]
        two = not pn >> 15
        for reg in (ab, cd):
            for sh in (0, 8):
                mpn = (hi << 6) | (R[reg // 2] >> sh & 0x3F)
                for ps in (0x2000, 0x800):
                    planes.add(((mpn * ps) & 0x7FFFF, two))
    for m, two in sorted(planes):
        if m + 0x2000 > len(vr): continue
        if two: a = np.frombuffer(vr[m:m + 0x4000], '>u2')[1::2][:4096].reshape(64, 64).astype(int)
        else: a = np.frombuffer(vr[m:m + 0x2000], '>u2').reshape(64, 64).astype(int)
        for y in range(64):
            line = ''; x = 0
            while x < 64:
                t = a[y, x] & 0x7FFF if two else a[y, x] & 0xFFF
                c = G.get(vr[t * 32:t * 32 + 128]) if t and t * 32 + 128 <= len(vr) else None
                if c: line += c; x += 2; continue
                c8 = T8.get(vr[t * 32:t * 32 + 32]) if t and t * 32 + 32 <= len(vr) else None
                if c8 and c8 not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ': line += c8; x += 1; continue
                line += '|'; x += 1
            for seg in line.split('|'):
                seg = seg.strip('　 ')
                if len(JP.findall(seg)) >= 2 and seg not in seen:
                    seen.add(seg); ok = re.sub('[ 　]', '', seg) in known
                    out.append((st, hex(m), y, seg, ok))
                    if not ok: miss[seg] += 1; where.setdefault(seg, st)
with open('work/text/screens.tsv', 'w', encoding='utf-8', newline='\n') as fo:
    for r in out: fo.write('%s\t%s\t%d\t%s\t%s\n' % r)
print('글자 줄', len(out), '번역표 없음 고유', len(miss))
print(' / '.join('%s(%s)' % (k, where[k]) for k, _ in miss.most_common(200))[:3500])
