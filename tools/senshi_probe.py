# -*- coding: utf-8 -*-
"""SENSHI.TXT 조사(읽기 전용): 형식, 파일명 참조, 스테이트 램 적재 여부."""
import sys, os, glob, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B, mstate
sys.stdout.reconfigure(encoding='utf-8')
for tag in 'KF':
    iso, E = B.disc(tag)
    if '/SENSHI.TXT' not in E: print(tag, '없음'); continue
    d = iso.read(*E['/SENSHI.TXT'][1:3]); print(tag, 'SENSHI', len(d), d[:16].hex())
    if tag == 'K':
        t = d.decode('cp932', 'replace'); L = t.splitlines()
        print('줄', len(L), '최대 줄 글자', max(map(len, L)), '끝 200', repr(t[-120:]))
        print('\n'.join(L[:30]))
        print('제어 바이트', collections.Counter(c for c in t if ord(c) < 32).most_common(8))
    keys = [b'SENSHI', b'senshi', 'SENSHI'.encode('utf-16-be')]
    for fn, e in E.items():
        if e[2] > 4000000 or fn.startswith('/CDDA') or fn.endswith(('.MUS', '.CPK', '.EP', '.DC')): continue
        try: b = iso.read(*e[1:3])
        except EOFError: continue
        for k in keys:
            for m in re.finditer(re.escape(k), b):
                print(' 이름 참조', tag, fn, hex(m.start()), b[max(0, m.start() - 24):m.start() + 28])
    if tag == 'K':
        sn = d[0x400:0x440]; sn2 = d[0x2000:0x2040]
        for f in sorted(glob.glob('work/states/*.state'), key=lambda x: (len(x), x)):
            s, v = mstate.load(f); hit = []
            for name in ('MAIN/WorkRAML', 'MAIN/WorkRAMH', 'VDP2/VRAM', 'VDP1/VRAM'):
                if name not in v: continue
                o, n = v[name]; r = bytearray(s[o:o + n]); r[0::2], r[1::2] = r[1::2], r[0::2]; r = bytes(r)
                for q in (sn, sn2):
                    p = r.find(q)
                    if p >= 0: hit.append((name, hex(p)))
            if hit: print(' 램', os.path.basename(f), hit)
