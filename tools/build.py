# -*- coding: utf-8 -*-
"""강철의 전풍 시험 빌더: 시나리오 문장·글꼴(SAKU_DT, SAKU_Fnn).  python tools/build.py [--write]
  입력 work/text/ko_final.tsv · master_pos.tsv. 출력 work/disc/ (--write 일 때만).
  글꼴 칸: 0~24 기호·숫자 그대로, 25~ 공통 라벨 글자(54개 글꼴 같은 번호), 그 뒤 시나리오 글자.
  문장: 라벨은 제자리(원래 길이 안), 시나리오 문장은 0x17FE2~ 표 앞까지 다시 깔고 포인터 표 고침. 같은 문장은 한 번만."""
import sys, os, glob, re, struct, shutil, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso9660 import Iso
import bdf
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\claude\roms\ss\World Advanced Daisenryaku'
ROM = glob.glob(B + r'\*Koutetsu*')[0]
T1 = glob.glob(ROM + r'\*(Track 1).bin')[0]
BASE = 0x2C0000; TBL = 0x25E3C; TXT0 = 0x17FE2; NPTR = 432
WRAP = 19
N = chr(92) + 'l'
SYM = {'０': 2, '１': 3, '２': 4, '３': 5, '４': 6, '５': 7, '６': 8, '７': 9, '８': 10, '９': 11, '0': 2, '1': 3, '2': 4, '3': 5, '4': 6, '5': 7, '6': 8, '7': 9, '8': 10, '9': 11,
       '+': 12, '-': 13, '－': 13, '.': 17, '．': 17, '・': 18, '·': 18, "'": 19, '=': 20, '/': 21, '?': 22, '？': 22, '!': 23, '！': 23, '%': 24, ':': 25, '：': 25, ' ': 0, '　': 0}
FONT = bdf.Font(r'C:\claude\utils\font\Galmuri-v2.40.3\Galmuri14.bdf')


