# -*- coding: utf-8 -*-
"""ASC16 메뉴 글꼴 + 문자열 빌더(시험: 디스크에 안 씀, 검사만).  python tools/asc_build.py
   글자 번호 = ASC16MAP 표 번호 = 문자열 값. 가나·한자·□ 칸 전부 한글 자원."""
import sys, os, glob, struct, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, asc_table as T, ko_audit as A
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
BLOCK = {'K': {'/GAME2.BIN': (0x1A036, 0x1A036 + 714 * 2 + 91 * 2)}, 'F': {'/GAME2.BIN': (0x1A546, 0x1A546 + 714 * 2 + 91 * 2)}}   # 줄 차례로 찾는 묶음
KEEP = re.compile(r'[A-Za-z0-9$.\'=/㎜?!%\-:ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ・（），。「≪≫○×＆㎏]')

def disc(tag):
    p = glob.glob(SS.B + (r'\*Koutetsu*' if tag == 'K' else r'\*Sakusen*'))[0]
    iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); return iso, {f[0]: f for f in iso.walk()}

def load():
    k, _, _ = A.load_ko()
    drop = set(open('work/text/drop_ids.txt', encoding='utf-8').read().split())
    pos = collections.defaultdict(list)
    import asc_more as MR
    have = collections.defaultdict(set); spans = collections.defaultdict(list)
    haveF = collections.defaultdict(set); spansF = collections.defaultdict(list)
    for l in open('work/text/ui_pos.tsv', encoding='utf-8'):
        i, tag, fn, o, n = l.rstrip('\n').split('\t')
        if i in drop: continue
        if tag == 'K': have[fn].add(int(o, 16)); spans[fn].append((int(o, 16), int(n)))
        if tag == 'F': haveF[fn].add(int(o, 16)); spansF[fn].append((int(o, 16), int(n)))
        if i not in drop and i in k: pos[(tag, fn)].append((int(o, 16), int(n), i, MR.FIX.get(i, k[i][0][5])))
    for tg_ in 'KF':
        _iso, _E = disc(tg_)
        hv = have if tg_ == 'K' else haveF; sp = spans if tg_ == 'K' else spansF
        more, miss = MR.rows(lambda fn: _iso.read(*_E[fn][1:3]), hv, sp)
        have2 = collections.defaultdict(set); span2 = collections.defaultdict(list)
        for fn_, s_ in sp.items(): span2[fn_] = list(s_)
        for fn_, a_, n_, _t in more: span2[fn_].append((a_, n_))
        auto = MR.auto_rows(lambda fn: _iso.read(*_E[fn][1:3]), [fn_ for fn_ in _E if fn_ in MR.AUTO_FILES], hv, span2, k, drop)
        print(tg_, '번역 있는 줄 자동 추가', len(auto)); more = more + auto
        miss_ = [x for x in miss]
        print(tg_, '못 찾은 추가 줄', miss_)
        for fn, o, n, t in more: pos[(tg_, fn)].append((o, n, 'M%X' % o, t))
    # 큰 유닛 이름(UPK 레코드 9칸, 제자리)
    big = {}
    for l in open('work/text/big.tsv', encoding='utf-8'):
        if l[0] != '#':
            q = l.rstrip('\n').split('\t')
            if len(q) > 5 and q[5]: big[q[0]] = q[5]
    for l in open('work/text/big_pos.tsv', encoding='utf-8'):
        i, tag, fn, o = l.rstrip('\n').split('\t')
        if i in big: pos[(tag, fn)].append((int(o, 16), 9, i, big[i]))
    return pos

def slots():
    S = T.SHEET
    return [i for i, c in enumerate(S) if i > 0 and not KEEP.match(c) and c != '　']

BASE = {'/GAME2.BIN': 0x217000, '/GAMEOVER.BIN': 0x6060000, '/00000000.BIN': 0x6010000}
BLK0 = {'K': 0x1A036, 'F': 0x1A546}          # GAME2 메시지 묶음(줄 차례로 찾음, 첫 줄 포인터만)
FF = 0xFFFF


def table():
    pos = load(); S = T.SHEET
    inv = {}
    for i, c in enumerate(S):
        if KEEP.match(c): inv.setdefault(c, i)
    inv[' '] = 0; inv['　'] = 0; inv['·'] = inv['・']
    need = sorted({c for v in pos.values() for r in v for c in r[3] if c not in inv})
    return pos, inv, need


