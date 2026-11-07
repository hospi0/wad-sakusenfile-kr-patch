# -*- coding: utf-8 -*-
"""본편 W_MAP2 연표 패치. 램 기준 0x210000. 글꼴 0x4E128(번호 x = 칸 x-2, 0 = 빈칸, 1 = 줄바꿈).
   줄 흐름 0x4A08C~0x4ABC4, 뒤는 FFFF 문장(포인터).  python tools/wmap_build.py = 검사만."""
import sys, os, re, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_build as B, ded_build as D
sys.stdout.reconfigure(encoding='utf-8')
NL = D.NL; FF = 0xFFFF; BASE = 0x210000; FB = 0x4E128; NF = 428; S0 = 0x4A08C; S1 = 0x4ABC4; W = 13
SRC = open('tools/extract2.py', encoding='utf-8').read()
FX = eval(re.search(r'FX = (\{.*?\})\n', SRC).group(1))


def nz(t):
    t = D.norm(t)
    for a, b in (('へ', 'ヘ'), ('ピ', 'ビ'), ('パ', 'バ'), ('ポ', 'ボ')): t = t.replace(a, b)
    return t


def rows():
    K = {}
    for l in open('work/text/ko_extra.tsv', encoding='utf-8'):
        if l[0] != '#':
            p = l.rstrip('\n').split('\t')
            if len(p) > 1: K[p[0]] = p[-1]
    R = [l.rstrip('\n').split('\t') for l in open('work/text/extra.tsv', encoding='utf-8') if l[0] != '#' and l.split('\t')[1] == 'Y']
    title = {}; sent = {}
    for r in R:
        if NL in r[4]:
            kl = K[r[0]].split(NL); kl[0] = re.sub('^[0-9]+년 +', '', kl[0])
            title[nz(re.sub('^[0-9]+年', '', r[4].split(NL)[0]))] = kl
        else: sent[nz(r[4])] = K[r[0]]; title.setdefault(nz(r[4]), [K[r[0]]])
    return title, sent


def wrap(t, w):
    o = []; c = ''
    for x in t.split(' '):
        if c and len(c) + 1 + len(x) > w: o.append(c); c = ''
        while len(x) > w: o.append(x[:w]); x = x[w:]
        c = c + ' ' + x if c else x
    if c: o.append(c)
    return o