_OY = []
def OY():
    if not _OY:
        ys = [p[1] for p in FONT.draw('한')[0]]; _OY.append((16 - (max(ys) - min(ys) + 1)) // 2 - min(ys))
    return _OY[0]


def glyph(c):
    """16×16 4비트: 글자 15, 둘레 1. 셀 순서 TL TR BL BR."""
    pts, w = FONT.draw(c)
    a = np.zeros((16, 16), np.uint8)
    if pts:
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        ox = (16 - (max(xs) - min(xs) + 1)) // 2 - min(xs); oy = OY()      # 세로는 글꼴 기준선 그대로(쉼표가 공중에 뜨지 않게)
        ink = [(x + ox, y + oy) for x, y in pts]
        for x, y in ink:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if 0 <= x + dx < 16 and 0 <= y + dy < 16: a[y + dy, x + dx] = 1
        for x, y in ink:
            if 0 <= x < 16 and 0 <= y < 16: a[y, x] = 15
    o = bytearray()
    for r0, c0 in ((0, 0), (0, 8), (8, 0), (8, 8)):
        for y in range(8):
            for x in range(0, 8, 2): o.append(a[r0 + y, c0 + x] << 4 | a[r0 + y, c0 + x + 1])
    return bytes(o)


PANEL = 'work/gfx/p13/cells.tsv'
KEEP = 26                                  # 0~25 원래 칸(숫자·기호, 25 = ':' — 코드·라벨이 직접 찍는다)


def pad8(s):
    """8칸 자동 접힘 창: 낱말이 줄을 넘으면 앞 줄을 공백으로 채워 다음 줄에서 시작."""
    if len(s) <= 8 or N in s: return s
    out = ''; cur = 0
    for w in s.split(' '):
        if cur and cur + 1 + len(w) > 8:
            out += ' ' * (8 - cur); cur = 0
        elif cur:
            out += ' '; cur += 1
        out += w; cur = (cur + len(w)) % 8
    return out


def wrap(s):
    """낱말 단위로 19칸에 맞춰 줄바꿈 코드 삽입. 원문 줄바꿈 유지."""
    out = []
    for para in s.split(N):
        line = ''
        for w in re.findall(r'[^ ]+ ?', para):
            if len(line) + len(w.rstrip()) > WRAP and line:
                out.append(line.rstrip()); line = ''
            while len(w.rstrip()) > WRAP:
                out.append(w[:WRAP]); w = w[WRAP:]
            line += w
        out.append(line.rstrip())
    return N.join(out)


def main():
    import punct; punct.guard()
    iso = Iso(T1); ent = {f[0]: f for f in iso.walk()}
    rd = lambda n: iso.read(*ent[n][1:3])
    dt = bytearray(rd('/SAKUSEN/SAKU_DT.BIN'))
    ko = {}
    for l in open('work/text/ko_final.tsv', encoding='utf-8'):
        if l[0] != '#': i, g, v = l.rstrip('\n').split('\t', 2); ko[i] = v
    pos = []
    for l in open('work/text/master_pos.tsv', encoding='utf-8'):
        if l[0] == '#': continue
        i, tag, s, o, n = l.rstrip('\n').split('\t')
        if tag == 'K': pos.append((int(o, 16), i, int(s), int(n)))
    pos.sort()
    titles = [struct.unpack_from('>I', dt, TBL + i * 20)[0] - BASE for i in range(54)]
    assert titles[0] == TXT0
    labels = [p for p in pos if p[0] < TXT0]; body = [p for p in pos if p[0] >= TXT0]
    strip = lambda t: re.sub('<[0-9A-F]+>', '', t.replace(N, ''))
    # 공통 라벨 글자
    common = []
    for o, i, s, n in labels:
        for c in strip(ko[i]):
            if c not in SYM and c not in common: common.append(c)
    print('라벨', len(labels), '공통 글자', len(common))
    assert KEEP + len(common) < 100
    cid = {c: KEEP + k for k, c in enumerate(common)}
    first = KEEP + len(common)
    # 시나리오: 제목 위치 이후 ~ 다음 제목 전. 첫 줄 조건은 앞 시나리오
    scen = collections.defaultdict(list)
    for p in body:
        k = sum(1 for t in titles if t <= p[0])
        scen[k].append(p)
    fonts = {}; maps = {}; over = []
    for k in range(1, 55):
        old = rd('/SAKUSEN/SAKU_F%02d.BIN' % k); n = len(old) // 128
        need = []
        for o, i, s, ln in scen[k]:
            for c in strip(ko[i]):
                if c not in SYM and c not in cid and c not in need: need.append(c)
        mp = dict(cid); mp.update({c: first + j for j, c in enumerate(need)}); maps[k] = mp
        tot = first + len(need)
        if tot > n: over.append((k, tot, n))
        b = bytearray(old[:KEEP * 128]); b[25 * 128:26 * 128] = glyph(':')
        for c in common + need: b += glyph(c)
        b += bytes(max(0, len(old) - len(b)))
        fonts[k] = bytes(b)
    print('글꼴 칸 넘침', len(over), over[:10], '최대', max(len(f) // 128 for f in fonts.values()))
    def enc(t, mp, raw=True):
        w = []
        for tok in re.findall(r'<[0-9A-F]+>|' + re.escape(N) + '|.', t):
            if tok == N: w.append(1)
            elif tok[0] == '<' and len(tok) > 2: w.append(int(tok[1:-1], 16))
            elif tok in SYM: w.append(SYM[tok])
            else: w.append(mp[tok])
        return struct.pack('>%dH' % len(w), *w) + b'\xff\xff'
    # 라벨 제자리
    lab_over = []
    for o, i, s, n in labels:
        e = enc(ko[i], cid)
        if len(e) > n * 2 + 2: lab_over.append((i, n, len(e) // 2 - 1, ko[i])); continue
        pad = n * 2 + 2 - len(e)
        dt[o:o + n * 2 + 2] = e[:-2] + b'\0\0' * (pad // 2) + b'\xff\xff'
    print('라벨 넘침', len(lab_over), lab_over[:14])
    # 시나리오 문장
    ptrs = [struct.unpack_from('>I', dt, TBL + i * 4)[0] - BASE for i in range(NPTR)]
    newoff = {}; q = TXT0; pool = {}; total = 0; cond = set(ptrs[270:])
    area = bytearray()
    for k in range(1, 55):
        for o, i, s, ln in scen[k]:
            t = ko[i]
            if o in cond: t = pad8(t)                          # 조건 줄(포인터 271번째~): 8칸 자동 접힘, 줄바꿈 코드 없음
            elif len(strip(t)) > 19: t = wrap(t)
            e = enc(t, maps[k]); key = (k, e)
            if key not in pool: pool[key] = TXT0 + len(area); area += e
            newoff[o] = pool[key]
    end = TXT0 + len(area)
    print('문장', len(body), '새 크기', len(area), '가능', TBL - TXT0, '여유', TBL - end)
    miss = [hex(p) for p in ptrs if p not in newoff]; print('표에 없는 위치', len(miss), miss[:6])
    if '--write' not in sys.argv: return
    assert end <= TBL and not over and not miss and not lab_over
    dt[TXT0:TBL] = area + bytes(TBL - end)
    for i, p in enumerate(ptrs): struct.pack_into('>I', dt, TBL + i * 4, newoff[p] + BASE)
    os.makedirs('work/disc', exist_ok=True)
    dst = os.path.join('work/disc', os.path.basename(T1))
    shutil.copyfile(T1, dst)                                  # 언제나 원본에서 새로
    import asc_build, gms_build
    extra = {}
    o1, left, _ = asc_build.patch('K'); extra.update(o1)
    assert not left, left
    o2, bad = gms_build.patch(); assert not bad, bad
    extra.update(o2)
    import ded_build
    g2_, tn, _, _ = ded_build.patch_turn(iso, ent, extra['/GAME2.BIN']); extra['/GAME2.BIN'] = g2_; extra['/TURNASC.BIN'] = tn
    extra['/RMC2.BIN'], extra['/RMC1.BIN'] = ded_build.patch_rmc(iso, ent)
    import wmap_build
    extra['/W_MAP2.BIN'] = wmap_build.patch(iso, ent)
    def over(fn, off, path):
        b = open(path, 'rb').read(); d = bytearray(extra.get(fn) or rd(fn))
        assert off + len(b) <= len(d), (fn, off, len(b), len(d))
        d[off:off + len(b)] = b; extra[fn] = bytes(d)
    for f in sorted(glob.glob('work/gfx/v15/DT_*.bin')):
        o = int(f[-8:-4], 16); b = open(f, 'rb').read(); dt[o:o + len(b)] = b
    for f in sorted(glob.glob('work/gfx/v15/GMS2_*.bin') + glob.glob('work/gfx/r6/GMS2_*.bin')):
        over('/GMS2.BIN', int(os.path.basename(f)[5:-4], 16), f)
    for n in ('TXT', 'MOV', 'MES'): over('/DAI_%s.DC' % n, 0, 'work/gfx/d4/DAI_%s.bin' % n)
    over('/DAI_TIT1.DC', 0x200, 'work/gfx/d4/DAI_TIT1.bin')
    for f in sorted(glob.glob('work/gfx/e12/*.bin')): over('/%s.EP' % os.path.basename(f)[:-4], 0, f)
    for f in sorted(glob.glob('work/gfx/m2/K_*.bin')): over('/SAKUSEN/%s.BIN' % os.path.basename(f)[2:-4], 0, f)
    import half_build
    extra['/SAKUSEN/SAKU_DT.BIN'] = bytes(dt)
    o3, _ = half_build.patch('K', extra); extra.update(o3)
    dt = bytearray(extra.pop('/SAKUSEN/SAKU_DT.BIN'))
    for l in open(PANEL, encoding='utf-8'):                  # 표 화면·유닛 정보·설정 버튼 칸 그림(tools/panel_kr.py)
        fn, oh, hx = l.rstrip(chr(10)).split(chr(9)); o_ = int(oh, 16); bb = bytes.fromhex(hx)
        d_ = bytearray(extra.get(fn) or rd(fn)); d_[o_:o_ + len(bb)] = bb; extra[fn] = bytes(d_)
    for l in open(PANEL.replace('cells', 'map'), encoding='utf-8'):   # 칸 맵 표 고침
        fn, oh, hx = l.rstrip(chr(10)).split(chr(9)); o_ = int(oh, 16); bb = bytes.fromhex(hx)
        d_ = bytearray(extra.get(fn) or rd(fn)); d_[o_:o_ + len(bb)] = bb; extra[fn] = bytes(d_)
    from discwrite import TrackWriter
    w = TrackWriter(dst, 0)
    w.write_user(ent['/SAKUSEN/SAKU_DT.BIN'][1], 0, bytes(dt))
    for k in range(1, 55):
        w.write_user(ent['/SAKUSEN/SAKU_F%02d.BIN' % k][1], 0, fonts[k])
    g2 = extra['/GMS2.BIN']; P = o2['/GMS2.BIN']
    for o, n in [(gms_build.STUB, gms_build.patch.stub)] + [(a_, c_) for a_, _, c_ in gms_build.patch.zones]:
        assert any(g2[o:o + n]) and P[o:o + n] == g2[o:o + n], ('뒤 단계에 덮임', hex(o))
    for fn, b_ in extra.items():
        assert len(b_) == ent[fn][2], fn
        w.write_user(ent[fn][1], 0, b_)
    print('추가 파일', len(extra))
    if hasattr(w, 'finish'): w.finish()
    elif hasattr(w, 'close'): w.close()
    print('완료', dst)


if __name__ == '__main__':
    main()
