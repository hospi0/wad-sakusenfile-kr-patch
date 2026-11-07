# -*- coding: utf-8 -*-
"""화면 글자의 저장 위치 찾기: 글꼴 번호(문자열 번호)·VRAM 칸 묶음 u16 로 전 파일 검색(읽기 전용).  python tools/str_find.py"""
import sys, os, glob, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, asc_table, unit_names as UN
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
CH = asc_table.CH
ID = {}
for i, c in enumerate(CH):
    if c != '□': ID.setdefault(c, []).append(i)
W = ['累積度', '通常', '記録日時', '国選択', '画面', 'ファイル', 'セレクト', '条約締結', '第一次世界', '賠償金', 'ベルサイユ']
K8 = {v: k + 1 for k, v in UN.S.items()}
S8 = ['トシ', 'カワ', 'ハヤシ', 'ドイツテイコク', '250㎜', 'バクダン', 'ヘイチ', 'ミズウミ']
keys = {}
for w in W:
    if all(c in ID for c in w):
        keys[w + ' u16'] = struct.pack('>%dH' % len(w), *[ID[c][0] for c in w])
for w in S8:
    if all(c in K8 for c in w): keys[w + ' u8'] = bytes(K8[c] for c in w)
for pat, tag in ((r'\*Koutetsu*', 'K'), (r'\*Sakusen*', 'F')):
    p = glob.glob(SS.B + pat)[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); hit = collections.defaultdict(list)
    for f in iso.walk():
        if f[0].endswith(('.MUS', '.CPK', '/')) or f[2] < 16 or f[0].startswith('/CDDA') or 'UNIT3D' in f[0]: continue
        try: d = iso.read(f[1], f[2])
        except EOFError: continue
        for k, b in keys.items():
            o = d.find(b)
            if o >= 0: hit[k].append((f[0], hex(o)))
    for k in keys: print(tag, k, len(hit[k]), hit[k][:4])