def patch(iso, E, log=print, cfg=None):
    import build as BD
    global FB, S0, S1
    d0 = iso.read(*E['/W_MAP2.BIN'][1:3]); d = bytearray(d0)
    if cfg:                                                  # 작전: 번호는 본편과 같고 위치만 다름. 글자표는 본편에서
        iK, EK = B.disc('K'); dK = iK.read(*EK['/W_MAP2.BIN'][1:3]); GK = D.gm(iK, EK)
        L = [FX.get(i, GK.get(dK[FB + i * 128:FB + i * 128 + 128], '?')) for i in range(NF)]
        FB, S0, S1 = cfg
    else:
        G = D.gm(iso, E)
        L = [FX.get(i, G.get(d0[FB + i * 128:FB + i * 128 + 128], '?')) for i in range(NF)]
    ch = lambda x: L[x - 2] if 2 <= x < NF + 2 else '#'
    title, sent = rows()
    w = struct.unpack('>%dH' % ((S1 - S0) // 2), d0[S0:S1])
    lines = [[]]
    for x in w:
        if x == 1: lines.append([])
        else: lines[-1].append(x)
    # 새 줄 목록(문자 단위)
    out = []; miss = []; cnt = 0
    for l in lines:
        z = 0
        while z < len(l) and l[z] == 0: z += 1
        q = ''.join('　' if x == 0 else ch(x) for x in l[z:])
        if not q: out.append(''); continue
        if z == 0: out.append(q.replace('年', '년')); continue
        if z == 5: continue                                         # 본문은 제목 줄에서 넣음
        k = nz(q)
        if k not in title: miss.append(q); out.append(' ' + q); continue
        kl = title[k]; out.append(' ' + kl[0]); cnt += 1
        for b in kl[1:]:
            out += ['    ' + x for x in wrap(b, W)]
    log(' 줄', len(lines), '새 줄', len(out), '제목 맞음', cnt, '못 찾음', miss, '최대 폭', max(len(x) for x in out))
    # 문장
    idx = D.ptrs(d0, BASE); q = S1 + 2; sl = []; other = []
    new_s = {}
    while q < FB - 2:
        e = q
        while e < FB and struct.unpack_from('>H', d0, e)[0] != FF: e += 2
        n = (e - q) // 2
        if n:
            t = ''.join(ch(x) if x > 1 else ('　' if x == 0 else '') for x in struct.unpack('>%dH' % n, d0[q:e]))
            k = nz(t)
            if k in sent: new_s[q] = sent[k]; sl.append(q)
            elif n > 10 and idx.get(q): other.append((hex(q), t[:40]))
        q = e + 2
    log(' 문장 맞음', len(sl), '표', len(sent), '포인터 있는데 표에 없음', len(other), other[:6], '안 쓴 표', [k[:14] for k in sent if k not in {nz(''.join(ch(x) if x > 1 else '' for x in struct.unpack('>%dH' % ((d0.find(b'\xff\xff', o) - o) // 2), d0[o:d0.find(b'\xff\xff', o)]))) for o in sl}][:6])
    need = []; keep = {}
    for i, c in enumerate(L):
        if re.match('[0-9]', c): keep.setdefault(c, i + 2)
    for t in out + list(new_s.values()):
        for c in t:
            if c != ' ' and c not in keep and c not in need: need.append(c)
    free = [i + 2 for i in range(NF) if i + 2 not in keep.values()]
    log(' 글자', len(need), '빈 칸', len(free)); assert len(need) <= len(free)
    M = dict(zip(need, free)); M.update(keep)
    for c, n in zip(need, free): d[FB + (n - 2) * 128:FB + (n - 1) * 128] = BD.glyph(c)
    enc = lambda t: [0 if c == ' ' else M[c] for c in t]
    st = []
    for i, t in enumerate(out):
        if i: st.append(1)
        st += enc(t)
    st += [1] * max(0, len(lines) - len(out))                        # 줄 수는 원본 이상
    log(' 흐름 워드', len(st), '가능', len(w)); assert len(st) <= len(w)
    d[S0:S1] = bytes(S1 - S0)
    struct.pack_into('>%dH' % len(st), d, S0, *st)
    struct.pack_into('>H', d, S0 + len(st) * 2, FF)
    # 문장 다시 채우기: 포인터 있는 문장만, 묶어서 자리 재활용
    pool = []; plan = []
    for o in sl:
        e = d0.find(b'\xff\xff', o); e -= (e - o) % 2
        while struct.unpack_from('>H', d0, e)[0] != FF: e += 2
        pool.append((o, e, enc(new_s[o])))
    over = []
    free_b = []
    for o, e, v in pool:
        n = (e - o) // 2
        if len(v) <= n:
            struct.pack_into('>%dH' % (len(v) + 1), d, o, *(v + [FF])); d[o + (len(v) + 1) * 2:e + 2] = bytes(e + 2 - (o + (len(v) + 1) * 2))
            if idx.get(o) and n - len(v) >= 8: free_b.append([o + (len(v) + 1) * 2, e + 2])
        else: over.append((o, e, v))
    free_b.append([S0 + (len(st) + 1) * 2, S1])                       # 줄 흐름 뒤 빈자리
    top = FB + (max(M.values()) - 1) * 128                            # 안 쓰는 글꼴 칸 자리(램에 그대로 있음)
    free_b.append([top, FB + NF * 128]); log(' 글꼴 뒤 빈자리', hex(top), FB + NF * 128 - top)
    left = []
    for o, e, v in sorted(over, key=lambda x: -len(x[2])):
        if not idx.get(o): left.append(hex(o)); continue
        sz = (len(v) + 1) * 2; c = [b for b in free_b if b[1] - b[0] >= sz]
        if not c: left.append(hex(o)); continue
        b = min(c, key=lambda x: x[1] - x[0]); struct.pack_into('>%dH' % (len(v) + 1), d, b[0], *(v + [FF]))
        for a in idx[o]: struct.pack_into('>I', d, a, BASE + b[0])
        b[0] += sz; d[o:e + 2] = bytes(e + 2 - o)
    log(' 긴 문장 옮김', len(over), '못 넣음', left)
    if not cfg: assert not left and not miss
    else: log(' 작전 연표 못 넣음', left, '못 찾음', miss)
    return bytes(d)


if __name__ == '__main__':
    iso, E = B.disc('K'); print(len(patch(iso, E)))
