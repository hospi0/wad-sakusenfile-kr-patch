# -*- coding: utf-8 -*-
"""반각 자리 ↔ 앞 빌드 단계(ASC16·GMS·턴·백업·연표·그림) 겹침 검사(디스크 안 씀)."""
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')
import asc_build, gms_build, ded_build, wmap_build, half_build as H
com, rom, C, miss, iso, E, syl = H.plan('K')
rd = lambda n: iso.read(*E[n][1:3])
extra = {}
o1, left, _ = asc_build.patch('K'); extra.update(o1)
o2, bad = gms_build.patch(); extra.update(o2)
g2_, tn, _, _ = ded_build.patch_turn(iso, E, extra['/GAME2.BIN']); extra['/GAME2.BIN'] = g2_; extra['/TURNASC.BIN'] = tn
extra['/RMC2.BIN'], extra['/RMC1.BIN'] = ded_build.patch_rmc(iso, E)
extra['/W_MAP2.BIN'] = wmap_build.patch(iso, E)
n = 0
for fn, o, c, t, v in C:
    if fn in extra:
        a, b = extra[fn][o:o + c], rd(fn)[o:o + c]
        if a != b: n += 1; print('겹침', fn, hex(o), t, v) if n < 20 else None
print('앞 단계와 겹친 자리', n, '파일', sorted({c[0] for c in C} & set(extra)))
dtc = [(o, c, t) for fn, o, c, t, v in C if fn == '/SAKUSEN/SAKU_DT.BIN']; m = 0
for f in sorted(glob.glob('work/gfx/v15/DT_*.bin')):
    a = int(f[-8:-4], 16); b = a + os.path.getsize(f)
    for o, c, t in dtc:
        if o < b and a < o + c: m += 1; print('그림 겹침', os.path.basename(f), hex(o), t)
print('SAKU_DT 그림 겹침', m, 'W_MAP2 글꼴 구역 앞 단계 변경', extra['/W_MAP2.BIN'][0x21A4:0x21A4 + 157 * 32] != rd('/W_MAP2.BIN')[0x21A4:0x21A4 + 157 * 32])
