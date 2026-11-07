# -*- coding: utf-8 -*-
"""Sakusen File 디스크 조사, 본편과 같은 파일 대조(읽기 전용).  python tools/sf_survey.py"""
import sys, os, glob, hashlib, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\claude\roms\ss\World Advanced Daisenryaku'
R1 = glob.glob(B + r'\*Koutetsu*')[0]; R2 = glob.glob(B + r'\*Sakusen*')[0]
print(os.listdir(R2))
t2 = sorted(glob.glob(R2 + r'\*.bin'))[0]
a = Iso(glob.glob(R1 + r'\*(Track 1).bin')[0]); b = Iso(t2)
print(b.sector(0)[:96]); fa = a.walk(); fb = b.walk()
print('파일', len(fb), '크기', sum(f[2] for f in fb))
print(collections.Counter('/'.join(f[0].split('/')[:2]) for f in fb).most_common(14))
print(collections.Counter(f[0].rsplit('.', 1)[-1] for f in fb if '.' in f[0]).most_common(12))
def h(iso, f):
    try: return hashlib.md5(iso.read(f[1], f[2])).hexdigest()
    except EOFError: return None
A = {}
for f in fa:
    if f[2] and not f[0].endswith('/') and f[2] < 8000000: A.setdefault((f[2], h(a, f)), f[0])
same = diff = 0; rest = []
for f in fb:
    if not f[2] or f[0].endswith('/'): continue
    if f[2] < 8000000 and (f[2], h(b, f)) in A: same += 1
    else: diff += 1; rest.append((f[0], f[2]))
print('같은 파일', same, '다른 파일', diff)
for r in sorted(rest, key=lambda x: x[0])[:70]: print(r)
