# -*- coding: utf-8 -*-
"""작전파일(Sakusen File) 빌더.  python tools/build_f.py [--write]
   입력은 본편과 같은 번역표. 출력 work/disc_f/ (--write 일 때만).
   SAKU 문장·글꼴 / ASC16 / 반각 / 그림(본편 패치의 원본 바이트를 작전 디스크에서 찾아 같은 그림으로)."""
import sys, os, glob, re, struct, shutil, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso9660 import Iso
import build as BD, asc_build as AB, half_build as HB
sys.stdout.reconfigure(encoding='utf-8')
N = BD.N; KEEP = BD.KEEP
B = r'C:\claude\roms\ss\World Advanced Daisenryaku'
T1 = glob.glob(glob.glob(B + r'\*Sakusen*')[0] + r'\*(Track 1).bin')[0]
BASE = 0x2C0000; TBL = 0x1C040; TXT0 = 0x14196; NPTR = (0x1D65C - 0x1C040) // 4 + 1
strip = lambda t: re.sub('<[0-9A-F]+>', '', t.replace(N, ''))


def saku(iso, ent, log=print):
    rd = lambda n: iso.read(*ent[n][1:3])
    dt = bytearray(rd('/SAKUSEN/SAKU_DT.BIN'))
    ko = {}
    for l in open('work/text/ko_final.tsv', encoding='utf-8'):
        if l[0] != '#':
            i, g, v = l.rstrip('\n').split('\t', 2); ko[i] = v
    pos = []
    for l in open('work/text/master_pos.tsv', encoding='utf-8'):
        if l[0] == '#': continue
        i, tag, s, o, n = l.rstrip('\n').split('\t')
        if tag == 'F': pos.append((int(o, 16), i, int(s), int(n)))
    pos.sort()
    labels = [p for p in pos if p[0] < TXT0]; body = [p for p in pos if p[0] >= TXT0]
    assert len(body) == 41 * 8, len(body)
    ptrs = [struct.unpack_from('>I', dt, TBL + i * 4)[0] - BASE for i in range(NPTR)]
    cond = {p[0] for j, p in enumerate(body) if j % 8 >= 5}
    scen = collections.defaultdict(list)
    for j, p in enumerate(body): scen[j // 8 + 1].append(p)
    common = []
    for o, i, s, n in labels:
        for c in strip(ko[i]):
            if c not in BD.SYM and c not in common: common.append(c)
    assert KEEP + len(common) < 100
    cid = {c: KEEP + k for k, c in enumerate(common)}; first = KEEP + len(common)
    fonts = {}; maps = {}; over = []; FNS = sorted(x for x in ent if '/SAK_F' in x); assert len(FNS) == 41, len(FNS)
    for k in range(1, 42):
        fn = FNS[k - 1]; old = rd(fn); n = len(old) // 128; need = []
        for o, i, s, ln in scen[k]:
            for c in strip(ko[i]):
                if c not in BD.SYM and c not in cid and c not in need: need.append(c)
        mp = dict(cid); mp.update({c: first + j for j, c in enumerate(need)}); maps[k] = mp
        if first + len(need) > n: over.append((k, first + len(need), n))
        b = bytearray(old[:KEEP * 128]); b[25 * 128:26 * 128] = BD.glyph(':')
        for c in common + need: b += BD.glyph(c)
        b += bytes(max(0, len(old) - len(b))); fonts[fn] = bytes(b)
    log('SAKU 라벨', len(labels), '공통', len(common), '글꼴 넘침', over, '최대 칸', max(len(f) // 128 for f in fonts.values()))

    def enc(t, mp):
        w = []
        for tok in re.findall(r'<[0-9A-F]+>|' + re.escape(N) + '|.', t):
            if tok == N: w.append(1)
            elif tok[0] == '<' and len(tok) > 2: w.append(int(tok[1:-1], 16))
            elif tok in BD.SYM: w.append(BD.SYM[tok])
            else: w.append(mp[tok])
        return struct.pack('>%dH' % len(w), *w) + b'\xff\xff'
    lab_over = []
    for o, i, s, n in labels:
        e = enc(ko[i], cid)
        if len(e) > n * 2 + 2: lab_over.append((i, n, ko[i])); continue
        dt[o:o + n * 2 + 2] = e[:-2] + b'\0\0' * ((n * 2 + 2 - len(e)) // 2) + b'\xff\xff'
    newoff = {}; pool = {}; area = bytearray()
    for k in range(1, 42):
        for o, i, s, ln in scen[k]:
            t = ko[i]
            if o in cond: t = BD.pad8(t)
            elif len(strip(t)) > 19: t = BD.wrap(t)
            e = enc(t, maps[k]); key = (k, e)
            if key not in pool: pool[key] = TXT0 + len(area); area += e
            newoff[o] = pool[key]
    miss = sorted({hex(p) for p in ptrs if p not in newoff})
    log('SAKU 문장', len(body), '새 크기', len(area), '가능', TBL - TXT0, '여유', TBL - TXT0 - len(area), '라벨 넘침', lab_over[:8], '표에 없는 위치', len(miss), miss[:8])
    assert not over and not lab_over and len(area) <= TBL - TXT0
    dt[TXT0:TBL] = area + bytes(TBL - TXT0 - len(area))
    for i, p in enumerate(ptrs):
        if p in newoff: struct.pack_into('>I', dt, TBL + i * 4, newoff[p] + BASE)
    return bytes(dt), fonts


def gfx(iso, ent, extra, log=print):
    """본편 그림 패치: 원본 바이트를 작전 파일에서 찾아 같은 새 그림으로."""
    ik = Iso(BD.T1); ek = {f[0]: f for f in ik.walk()}
    F = {}
    def get(fn):
        if fn not in F: F[fn] = bytearray(extra.get(fn) or iso.read(*ent[fn][1:3]))
        return F[fn]
    dat = {}
    for fn, e in ent.items():
        if fn.endswith(('.MUS', '.CPK', '/')) or e[2] < 64 or fn.startswith(('/CDDA', '/UNIT3D', '/UNITPACK', '/UNITINIT', '/EARTH', '/VIEWMAP', '/RBG')) or '/SAK_' in fn: continue
        try: dat[fn] = iso.read(*e[1:3])
        except EOFError: pass
    J = []
    for f in sorted(glob.glob('work/gfx/v15/DT_*.bin')): J.append(('/SAKUSEN/SAKU_DT.BIN', int(f[-8:-4], 16), open(f, 'rb').read()))
    for f in sorted(glob.glob('work/gfx/v15/GMS2_*.bin') + glob.glob('work/gfx/r6/GMS2_*.bin')): J.append(('/GMS2.BIN', int(os.path.basename(f)[5:-4], 16), open(f, 'rb').read()))
    for l in open(BD.PANEL, encoding='utf-8'):
        fn, oh, hx = l.rstrip('\n').split('\t'); J.append((fn, int(oh, 16), bytes.fromhex(hx)))
    done = collections.Counter(); none = []
    for fn, o, new in J:
        old = ik.read(*ek[fn][1:3])[o:o + len(new)]; hit = 0
        for fn2, d in dat.items():
            q = -1
            while True:
                q = d.find(old, q + 1)
                if q < 0: break
                get(fn2)[q:q + len(new)] = new; hit += 1; done[fn2] += 1
        if not hit: none.append((fn, hex(o), len(new)))
    log('그림 자리', done.most_common(10), '작전에 없음', len(none), none[:14])
    for f in sorted(glob.glob('work/gfx/m2/F_*.bin')):
        fn = '/SAKUSEN/%s.BIN' % os.path.basename(f)[2:-4]; b = open(f, 'rb').read(); d = get(fn); assert len(b) <= len(d), fn; d[:len(b)] = b
    return {k: bytes(v) for k, v in F.items()}


def main():
    import punct; punct.guard()
    iso = Iso(T1); ent = {f[0]: f for f in iso.walk()}
    extra = {}
    dt, fonts = saku(iso, ent)
    extra['/SAKUSEN/SAKU_DT.BIN'] = dt; extra.update(fonts)
    o1, left, M = AB.patch('F'); extra.update(o1)
    print('ASC16 파일', len(o1), '못 넣은 줄', left[:12])
    o3, _ = HB.patch('F', extra); extra.update(o3)
    import ded_f, ded_build as DB, wmap_build as WM
    extra['/RMC2.BIN'], extra['/RMC1.BIN'] = DB.patch_rmc(iso, ent)
    extra.update(ded_f.patch(iso, ent, extra))
    extra.update(ded_f.patch_end(iso, ent))
    wm = WM.patch(iso, ent, cfg=(0x2CC1C, 0x2A850, 0x2B388))
    wx = extra.get('/W_MAP2.BIN'); wo = iso.read(*ent['/W_MAP2.BIN'][1:3])
    if wx:                                                   # 반각 사본 칸은 앞 단계 결과 유지
        wb = bytearray(wm)
        for i_ in range(0, 0x2090 + 157 * 32):
            if wx[i_] != wo[i_]: wb[i_] = wx[i_]
        wm = bytes(wb)
    extra['/W_MAP2.BIN'] = wm
    extra.update(gfx(iso, ent, extra))
    # 칸 맵 표: 본편과 같은 줄을 찾아 같은 고침(수입 줄 빈 자리)
    ik_ = Iso(BD.T1); ek_ = {f[0]: f for f in ik_.walk()}; gk = ik_.read(*ek_['/GAME2.BIN'][1:3]); g_ = bytearray(extra['/GAME2.BIN'])
    for l in open(BD.PANEL.replace('cells', 'map'), encoding='utf-8'):
        fn, oh, hx = l.rstrip('\n').split('\t'); o_ = int(oh, 16); ctx = gk[o_ - 8:o_ + 10]; q_ = g_.find(ctx)
        assert q_ >= 0 and g_.count(ctx) == 1, hex(o_)
        g_[q_ + 8:q_ + 10] = bytes.fromhex(hx); print(' 맵 고침', hex(q_ + 8))
    extra['/GAME2.BIN'] = bytes(g_)
    # 작전 전용 그림: 제목 띠, 병기 타입 메뉴
    t_ = bytearray(extra.get('/DAI_TIT1.DC') or iso.read(*ent['/DAI_TIT1.DC'][1:3])); b_ = open('work/gfx/ft2/F_DAI_TIT1.bin', 'rb').read(); t_[0x200:0x200 + len(b_)] = b_; extra['/DAI_TIT1.DC'] = bytes(t_)
    g2_ = bytearray(extra.get('/GMS2.BIN') or iso.read(*ent['/GMS2.BIN'][1:3])); b_ = open('work/gfx/ty2/GMS2_31A40.bin', 'rb').read(); g2_[0x31A40:0x31A40 + len(b_)] = b_
    b_ = open('work/gfx/tysel/GMS2_37BE0.bin', 'rb').read(); assert len(b_) == 5 * 0xF00; g2_[0x37BE0:0x37BE0 + len(b_)] = b_; extra['/GMS2.BIN'] = bytes(g2_)   # 선택 줄 밝은 그림 5장
    # DAI_TXT 는 본편과 같은 파일
    extra['/DAI_TXT.DC'] = open('work/gfx/d4/DAI_TXT.bin', 'rb').read() + iso.read(*ent['/DAI_TXT.DC'][1:3])[os.path.getsize('work/gfx/d4/DAI_TXT.bin'):]
    print('바뀐 파일', len(extra))
    if '--write' not in sys.argv: return
    assert not left
    os.makedirs('work/disc_f', exist_ok=True)
    dst = os.path.join('work/disc_f', os.path.basename(T1)); shutil.copyfile(T1, dst)
    from discwrite import TrackWriter
    w = TrackWriter(dst, 0)
    for fn, b in extra.items():
        assert len(b) == ent[fn][2], fn
        w.write_user(ent[fn][1], 0, b)
    if hasattr(w, 'finish'): w.finish()
    elif hasattr(w, 'close'): w.close()
    print('완료', dst)


if __name__ == '__main__':
    main()