def patch(tag, log=print):
    """디스크 tag 의 ASC16 글꼴·문자열 패치. 돌려주는 값 {파일: 새 바이트}, 못 넣은 줄 목록."""
    import build as BD
    pos, inv, need = table()
    iso, E = disc(tag); r = lambda n: iso.read(*E[n][1:3])
    mp = r('/VIEWCG/ASC16MAP.BIN'); w = struct.unpack('>%dH' % (len(mp) // 2), mp)
    a, b = r('/VIEWCG/ASC16X16.BIN'), r('/VIEWCG/ASC16_2.BIN'); cg = bytearray(a + b)
    c4 = collections.Counter(w)
    # 번호 544 이상은 번호→칸 대응이 어긋나고(시트+2) 작전파일 시트도 달라, 두 디스크가 같은 아래쪽 칸만 쓴다
    free = [i for i in slots() if i < 540 and all(c4[x] == 1 for x in w[i * 4:i * 4 + 4])]
    assert len(need) <= len(free), (len(need), len(free))
    M = dict(zip(need, free))
    for c, i in M.items():
        g = BD.glyph(c)
        for q in range(4):
            o = (w[i * 4 + q] - 0x800) * 32; cg[o:o + 32] = g[q * 32:q * 32 + 32]
    enc = lambda t: [M[c] if c in M else inv[c] for c in t]
    out = {'/VIEWCG/ASC16X16.BIN': bytes(cg[:len(a)]), '/VIEWCG/ASC16_2.BIN': bytes(cg[len(a):])}
    left = []
    for (tg, fn), v in pos.items():
        if tg != tag: continue
        d = bytearray(r(fn)); v = sorted(set(v)); base = BASE.get(fn)
        put = lambda o, e: struct.pack_into('>%dH' % len(e), d, o, *e)
        idx = collections.defaultdict(list)
        if base is not None:
            for i in range(0, len(d) - 3, 2):
                x = struct.unpack_from('>I', d, i)[0] - base
                if 0 <= x < len(d): idx[x].append(i)
        src = bytes(d); W = lambda o: struct.unpack_from('>H', src, o)[0]
        byo = {o: (n, i, t) for o, n, i, t in v}

        def line_end(o):
            """줄 끝 FFFF 위치. 문자열처럼 안 보이면 None."""
            q = o
            while q < len(src) - 1 and q - o < 80:
                x = W(q)
                if x == FF: return q
                if x >= 1200: return None
                q += 2
            return None

        def region(o):
            """o 줄을 포함해 FFFF 로 이어진 줄들(앞뒤로 번역 줄이나 포인터 있는 줄까지)."""
            L = [o]
            while True:                                     # 뒤로
                e = line_end(L[-1])
                if e is None: break
                nx = e + 2
                if nx not in byo and not idx.get(nx): break
                if line_end(nx) is None: break
                L.append(nx)
            while True:                                     # 앞으로
                pv = [a for a, (n, _, _) in byo.items() if a + (n + 1) * 2 == L[0]]
                if not pv: break
                L.insert(0, pv[0])
            return L

        def reflow(L):
            """줄 묶음 다시 채우기. 포인터 없는 줄은 시작 위치 고정, 포인터 있는 줄은 빈 구간에 큰 것부터 채운다."""
            s0 = L[0]; e0 = line_end(L[-1]) + 2
            word = lambda o: enc(byo[o][2]) if o in byo else list(struct.unpack('>%dH' % ((line_end(o) - o) // 2), src[o:line_end(o)]))
            fix = [o for o in L if not idx.get(o)]; mov = [o for o in L if idx.get(o)]
            bins = []; cur = s0
            for o in fix:
                if o < cur: return None
                if o > cur: bins.append([cur, o])
                cur = o + (len(word(o)) + 1) * 2
            if cur > e0: return None
            if cur < e0: bins.append([cur, e0])
            plan = [(o, o, word(o)) for o in fix]
            for o in sorted(mov, key=lambda x: -len(word(x))):
                e = word(o); sz = (len(e) + 1) * 2
                c = [b for b in bins if b[1] - b[0] >= sz]
                if not c: return None
                b = min(c, key=lambda x: x[1] - x[0]); plan.append((o, b[0], e)); b[0] += sz
            d[s0:e0] = bytes(e0 - s0)
            for o, q, e in plan:
                put(q, e + [FF])
                if q != o:
                    for a in idx[o]: struct.pack_into('>I', d, a, q + base)
            return len(plan), len(fix), sum(b[1] - b[0] for b in bins) // 2

        over = [x for x in v if len(enc(x[3])) > x[1]]
        done = set()
        if fn == '/GAME2.BIN':
            o = BLK0[tag]; L = [];
            for _ in range(91):
                L.append(o); o = struct.unpack_from('>H', src, o) and line_end(o) + 2
            res = reflow(L); log(' 묶음', hex(L[0]), res)
            if res: done |= set(L)
            else: left.append((fn, hex(L[0]), '묶음 못 넣음'))
        for o, n, i, t in over:
            if o in done: continue
            L = region(o); res = reflow(L) if (base is not None and len(L) > 1) else None
            if res: done |= set(L); log('  다시 채움', fn, i, hex(L[0]), res)
            else: left.append((fn, hex(o), i, n, len(enc(t)), t, len(L)))
        for o, n, i, t in v:
            if o in done: continue
            e = enc(t)
            lead = 0
            while lead < n and W(o + lead * 2) == 0: lead += 1
            if len(e) + lead <= n: e = [0] * lead + e                # 원문 앞 빈칸(들여쓰기·겹침 자리) 유지
            if len(e) <= n: put(o, e + [0] * (n - len(e)))
        out[fn] = bytes(d)
    return out, left, M


def main():
    for tag in 'KF':
        out, left, M = patch(tag)
        print(tag, '바뀐 파일', {k: len(v) for k, v in out.items()}, '글자', len(M))
        for x in left: print('  남음', x)


if __name__ == '__main__':
    main()
