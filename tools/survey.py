# -*- coding: utf-8 -*-
"""초기 조사(읽기 전용).  python tools/survey.py"""
import sys, os, re, collections, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
R = r'C:\claude\roms\ss\World Advanced Daisenryaku\World Advanced Daisenryaku - Koutetsu no Senpuu (Japan) (Rev A) (10M)'
T1 = glob.glob(R + r'\*(Track 1).bin')[0]
iso = Iso(T1); fs = [f for f in iso.walk()]
print(fs[0] if fs else None, '수', len(fs), '크기', sum(f[2] for f in fs))
print(iso.sector(0)[:96])
ext = collections.Counter(); sz = collections.Counter()
for f in fs:
    e = f[0].rsplit('.', 1)[-1] if '.' in f[0].split('/')[-1] else ''; ext[e] += 1; sz[e] += f[2]
print(sorted(sz.items(), key=lambda x: -x[1])[:20]); print(ext.most_common(20))
print(collections.Counter('/'.join(f[0].split('/')[:2]) for f in fs).most_common(16))
for f in sorted(fs, key=lambda x: -x[2])[:22]: print(f[0], f[2])
RE = re.compile(rb'(?:[\x81-\x9f\xe0-\xef][\x40-\x7e\x80-\xfc]){3,}')
JP = re.compile('[ぁ-んァ-ヶ一-龥]')
tot = collections.Counter(); ch = collections.Counter(); samp = {}
for f in fs:
    if f[2] > 40000000: continue
    try: d = iso.read(f[1], f[2]); c = 0; n = 0
    except EOFError: continue
    for m in RE.finditer(d):
        try: t = m.group(0).decode('cp932')
        except Exception: continue
        if len(JP.findall(t)) >= 3 and re.search('[ぁ-ん]', t): c += 1; n += len(t); samp.setdefault(f[0], t[:24])
    if c: tot[f[0]] = c; ch[f[0]] = n
print('히라가나 문자열 파일', len(tot), '줄', sum(tot.values()), '글자', sum(ch.values()))
for k, v in tot.most_common(20): print(k, v, ch[k], samp[k])
