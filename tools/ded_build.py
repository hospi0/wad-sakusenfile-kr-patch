# -*- coding: utf-8 -*-
"""전용 글꼴 쌍(본편 TURNASC+GAME2, RMC2) 패치.  python tools/ded_build.py = 검사만."""
import sys, os, re, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B, asc_table
sys.stdout.reconfigure(encoding='utf-8')
NL = chr(92) + 'l'; FF, FE = 0xFFFF, 0xFFFE
SRC = open('tools/extract2.py', encoding='utf-8').read()
FIXT = eval(re.search(r"font\(T, 0, 188, (\{.*?\})\)", SRC).group(1))
FIXW = eval(re.search(r"^FIXW = (\(.*\))$", SRC, re.M).group(1))


NATION = {'アメリカ太平洋艦隊': '미국 태평양함대', 'イギリス中央軍': '영국 중앙군', '中央正面軍': '중앙 정면군', '満州軍': '만주군', 'AUS第8師団': 'AUS 8사단',
          'コヒマ守備隊': '코히마 수비대', '第6SS装甲軍': '6SS 기갑군', '中央軍集団': '중앙 군집단'}
NATION.update({'第%d軍' % n: '%d군' % n for n in range(1, 100)})


def gm(iso, E):
    r = lambda n: iso.read(*E[n][1:3])
    mp = r('/VIEWCG/ASC16MAP.BIN'); cg = r('/VIEWCG/ASC16X16.BIN') + r('/VIEWCG/ASC16_2.BIN')
    w = struct.unpack('>%dH' % (len(mp) // 2), mp); G = {}
    for i in range(len(w) // 4):
        g = b''.join(cg[(t - 0x800) * 32:(t - 0x800) * 32 + 32] for t in w[i * 4:i * 4 + 4]); G.setdefault(g, asc_table.SHEET[i])
    return G


def rows(groups):
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
                if p[1] in groups and K.get(p[0]): R[norm(p[4])] = K[p[0]]
    return R


def norm(t):
    for x, y in FIXW: t = t.replace(x, y)
    t = t.replace('ピャ', 'ビャ')
    return t.replace('　', '').replace('?', '').replace(NL, '/')


def ptrs(d, base):
    idx = collections.defaultdict(list)
    for i in range(0, len(d) - 3, 2):
        x = struct.unpack_from('>I', d, i)[0] - base
        if 0 <= x < len(d): idx[x].append(i)
    return idx


def walk(d, a, b):
    """FFFF 로 끝나는 줄 시작 목록."""
    L = []; o = a
    while o < b:
        L.append(o)
        while struct.unpack_from('>H', d, o)[0] != FF: o += 2
        o += 2
    return L, o


def reflow(d, src, L, e0, new, idx, base, log):
    """new[o] = 새 워드(없으면 원본). 포인터 없는 줄은 제자리."""
    def word(o):
        if o in new: return new[o]
        q = o
        while struct.unpack_from('>H', src, q)[0] != FF: q += 2
        return list(struct.unpack('>%dH' % ((q - o) // 2), src[o:q]))
    s0 = L[0]; fix = [o for o in L if not idx.get(o)]; mov = [o for o in L if idx.get(o)]
    bins = []; cur = s0
    for o in fix:
        assert o >= cur, ('고정 줄 겹침', hex(o), hex(cur))
        if o > cur: bins.append([cur, o])
        cur = o + (len(word(o)) + 1) * 2
    assert cur <= e0
    if cur < e0: bins.append([cur, e0])
    plan = [(o, o, word(o)) for o in fix]; same = {}
    for o in sorted(mov, key=lambda x: -len(word(x))):
        e = word(o); sz = (len(e) + 1) * 2; k = tuple(e)
        if k in same: plan.append((o, same[k], e)); continue          # 같은 문장은 한 벌만
        c = [b for b in bins if b[1] - b[0] >= sz]
        assert c, ('자리 없음', hex(o), sz, [b[1] - b[0] for b in bins])
        b = min(c, key=lambda x: x[1] - x[0]); plan.append((o, b[0], e)); same[k] = b[0]; b[0] += sz
    d[s0:e0] = bytes(e0 - s0)
    for o, q, e in plan:
        struct.pack_into('>%dH' % (len(e) + 1), d, q, *(e + [FF]))
    for o, q, e in plan:
        if q != o:
            for a in idx[o]: struct.pack_into('>I', d, a, q + base)
    log(' 다시 채움', hex(s0), len(plan), '고정', len(fix), '남은 워드', sum(b[1] - b[0] for b in bins) // 2)


def wrap(t, W):
    """문단을 낱말 단위로 W 칸에 다시 채움(원문 줄바꿈은 W 안이면 유지, 넘치면 이어 붙여 다시)."""
    if all(len(x) <= W for x in t.split(NL)): return t
    out = []; cur = ''
    for w in t.replace(NL, ' ').split(' '):
        if cur and len(cur) + 1 + len(w) > W: out.append(cur); cur = w
        else: cur = cur + ' ' + w if cur else w
    out.append(cur)
    return NL.join(out)


def patch_turn(iso, E, game2, log=print):
    import build as BD
    r = lambda n: iso.read(*E[n][1:3])
    G = gm(iso, E); T = bytearray(r('/TURNASC.BIN')); N = len(T) // 128
    L = [FIXT.get(i, G.get(bytes(T[i * 128:i * 128 + 128]), '?')) for i in range(N)]
    R = rows({'T'}); src = bytes(game2); d = bytearray(game2); idx = ptrs(src, 0x217000)
    linesA = [0x5D8A0, 0x5D8A6, 0x5D8AE, 0x5D8B4]; eA = 0x5D8BA      # 0x5D8BA~0x5D8DC 는 포인터 표
    linesB, e0 = walk(src, 0x5D8DC, 0x5DC26 + 2)
    lines = linesA + linesB
    keep = {}                                                # 그대로 둘 글자(숫자·라틴)
    for i, c in enumerate(L):
        if i and re.match('[0-9A-Za-z!]', c): keep.setdefault(c, i)
    SWAP = {'年': '년', '月': '월', '日': '일'}
    for i, c in enumerate(L):
        if c in SWAP: T[i * 128:i * 128 + 128] = BD.glyph(SWAP[c]); keep[SWAP[c]] = i
    txt = {}
    for o in lines:
        q = o; s = ''; bad = False
        while True:
            x = struct.unpack_from('>H', src, q)[0]; q += 2
            if x == FF: break
            if x == FE: s += '/'
            elif x < N: s += L[x]
            else: bad = True
        k = norm(s)
        if not bad and k in R: txt[o] = wrap(R[k], 19)
        elif not bad and len(k) > 1: log('  표에 없는 줄', hex(o), s[:30])
    used = set(R) - {norm_s for norm_s in []}
    log(' 줄', len(lines), '번역 찾음', len(txt), '표', len(R))
    # 나라·부대 이름: u8, 10칸 + FF, 가운데 맞춤
    import ko_audit as A
    kk, _, _ = A.load_ko(); J = {}
    for l in open('work/text/ui.tsv', encoding='utf-8'):
        if l[0] != '#':
            q = l.split('\t')
            if q[0] in kk: J.setdefault(q[4].replace('　', ''), kk[q[0]][0][5])
    J.update(NATION)
    names = {}; o = 0x5DCD0; miss = []
    while src[o + 10] == 0xFF:
        t = ''.join(L[x] for x in src[o:o + 10] if x).replace('ピ', 'ビ')
        if t in J: names[o] = J[t]
        else: miss.append((hex(o), t))
        o += 11
    log(' 나라·부대 이름', len(names), '못 찾음', miss, '끝', hex(o))
    assert not miss
    need = []
    for t in names.values():
        for c in t:
            if c != ' ' and c not in keep and c not in need: need.append(c)
    for t in txt.values():
        for c in t.replace(NL, ''):
            if c != ' ' and c not in keep and c not in need: need.append(c)
    free = [i for i, c in enumerate(L) if i > 1 and i not in keep.values()]
    assert len(need) <= len(free), (len(need), len(free))
    M = dict(zip(need, free)); M.update(keep)
    for c, i in zip(need, free): T[i * 128:i * 128 + 128] = BD.glyph(c)
    def enc(t):
        o = []
        for l, part in enumerate(t.split(NL)):
            if l: o.append(FE)
            o += [0 if c == ' ' else M[c] for c in part]
        return o
    new = {o: enc(t) for o, t in txt.items()}
    for o, t in names.items():
        e = enc(t); assert len(e) <= 10, t
        pad = (10 - len(e)) // 2; d[o:o + 10] = bytes([0] * pad + e + [0] * (10 - len(e) - pad))
    w = max(len(p) for t in txt.values() for p in t.split(NL)); log(' 최대 줄 폭', w, '원문 최대 18')
    log(' 최대 줄 수', max(t.count(NL) + 1 for t in txt.values()))
    reflow(d, src, linesA, eA, new, idx, 0x217000, log)
    reflow(d, src, linesB, e0, new, idx, 0x217000, log)
    return bytes(d), bytes(T), None, txt


def patch_rmc(iso, E, log=print):
    """글꼴·문자열 RMC2(램 0x200000), 줄 포인터 표는 RMC1 0x279E0~."""
    import build as BD
    d0 = iso.read(*E['/RMC2.BIN'][1:3]); r1 = bytearray(iso.read(*E['/RMC1.BIN'][1:3])); NF = 88; FB = 0x44; BASE = 0x200000
    ids = ['01680', '01681', '01682', '01683', '01684', '01685', '02238', '02239']
    K = {}
    for l in open('work/text/ko_extra.tsv', encoding='utf-8'):
        if l[0] != '#':
            q = l.rstrip('\n').split('\t')
            if len(q) > 1: K[q[0]] = q[-1]
    lines, e0 = walk(d0, 0x2C48, 0x31D0 - 2); assert e0 == 0x31D0 and len(lines) == 8, (hex(e0), len(lines))
    ptr = {}
    for i in range(0, len(r1) - 3, 2):
        x = struct.unpack_from('>I', r1, i)[0] - BASE
        if x in lines: ptr.setdefault(x, []).append(i)
    assert len(ptr) == 8, ptr
    txt = {o: wrapp(K[i], 20) for o, i in zip(lines, ids)}
    need = []
    for t in txt.values():
        for ch in t.replace(NL, ''):
            if ch != ' ' and ch not in need: need.append(ch)
    assert len(need) <= NF, len(need)
    d = bytearray(d0); M = {ch: i + 1 for i, ch in enumerate(need)}
    for ch, i in M.items(): d[FB + (i - 1) * 128:FB + i * 128] = BD.glyph(ch)
    def enc(t):
        o = []
        for l, part in enumerate(t.split(NL)):
            if l: o.append(FE)
            o += [0 if ch == ' ' else M[ch] for ch in part]
        return o
    cur = 0x2C48; d[0x2C48:e0] = bytes(e0 - 0x2C48)
    for o in lines:
        e = enc(txt[o]) + [FF]; struct.pack_into('>%dH' % len(e), d, cur, *e)
        for a in ptr[o]: struct.pack_into('>I', r1, a, BASE + cur)
        cur += len(e) * 2
    assert cur <= e0, (hex(cur), hex(e0))
    log(' RMC 글자', len(need), '줄', len(txt), '최대 폭', max(len(p) for t in txt.values() for p in t.split(NL)), '최대 줄 수', max(t.count(NL) + 1 for t in txt.values()), '남은 워드', (e0 - cur) // 2)
    return bytes(d), bytes(r1)


def wrapp(t, W):
    """문장 단위로 줄을 끊고 낱말 단위로 W 칸에 채움."""
    out = []
    for sent in re.split(r'(?<=[.?!])\s*(?:' + re.escape(NL) + r')?\s*(?=\S)', t.replace(NL, ' ')):
        cur = ''
        for w in sent.split(' '):
            if cur and len(cur) + 1 + len(w) > W: out.append(cur); cur = w
            else: cur = cur + ' ' + w if cur else w
        out.append(cur)
    return NL.join(out)


if __name__ == '__main__':
    iso, E = B.disc('K')
    g, t, _, txt = patch_turn(iso, E, iso.read(*E['/GAME2.BIN'][1:3]))
    print(len(g), len(t)); print(list(txt.values())[:4])
    a, b = patch_rmc(iso, E); print(len(a), len(b))
