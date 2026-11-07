# -*- coding: utf-8 -*-
"""VDP2 칸 그림 글자(표 화면·유닛 정보·설정 버튼) 한글화 미리보기.  python tools/panel_kr.py [폴더]
   상태 VRAM 8비트 칸에서 라벨을 지우고 한글을 그린 뒤, 칸 단위로 파일 위치를 찾아 패치 목록을 만든다.
   결과: 폴더/preview.png(왼쪽 원본, 오른쪽 새것, 실제 색), 폴더/cells.tsv(파일, 위치, 16진 64 B).  디스크는 안 건드림."""
import sys, os, collections, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mstate, asc_build as B, bdf
import numpy as np
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding='utf-8')
OUT = sys.argv[1] if len(sys.argv) > 1 else 'work/gfx/p1'; os.makedirs(OUT, exist_ok=True)
G14 = bdf.Font(r'C:\claude\utils\font\Galmuri-v2.40.3\Galmuri14.bdf')
G11 = bdf.Font(r'C:\claude\utils\font\Galmuri-v2.40.3\Galmuri11.bdf')
# 스테이트, 면, 화소 상자(x0,y0,x1,y1), 글자들, 세로?, 바탕(ref 칸 x 또는 None=줄 최빈), 글꼴
# 글자 x 직접 지정(하스피 «붙이고»). 공유 칸 때문에 움직일 수 있는 범위가 정해져 있다 — 충돌 0 으로 확인
MAPFIX = [(9, 16, 0x20532), (9, 19, 0x2063A)]; mapout = []
XS = {('20', (192, 120, 248, 136)): [194, 225], ('38', (104, 168, 168, 190)): [108, 152], ('38', (264, 168, 330, 190)): [266, 312], ('12', (247, 40, 279, 56)): [248, 264]}
J = [
    ('21', 0, (168, 24, 186, 39), '공', 0, 150, G11), ('21', 0, (240, 24, 258, 39), '육', 0, 222, G11), ('21', 0, (296, 24, 314, 39), '해', 0, 222, G11),
    ('20', 0, (56, 96, 104, 112), '군사비', 0, 120, G14), ('20', 0, (56, 120, 92, 136), '수 입', 0, 120, G14), ('20', 0, (56, 144, 92, 160), '수 입', 0, 120, G14),
    ('20', 0, (56, 168, 104, 184), '도시', 0, 120, G14), ('20', 0, (56, 192, 104, 208), '공항', 0, 120, G14),
    ('20', 0, (200, 96, 232, 112), '항', 0, 280, G14), ('20', 0, (192, 120, 248, 136), '병 력', 0, 280, G14),
    ('20', 0, (193, 145, 222, 159), '도시', 0, ('c', 257, 6), G14), ('20', 0, (226, 145, 254, 159), '공항', 0, ('c', 257, 6), G14), ('20', 0, (263, 145, 285, 159), '항', 0, ('c', 257, 6), G14), ('20', 0, (290, 145, 319, 159), '병력', 0, ('c', 257, 6), G14),
    ('20', 0, (146, 26, 192, 38), '군사비', 0, (150, 26, '21'), G11), ('20', 0, (208, 26, 240, 39), '수입', 0, (150, 26, '21'), G11), ('20', 0, (264, 26, 296, 39), '수입', 0, (150, 26, '21'), G11),
    ('12', 0, (16, 40, 48, 56), '이동', 0, 56, G14), ('12', 0, (88, 40, 120, 56), '연료', 0, 128, G14), ('12', 0, (184, 40, 216, 56), '색적', 0, 224, G14), ('12', 0, (247, 40, 279, 56), '대잠', 0, 224, G14), ('12', 0, (280, 40, 312, 56), '색적', 0, 224, G14),
    ('12', 0, (280, 120, 312, 136), '탑재', 0, 320, G14), ('12', 0, (16, 80, 32, 128), '방어력', 1, (56, 40), G14), ('12', 0, (24, 152, 72, 168), '공격력', 0, (56, 40), G14),
    ('38', 3, (24, 168, 86, 190), '시스템', 0, ('c', 88, 2), G11), ('38', 3, (104, 168, 168, 190), '입력', 0, ('c', 88, 2), G11), ('38', 3, (184, 168, 248, 190), '사운드', 0, ('c', 88, 2), G11), ('38', 3, (264, 168, 330, 190), '조작', 0, ('c', 88, 2), G11),
]
iso, E = B.disc('K')
Fs = {}
for fn, e in E.items():
    if fn.endswith(('.MUS', '.CPK', '/')) or e[2] < 64 or fn.startswith(('/CDDA', '/UNIT3D', '/UNITPACK', '/UNITINIT', '/EARTH', '/DAI_SF', '/VIEWMAP', '/RBG')) or 'SAKU' in fn: continue
    try: Fs[fn] = iso.read(*e[1:3])
    except EOFError: pass


