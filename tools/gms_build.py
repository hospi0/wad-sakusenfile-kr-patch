# -*- coding: utf-8 -*-
"""본편 GMS2 전용 글꼴(맵 이름·화면 제목) 패치. 번호→칸 표(GMS1 0x13D0 → GMS2)를 옮겨 늘리고, 100번부터는 스텁으로 VRAM 0xB320~ 에 복사.
   python tools/gms_build.py  = 검사만."""
import sys, os, struct, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B, asc_table
sys.stdout.reconfigure(encoding='utf-8')
FONT = 0xD95C; NF = 99
TBL0 = 0x1AAC                               # 원래 번호→칸 표(번호마다 4워드, 0~99)
DIG = '0123456789年月日'                      # 0x14DE 번호표: 코드가 숫자·년월일을 이 표로 찍는다. 바로 뒤에 첫 맵 이름이 구분 없이 붙어 있다
ZEND2 = 0x1C026                             # 띠 뒤쪽 빈 구역 시작
Z2END = 0x1C5A6
# 0x199A6~0x1C5A6 은 352×32 띠 스프라이트의 투명 줄이다. 글자·표를 잠깐 두었다가 스텁이 VRAM·램으로 옮기고 0 으로 지운다
# (스프라이트 적재는 복사 호출 뒤 0x2000C8 표에서 일어난다). 옛 표 자리(0x1AAC)는 스프라이트가 아니라 스텁·글자가 남아도 된다.
STUB = TBL0; STUBMAX = 288                  # 스텁 자리
Z1 = 0x19802; Z1END = 0x1A086              # 앞 그림(0x18CA6) 투명 줄 + 띠 투명 줄
ZONES = [(Z1, 17), (TBL0 + STUBMAX, 4), (ZEND2, 11)]  # 글자 자리(파일 위치, 글자 수)
RTBL = 0x2F8000                             # 실행 때 표가 살 램(GMS 스테이트 전부 0)
CELL = 0x599                                # 100번 칸(참조·내용 없는 곳. 0x28D~ 는 세계 지도 쪽이 빈칸으로 참조)
VR = 0x25E00000 + CELL * 32
FW = (('ズzゲーム', 'ゲーム'), ('インパール', 'インバール'), ('画?', '画面'), ('ラパウル', 'ラバウル'), ('ポウエイ', 'ボウエイ'), ('へンダ', 'ヘンダ'), ('パルジ', 'バルジ'), ('スラピア', 'スラビア'))


def rows():
    K = {}
    for f in ('work/text/ko_extra.tsv', 'work/text/ko_extra2.tsv'):
        for l in open(f, encoding='utf-8'):
            if l[0] != '#':
                p = l.rstrip('\n').split('\t')
                if len(p) > 1: K[p[0]] = p[-1]
    R = {}
    for f in ('work/text/extra.tsv', 'work/text/extra2.tsv'):
        for l in open(f, encoding='utf-8'):
            if l[0] != '#':
                p = l.split('\t')
                if p[1] in ('M', 'KG') and K.get(p[0]): R[p[4].replace('　', '').replace(DIG, '')] = K[p[0]]
    R['開始'] = '시작'; R['D-DAY'] = '디데이'
    R['記録日時'] = '기록일시'
    return R