def load(st, p):
    s, v = mstate.load('work/states/%s.state' % st)
    def sw(k):
        o, n = v[k]; b = bytearray(s[o:o + n]); b[0::2], b[1::2] = b[1::2], b[0::2]; return bytes(b)
    vr = sw('VDP2/VRAM'); co, cn = v['VDP2/CRAM']
    cr = np.frombuffer(bytes(s[co:co + cn]), '<u2').astype(int)            # CRAM 은 뒤집지 않음(화면 스샷 대조)
    a, c = v['VDP2/RawRegs']; r = [int(x) for x in np.frombuffer(s[a:a + c], '<u2')]; R = lambda x: r[x // 2]
    mp = {0: R(0x40), 1: R(0x44), 2: R(0x48), 3: R(0x4C)}[p] & 0x3F; base = (R(0x30 + p * 2) >> 2 & 7) << 12
    m = np.frombuffer(vr[mp * 0x2000:mp * 0x2000 + 0x2000], '>u2').reshape(64, 64).astype(int)
    nz = m[m != 0]; bank = (int(np.bincount(nz >> 12 & 7).argmax()) << 8)     # 맵 윗비트 = 팔레트(8비트 칸은 256색 단위)
    return vr, cr, m, base, bank


def cellimg(vr, t): return np.frombuffer(vr[t * 32:t * 32 + 64], np.uint8).reshape(8, 8)


def rgb(a, cr, bank):
    v = cr[(a.astype(int) + bank) & 0x7FF]
    return np.stack([(v & 31) << 3, (v >> 5 & 31) << 3, (v >> 10 & 31) << 3], 2).astype(np.uint8)


def lum(cr, bank, i):
    v = int(cr[(int(i) + bank) & 0x7FF]); return (v & 31) * 3 + (v >> 5 & 31) * 6 + (v >> 10 & 31)


def glyph_mask(c, font):
    pts, _ = font.draw(c); xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    w, h = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1; m = np.zeros((h, w), bool)
    for x, y in pts: m[y - min(ys), x - min(xs)] = True
    return m


# 라벨 상자 밖(다른 화면 포함)에서 쓰이는 칸 = 절대 건드리지 않음. 스테이트 전부에서 8비트 면의 칸 내용을 모은다
import glob
BOXES = collections.defaultdict(list)
for j in J: BOXES[(j[0], j[1])].append(j[2])
OUTSIDE = set()
POS = collections.defaultdict(set)                       # 라벨 상자 칸: 다른 화면에 같은 자리·같은 내용이면 같은 라벨(설정 버튼 17·38·39·40)
for (st_, pl0), bxs in BOXES.items():
    vr0, _c, m0, base0, _b = load(st_, pl0)
    for q in bxs:
        for y in range(q[1] // 8, (q[3] + 7) // 8):
            for x in range(q[0] // 8, (q[2] + 7) // 8):
                t = (int(m0[y, x]) & 0xFFF) + base0; POS[(x, y)].add(vr0[t * 32:t * 32 + 64])
for f in glob.glob('work/states/*.state'):
    stn = os.path.basename(f)[:-6]
    s_, v_ = mstate.load(f)
    if 'VDP2/VRAM' not in v_: continue
    o_, n_ = v_['VDP2/VRAM']; b_ = bytearray(s_[o_:o_ + n_]); b_[0::2], b_[1::2] = b_[1::2], b_[0::2]; vr_ = bytes(b_)
    a_, c_ = v_['VDP2/RawRegs']; r_ = [int(x) for x in np.frombuffer(s_[a_:a_ + c_], '<u2')]
    ch = {0: r_[0x28 // 2] >> 4 & 7, 1: r_[0x28 // 2] >> 12 & 3, 2: r_[0x2A // 2] >> 1 & 1, 3: r_[0x2A // 2] >> 5 & 1}
    for pl_, reg, mr in ((0, 0x30, 0x40), (1, 0x32, 0x44), (2, 0x34, 0x48), (3, 0x36, 0x4C)):
        if not r_[0x20 // 2] >> pl_ & 1 or not ch[pl_]: continue
        base_ = (r_[reg // 2] >> 2 & 7) << 12; mp_ = r_[mr // 2] & 0x3F
        mm = np.frombuffer(vr_[mp_ * 0x2000:mp_ * 0x2000 + 0x2000], '>u2').reshape(64, 64).astype(int)
        bx = BOXES.get((stn, pl_), [])
        for y in range(64):
            for x in range(64):
                if any(x * 8 < q[2] and x * 8 + 8 > q[0] and y * 8 < q[3] and y * 8 + 8 > q[1] for q in bx): continue
                if stn in ('20',) and pl_ == 0 and (x, y) in ((9, 16), (9, 19)): continue
                t = (int(mm[y, x]) & 0xFFF) + base_; cb_ = vr_[t * 32:t * 32 + 64]
                if cb_ in POS.get((x, y), ()): continue
                OUTSIDE.add(cb_)
print('상자 밖 칸 내용', len(OUTSIDE), flush=True)
shared = []; rows = []; cache = {}; m_of = {}; clipped = collections.Counter()


def run_jobs(BLANK):
    rows.clear(); clipped.clear()
    for k_, c_ in cache.items(): c_[4][:] = c_[3]
    for st, p, box, text, vert, ref, font in J:
        if (st, p) not in cache:
            vr, cr, m, base, bank = load(st, p); tl = (m & 0xFFF) + base
            g = np.zeros((256, 368), np.uint8)
            for y in range(32):
                for x in range(46):
                    g[y * 8:y * 8 + 8, x * 8:x * 8 + 8] = cellimg(vr, int(tl[y, x]))
            if st == '20':                                      # 수입 줄 빈 자리(9,16)·(9,19)는 력과 함께 쓰던 칸 → 바탕 칸으로 돌려 0x15AC 를 력 전용으로
                for x_, y_, rowf in MAPFIX:
                    old_ = int(tl[y_, x_]); tl[y_, x_] = tl[y_, 13]; m[y_, x_] = m[y_, 13]
                    g[y_ * 8:y_ * 8 + 8, x_ * 8:x_ * 8 + 8] = cellimg(vr, int(tl[y_, x_]))
                    mapout.append(('/GAME2.BIN', rowf + (x_ - 5) * 2, struct.pack('>H', old_ & 0xFFF), struct.pack('>H', (int(m[y_, x_]) & 0xFFF) - 0x400)))
            cache[(st, p)] = (vr, cr, tl, g.copy(), g, bank); m_of[(st, p)] = m
        vr, cr, tl, g0, g, bank = cache[(st, p)]
        x0, y0, x1, y1 = box; sub = g0[y0:y1, x0:x1]
        bank = (int(m_of[(st, p)][y0 // 8, x0 // 8]) >> 12 & 7) << 8
        # 바탕
        bgim = np.zeros_like(sub)
        for y in range(y1 - y0):
            for x in range(x1 - x0):
                if isinstance(ref, tuple) and ref[0] == 'c':
                    bgim[y, x] = g0[y0 + y, ref[1] + (x0 + x) % ref[2]]
                elif isinstance(ref, tuple):
                    src = cache[(ref[2], 0)][3] if len(ref) > 2 else g0
                    bgim[y, x] = src[ref[1] + y % 16, ref[0] + (x0 + x - ref[0]) % 16]
                elif ref is not None:
                    bgim[y, x] = g0[y0 + y, ref + (x0 + x - ref) % 16]
                else:
                    par = sub[y, (x % 2)::2]; bgim[y, x] = np.bincount(par).argmax()
        if ref is None:
            # 세로 방향 줄 바탕: 줄 최빈이 글자색이면 상자 왼쪽 바깥 같은 줄로
            for y in range(y1 - y0):
                for par in (0, 1):
                    col = g0[y0 + y, max(0, x0 - 6 + par):x0:2]
                    if len(col):
                        bgim[y, par::2] = np.bincount(col).argmax() if lum(cr, bank, bgim[y, par]) < 30 else bgim[y, par]
        diff = sub != bgim
        Lv = np.vectorize(lambda i: lum(cr, bank, i))(sub)
        inkvals = sub[diff & (Lv <= np.percentile(Lv, 25))]; ink = np.bincount(inkvals).argmax() if len(inkvals) else sub.min()
        hivals = sub[diff & (Lv >= np.percentile(Lv, 75))]; hi = np.bincount(hivals).argmax() if len(hivals) else ink
        ys, xs = np.nonzero(diff)
        ex0, ex1 = (xs.min(), xs.max()) if len(xs) else (0, x1 - x0 - 1); ey0, ey1 = (ys.min(), ys.max()) if len(ys) else (0, y1 - y0 - 1)
        def cellb(px, py):
            cx_, cy_ = (x0 + px) // 8, (y0 + py) // 8
            return g0[cy_ * 8:cy_ * 8 + 8, cx_ * 8:cx_ * 8 + 8].tobytes()
        froz = np.zeros(sub.shape, bool); noink = np.zeros(sub.shape, bool)
        for py in range(sub.shape[0]):
            for px in range(sub.shape[1]):
                k0 = cellb(px, py)
                if k0 in OUTSIDE: froz[py, px] = True
                if k0 in BLANK: noink[py, px] = True
        new = sub.copy(); new[diff & ~froz] = bgim[diff & ~froz]; ms = [glyph_mask(c, font) for c in text.replace(' ', '')]; n = len(ms)
        if ' ' in text: ex1 = x1 - x0 - 1                     # 띄움: 상자 끝까지 벌려 공유 칸을 피함
        for i, gm in enumerate(ms):
            h, w = gm.shape
            if vert:
                cy = (ey0 + ey1 - h) // 2 if n == 1 else ey0 + (ey1 - ey0 + 1 - h) * i // (n - 1); cx = (ex0 + ex1 + 1 - w) // 2
            else:
                cx = (ex0 + ex1 + 1 - w) // 2 if n == 1 else ex0 + (ex1 - ex0 + 1 - w) * i // (n - 1); cy = (ey0 + ey1 + 1 - h) // 2
                if (st, box) in XS: cx = XS[(st, box)][i] - x0
                if st == '38': cy = 176 - y0                       # 버튼 글자 높이 통일(20번 줄은 공유 칸)
            for yy in range(h):
                for xx in range(w):
                    if gm[yy, xx]:
                        a, b_ = cy + yy + 1, cx + xx + 1
                        if 0 <= a < new.shape[0] and 0 <= b_ < new.shape[1] and not froz[a, b_] and not noink[a, b_]: new[a, b_] = hi
            for yy in range(h):
                for xx in range(w):
                    if gm[yy, xx] and 0 <= cy + yy < new.shape[0] and 0 <= cx + xx < new.shape[1]:
                        if froz[cy + yy, cx + xx] or noink[cy + yy, cx + xx]: clipped[(st, text)] += 1
                        else: new[cy + yy, cx + xx] = ink
        g[y0:y1, x0:x1] = new
        rows.append((st, p, box, text, g0[y0:y1, x0:x1].copy(), new.copy(), cr, bank))


run_jobs(set())
# 같은 칸 내용이 상자마다 다르게 나오면 글자를 빼고 다시(바탕만)
BLANK = set()
for _ in range(4):
    res = collections.defaultdict(set)
    for key, c_ in cache.items():
        g0_, g_ = c_[3], c_[4]
        for y in range(32):
            for x in range(46):
                a_, b_ = g0_[y * 8:y * 8 + 8, x * 8:x * 8 + 8], g_[y * 8:y * 8 + 8, x * 8:x * 8 + 8]
                if not (a_ == b_).all(): res[a_.tobytes()].add(b_.tobytes())
    bad = {k for k, v in res.items() if len(v) > 1} - BLANK
    print('다른 그림 칸', len(bad), flush=True)
    if not bad: break
    BLANK |= bad; run_jobs(BLANK)
# BLANK 칸은 첫 결과로 통일
first = {}
for key, c_ in cache.items():
    g0_, g_ = c_[3], c_[4]
    for y in range(32):
        for x in range(46):
            a_ = g0_[y * 8:y * 8 + 8, x * 8:x * 8 + 8].tobytes()
            if a_ in BLANK:
                b_ = g_[y * 8:y * 8 + 8, x * 8:x * 8 + 8]
                if a_ not in first and b_.tobytes() != a_: first[a_] = b_.copy()
                elif a_ in first: g_[y * 8:y * 8 + 8, x * 8:x * 8 + 8] = first[a_]
print('글자 잘린 화소', dict(clipped))
# 최종 검사: 바뀐 칸 내용이 상자 밖에서 쓰이면 중단
viol = 0
for key, c_ in cache.items():
    g0_, g_ = c_[3], c_[4]
    for y in range(32):
        for x in range(46):
            a_, b_ = g0_[y * 8:y * 8 + 8, x * 8:x * 8 + 8], g_[y * 8:y * 8 + 8, x * 8:x * 8 + 8]
            if not (a_ == b_).all() and a_.tobytes() in OUTSIDE: viol += 1
assert not viol, viol
print('상자 밖 칸 변경 0', flush=True)
g0_ = cache[('38', 3)][3]
for y in range(20, 24):
    print('버튼 줄', y, ''.join('#' if g0_[y * 8:y * 8 + 8, x * 8:x * 8 + 8].tobytes() in OUTSIDE else ('b' if g0_[y * 8:y * 8 + 8, x * 8:x * 8 + 8].tobytes() in BLANK else '.') for x in range(46)))
g0_ = cache[('20', 0)][3]
for y in (15, 16):
    print('병력 줄', y, ''.join('#' if g0_[y * 8:y * 8 + 8, x * 8:x * 8 + 8].tobytes() in OUTSIDE else ('b' if g0_[y * 8:y * 8 + 8, x * 8:x * 8 + 8].tobytes() in BLANK else '.') for x in range(46)))
# 칸 → 파일
used = collections.Counter()
for (st, p), (vr, cr, tl, g0, g, bank) in cache.items():
    for t in tl.flat: used[(st, p, int(t))] += 1
out = []; missing = []; conflict = []
for (st, p), (vr, cr, tl, g0, g, bank) in cache.items():
    seen = {}
    for y in range(32):
        for x in range(46):
            a, b = g0[y * 8:y * 8 + 8, x * 8:x * 8 + 8], g[y * 8:y * 8 + 8, x * 8:x * 8 + 8]
            if (a == b).all(): continue
            t = int(tl[y, x])
            if t in seen:
                if seen[t] != b.tobytes(): conflict.append((st, p, x, y, hex(t)))
                continue
            seen[t] = b.tobytes()
            if used[(st, p, t)] > 1: shared.append((st, p, x, y, hex(t), used[(st, p, t)]))
            raw = a.tobytes(); hits = []
            for fn, d in Fs.items():
                q = -1
                while True:
                    q = d.find(raw, q + 1)
                    if q < 0: break
                    hits.append((fn, q))
            if not hits: missing.append((st, p, x, y, hex(t)))
            for fn, q in hits: out.append((fn, q, b.tobytes().hex()))
seen_m = set(); open(OUT + '/map.tsv', 'w', encoding='utf-8', newline='\n').write(''.join('%s\t%X\t%s\n' % (r[0], r[1], r[3].hex()) for r in mapout if not (r[1] in seen_m or seen_m.add(r[1]))))
open(OUT + '/cells.tsv', 'w', encoding='utf-8', newline='\n').write(''.join('%s\t%X\t%s\n' % r for r in out))
print('충돌 칸(같은 칸에 다른 그림)', len(conflict), conflict[:30]); print('칸', len(out), '공유 칸', len(shared), shared[:30]); print('출처 없음', missing[:20]); print(collections.Counter(r[0] for r in out))
S = 3; W = 2 * 80 * S + 40; H = sum((r[4].shape[0] * S + 8) for r in rows); pg = Image.new('RGB', (W, H), (40, 40, 60)); y = 0; d = ImageDraw.Draw(pg)
for st, p, box, text, src, new, cr, bank in rows:
    for i, a in enumerate((src, new)):
        im = Image.fromarray(rgb(a, cr, bank)); pg.paste(im.resize((im.width * S, im.height * S), 0), (i * (80 * S + 20) + 4, y))
    y += src.shape[0] * S + 8
pg.save(OUT + '/preview.png'); print(pg.size)
# 면 전체 전후(라벨 상자 밖 찌꺼기 확인)
for key, (vr_, cr_, tl_, g0_, g_, _b) in cache.items():
    m_ = m_of[key]; pl = ((m_ >> 12 & 7) << 8)
    ex = np.zeros((256, 368), int)
    for y in range(32):
        for x in range(46): ex[y * 8:y * 8 + 8, x * 8:x * 8 + 8] = int(pl[y, x])
    both = []
    for a_ in (g0_, g_):
        v_ = cr_[(a_.astype(int) + ex) & 0x7FF]
        both.append(np.stack([(v_ & 31) << 3, (v_ >> 5 & 31) << 3, (v_ >> 10 & 31) << 3], 2).astype(np.uint8))
    Image.fromarray(np.vstack(both)).resize((368 * 3, 512 * 3), 0).save(OUT + '/면_%s_%d_위원본_아래새것.png' % key)
# 스프라이트 空·陸·海 (GAME2 16×16 8비트, 팔레트 0x100 — 18번 화면과 화소 일치 확인)
vrc, crc, tlc, g0c, _, _ = cache[('20', 0)]; b100 = 0x100
L = lambda i: lum(crc, b100, i)
pg2 = Image.new('RGB', (4 * 16 * 4 + 30, 3 * 16 * 4 + 12), (40, 40, 60)); more = []
for k, (o, c) in enumerate(((0x2ADC0, '공'), (0x2AEC0, '육'), (0x2AFC0, '해'))):
    src = np.frombuffer(Fs['/GAME2.BIN'][o:o + 256], np.uint8).reshape(16, 16); a = src.copy()
    ref = g0c[98 + np.arange(16) % 14][:, 280 + np.arange(16)]
    lv = np.vectorize(L)(a); ink = a[lv <= np.percentile(lv, 15)]; ink = int(np.bincount(ink).argmax()); hi = a[lv >= np.percentile(lv, 90)]; hi = int(np.bincount(hi).argmax())
    # 가장자리(글자 없는 테두리 1줄)는 남기고 안쪽을 바탕으로
    a[:, :] = ref                                           # 가장자리까지 원본 글자가 닿아 있어 전체를 바탕으로
    gm = glyph_mask(c, G14); h, w = gm.shape; cy, cx = (16 - h) // 2, (16 - w) // 2
    for yy in range(h):
        for xx in range(w):
            if gm[yy, xx] and cy + yy + 1 < 16 and cx + xx + 1 < 16: a[cy + yy + 1, cx + xx + 1] = hi
    for yy in range(h):
        for xx in range(w):
            if gm[yy, xx]: a[cy + yy, cx + xx] = ink
    for fn, d in Fs.items():
        q = -1
        while True:
            q = d.find(src.tobytes(), q + 1)
            if q < 0: break
            more.append((fn, q, a.tobytes().hex()))
    for i, x in enumerate((src, a)):
        im = Image.fromarray(rgb(x, crc, b100)); pg2.paste(im.resize((64, 64), 0), (i * 80 + 4, k * 68 + 4))
pg2.save(OUT + '/sprite_preview.png')
open(OUT + '/cells.tsv', 'a', encoding='utf-8', newline='\n').write(''.join('%s\t%X\t%s\n' % r for r in more)); print('스프라이트 자리', [(r[0], hex(r[1])) for r in more])