def table(iso, E):
    rk = lambda n: iso.read(*E[n][1:3])
    mp = rk('/VIEWCG/ASC16MAP.BIN'); cg = rk('/VIEWCG/ASC16X16.BIN') + rk('/VIEWCG/ASC16_2.BIN')
    w = struct.unpack('>%dH' % (len(mp) // 2), mp); G = {}
    for i in range(len(w) // 4):
        g = b''.join(cg[(t - 0x800) * 32:(t - 0x800) * 32 + 32] for t in w[i * 4:i * 4 + 4]); G.setdefault(g, asc_table.SHEET[i])
    d = rk('/GMS2.BIN')
    return d, [G.get(d[FONT + i * 128:FONT + i * 128 + 128], '?') for i in range(NF)]


def runs(d, L):
    """문자열 자리: (시작, 칸 수(끝 표지 전까지), 원문)."""
    out = []
    W = lambda o: struct.unpack_from('>H', d, o)[0]
    for a, b in ((0x14A0, 0x1A00), (0x11930, 0x11A00)):
        o = a
        while o < b:
            x = W(o)
            if 1 <= x <= NF:
                st = o; s = ''
                while o < b + 64 and W(o) <= NF:
                    s += L[W(o) - 1] if W(o) else '　'; o += 2
                if s.startswith('ズz'): st += 4; s = s[2:]                     # 앞 두 워드는 머리 값
                while W(st - 2) == 0 and a > 0x2000: st -= 2                   # 제목 앞 빈칸도 자리
                out.append((st, (o - st) // 2, s))
            else: o += 2
    return out


def fx(t):
    for x, y in FW: t = t.replace(x, y)
    return t.replace('　', '')


def patch(log=print):
    import build as BD
    iso, E = B.disc('K'); d0, L = table(iso, E); R = rows(); d = bytearray(d0)
    need = list('0123456789년월일')                                   # 번호표 글자는 원래 글꼴 칸 안에
    for t in R.values():
        for c in t:
            if c != ' ' and c not in need: need.append(c)
    zones = ZONES
    cap = NF + sum(n for _, n in zones)
    log('글자', len(need), '칸', cap); assert len(need) <= cap
    num = {c: i + 1 for i, c in enumerate(need)}
    # 글꼴: 1~99 제자리, 100~ 빈 구역
    seg = []; k = NF; v = VR
    for i, c in enumerate(need[:NF]): d[FONT + i * 128:FONT + i * 128 + 128] = BD.glyph(c)
    rest = need[NF:]; used = []
    for o, n in zones:
        part, rest = rest[:n], rest[n:]
        if not part: break
        for j, c in enumerate(part): d[o + j * 128:o + j * 128 + 128] = BD.glyph(c)
        used.append((o, v, len(part) * 128)); v += len(part) * 128
    # 번호→칸 표
    old = struct.unpack('>400H', d0[TBL0:TBL0 + 800])
    assert old[:8] == (0x100, 0x100, 0x100, 0x100, 0x101, 0x102, 0x103, 0x104) and old[99 * 4:] == (0x289, 0x28A, 0x28B, 0x28C)
    assert old[:4] == (0x100,) * 4 and all(old[(n - 1) * 4 + 4 + q] == 0x101 + (n - 1) * 4 + q for n in range(1, 100) for q in range(4))  # 규칙적 → 스텁이 만든다
    assert not any(d0[Z1:Z1END]) and not any(d0[ZEND2:Z2END])
    tb = [0x100] * 4 + list(range(0x101, 0x101 + 99 * 4)) + list(range(CELL, CELL + (len(need) - 99) * 4))
    bad = []; seen = set()
    for st, n, s in runs(d0, L):
        if s.startswith(DIG):
            struct.pack_into('>13H', d, st, *[num[c] for c in '0123456789년월일']); st += 26; n -= 13; s = s[13:]
        k = fx(s)
        if len(k) < 2 or k == 'フド': continue
        if k not in R: log('  표에 없음', hex(st), n, s); continue
        e = [num[c] if c != ' ' else 0 for c in R[k]]; seen.add(k)
        if len(e) > n: bad.append((hex(st), n, len(e), R[k])); continue
        pad = (n - len(e)) // 2 if st >= 0x11000 else 0                      # 화면 제목은 가운데
        struct.pack_into('>%dH' % n, d, st, *([0] * pad + e + [0] * (n - len(e) - pad)))
    assert d0[0x1A5A:0x1A62] == struct.pack('>4H', 89, 90, 88, 91)         # 로드 화면 記録日時(runs 범위 밖)
    struct.pack_into('>4H', d, 0x1A5A, *[num[c] for c in R['記録日時']]); seen.add('記録日時')
    log('못 찾은 줄', [k for k in R if k not in seen], '넘침', bad)
    # 스텁: r4,r5 는 호출부 값 그대로
    F = 0x6013208; RAM = 0x200000
    code = [0x4F22]                                                  # sts.l pr,@-r15
    lit = []

    def L32(reg, val):
        lit.append((len(code), reg, val)); code.append(0)
    L32(6, 0x210ADC); code.append(0x6662)                            # r6 = [크기]
    L32(0, F); code += [0x400B, 0x0009]                              # jsr @r0
    for o, vv, n in used:
        L32(4, 0x20200000 + o); L32(5, vv); L32(6, n); L32(0, F); code += [0x400B, 0x0009]
    L32(1, 0x20000000 + RTBL)                                        # 번호→칸 표 만들기
    for start, cnt, step in ((0x100, 4, 0), (0x101, 99 * 4, 1), (CELL, (len(need) - 99) * 4, 1)):
        L32(3, start); L32(2, cnt)
        code += [0x2131, 0x7102] + ([0x7301, 0x4210, 0x8BFA] if step else [0x4210, 0x8BFB])
    code.append(0xE300)                                              # mov #0,r3
    for a_, n_ in ((Z1, Z1END - Z1), (ZEND2, Z2END - ZEND2)):
        L32(1, 0x20200000 + a_); L32(2, n_ // 2)
        code += [0x2131, 0x7102, 0x4210, 0x8BFB]                     # mov.w r3,@r1; add #2,r1; dt r2; bf 앞으로
    code += [0x4F26, 0x000B, 0x0009]                                 # lds.l @r15+,pr; rts; nop
    if len(code) % 2: code.append(0x0009)
    pool = {}; data = []
    base = len(code) * 2
    for pc, reg, val in lit:
        if val not in pool: pool[val] = base + len(data) * 4; data.append(val)
        a = STUB + pc * 2; t = STUB + pool[val]
        disp = (t - ((a & ~3) + 4)) // 4; assert 0 <= disp < 256 and (t - ((a & ~3) + 4)) % 4 == 0
        code[pc] = 0xD000 | reg << 8 | disp
    blob = struct.pack('>%dH' % len(code), *code) + struct.pack('>%dI' % len(data), *data)
    assert STUB % 4 == 0 and len(blob) <= STUBMAX, len(blob)
    d[STUB:STUB + len(blob)] = blob
    log('스텁', len(blob), 'B', '구역', [(hex(a), hex(b), c) for a, b, c in used])
    g = bytearray(iso.read(*E['/GMS1.BIN'][1:3]))
    assert g[0x8E0:0x8EC].hex() == 'd68bd58cd48cd28d420b6662' and struct.unpack_from('>I', g, 0xB10)[0] == 0x210ADC
    struct.pack_into('>I', g, 0xB10, RAM + STUB)                     # r6 = 스텁
    g[0x8E8:0x8EC] = bytes.fromhex('460b0009')                       # jsr @r6; nop
    assert struct.unpack_from('>I', g, 0x13D0)[0] == 0x200000 + TBL0
    struct.pack_into('>I', g, 0x13D0, RTBL)                          # 표 옮김(스텁이 복사)
    patch.stub = len(blob); patch.zones = used; patch.tb = tb
    return {'/GMS2.BIN': bytes(d), '/GMS1.BIN': bytes(g)}, bad


if __name__ == '__main__':
    out, bad = patch()
    print({k: len(v) for k, v in out.items()}, len(bad))
