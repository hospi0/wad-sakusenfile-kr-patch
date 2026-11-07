# -*- coding: utf-8 -*-
"""작전파일 전용 글꼴 4벌(TURNASC·GMSFONT·KASOU·GAMEOVER) 패치.  python tools/ded_f.py = 검사만
   f_text.py 가 남긴 work/text/f_L.json(칸별 글자·번호 어긋남) + f_raw.tsv 문자열.
   숫자·라틴·기호 칸은 유지(코드가 번호로 찍음), 年月日 칸은 년월일 그림으로. 넘치는 줄은 포인터로 다시 채움."""
import sys, os, re, json, struct, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as BD, ded_build as D, sf_ded as SD
sys.stdout.reconfigure(encoding='utf-8')
NL = BD.N; FF, FE = 0xFFFF, 0xFFFE
#          이름, 글꼴 파일, 글꼴 위치, 칸 수, 문자열 파일, 줄 폭
BLK = [('/TURNASC.BIN', '/TURNASC.BIN', 0, 206, '/GAME2.BIN', 19), ('/GMSFONT.BIN', '/GMSFONT.BIN', 0, 371, '/GMS1.BIN', 19),
       ('/KASOU', '/KASOU.BIN', 0x12CFC, 452, '/KASOU.BIN', 19), ('/GAMEOVER', '/GAMEOVER.BIN', 0, 0, '/GAMEOVER.BIN', 17)]
SWAP = {'年': '년', '月': '월', '日': '일'}
KEEPC = re.compile('[0-9A-Za-z!?.,:;\'/%#=+\\-]')
SKIP = {'年月日'}                                          # 코드가 찍는 번호표: 칸 그림만 바꾼다
NL_ = chr(92) + 'l'
# 시나리오 설명 창 = 줄 19칸(실기 2026-11-07) — 자리별 지정
BY_OFF = {0x49E60: '2차 대전기 독소전을 재현한' + NL_ + '캠페인 게임입니다.',
          0x49EA8: '가상 세계 바라드 대륙의 동란을' + NL_ + '다룬 캠페인입니다.',
          0x4A078: '신병기의 독일군과 소련군의' + NL_ + '사상 최대 전차전입니다.',
          0x4A0C8: '대륙 상륙 후 파죽지세로 진격하는' + NL_ + '연합군과 약화된 독일군의 전투입니다',
          0x4A2F8: '패색 짙은 독일이 마지막 대규모' + NL_ + '반격을 시도한 대전차전 MAP입니다',
          0x4A7F8: '대전략의 원점이라 해도 좋을 맵.' + NL_ + '아는 분은 꽤나 통달한 분이겠네요.',
          0x4A848: '뉴칼레도니아 섬의 수비군이 되어' + NL_ + '적에게서 아름다운 자연을 지켜라!',
          0x4A9D8: '세토나이카이를 무대로 한 맵.' + NL_ + '바다를 사이에 둔 전투를 체험합니다'}
BASES = {'/TURNASC.BIN': 0x217000, '/GMSFONT.BIN': 0x6060000, '/KASOU': 0x6060000, '/GAMEOVER': 0x6060000}
# 칸 고정(포인터 없음) 줄·턴 문장은 칸 안으로 줄인 표현(작전 디스크 전용)
SHORT = {
    '전쟁의 주도권은 미국으로 넘어갔다.\\l일본이 어떻게 지킬 것인가 하는 맵입니다.': '주도권은 미국으로 넘어갔다.\\l일본의 방어전을 다룬 맵입니다.',
    '1941년 곡창지대 우크라이나의 수도\\l키예프를 둘러싼 독일과 소련의 전투입니다.': '1941년 곡창 우크라이나의 수도\\l키예프를 둘러싼 독소 전투입니다.',
    '동서에서 압도적 전력의 연합군이 몰려오는\\l독일 제3제국 최후의 맵입니다.': '동서에서 압도적 연합군이 몰려온다.\\l독일 제3제국 최후의 맵입니다.',
    '파죽지세로 진격한 독일군은 드디어 모스\\l크바로… 동장군은 때맞춰 올 것인가.': '파죽지세의 독일군은 모스크바로…\\l동장군은 때맞춰 올 것인가.',
    '독일의 소련 침공작전 「바르바로사」에서\\l모스크바로 가는 발판이 된 MAP입니다.': '바르바로사 작전에서 모스크바로\\l가는 발판이 된 MAP입니다.',
    '패색이 짙어진 독일이 마지막 대규모\\l반격을 시도한 대전차전 MAP입니다.': '패색 짙은 독일이 마지막 대규모\\l반격을 시도한 대전차전 MAP입니다.',
    '공세 한계에 달한 소련군의 추격을 격파하고\\l하리코프 시를 탈환하는 MAP입니다.': '공세 한계의 소련군 추격을 격파하고\\l하리코프를 탈환하는 MAP입니다.',
    '태평양을 완전 제압한 일본의 미국 본토\\l상륙작전이라는 가상전 MAP입니다.': '태평양을 제압한 일본의 미국 본토\\l상륙작전이라는 가상전 MAP입니다.',
    '겨울 전쟁이 주제입니다. 양의 소련군·질의\\l핀란드군. 양자의 차이를 재현.': '겨울 전쟁이 주제. 양의 소련군·\\l질의 핀란드군, 그 차이를 재현.',
    '독일 지배하의 네덜란드령 아른험 시에서\\l벌어진 연합군의 대공수 작전입니다.': '독일 지배하의 네덜란드 아른험에서\\l벌어진 연합군 대공수 작전입니다.',
    '보병은 산 넘고 숲 넘어 공격해 간다.\\l군대의 기본, 보병전을 다룬 맵입니다.': '보병은 산 넘고 숲 넘어 공격한다.\\l군대의 기본, 보병전 맵입니다.',
    '태평양 전쟁의 터닝 포인트가 된\\l전투입니다. 항공모함전을 벌이는 맵입니다.': '태평양 전쟁의 전환점이 된\\l전투입니다. 항공모함전 맵입니다.',
    '세토나이카이를 무대로 전투를 벌이는 맵.\\l바다를 사이에 둔 전투를 체험할 수 있습니다.': '세토나이카이를 무대로 한 맵.\\l바다를 사이에 둔 전투를 체험합니다.',
    '천국에서 가장 가까운 섬': '천국에 가까운 섬', '기록 일시': '기록일시',
    '북서쪽의 50군이 포위망을 돌파해\\l  원군으로 남하 중이라는 연락이 있음.': '북서쪽의 50군이 포위망을 돌파해\\l 원군이 남하 중이라는 연락.',
    '적장 만슈타인의 군이 남방에서\\l접근 중!\\l전면의 적을 조기 격파해 이에 대비하라.': '적장 만슈타인의 군이 남방에서\\l접근 중!\\l전면의 적을 조기 격파하라.',
    '프리피야트 강 남방에서\\l 양동 부대가 진격을 개시했습니다.': '프리피야트 강 남방에서\\l 양동 부대가 진격 개시.',
}


def best_base(src, offs):
    S = set(offs); vote = collections.Counter()
    for i in range(0, len(src) - 3, 2):
        x = struct.unpack_from('>I', src, i)[0]
        if not 0x200000 <= x < 0x6200000: continue
        for o in offs[:60]:
            b = x - o
            if b >= 0 and b % 0x1000 == 0: vote[b] += 1
    return vote.most_common(3)


def patch(iso, ent, extra, log=print):
    J = SD.table(); Lmap = json.load(open('work/text/f_L.json', encoding='utf-8'))
    raw = collections.defaultdict(list)
    for l in open('work/text/f_raw.tsv', encoding='utf-8'):
        nm, o, t = l.rstrip('\n').split('\t'); raw[nm].append((int(o, 16), t))
    rd = lambda n: extra.get(n) or iso.read(*ent[n][1:3])
    out = {}; report = []
    for nm, ff, fb, n, sf, W in BLK:
        info = Lmap[nm]; L = info['L']; sh = info.get('sh', 0); fb = info.get('base', fb); n = len(L) - 160 if sh else info.get('n', len(L))
        src = bytes(rd(sf)) if sf not in out else out[sf]; d = bytearray(src); fd = bytearray(out.get(ff) or rd(ff))
        rows = []
        for o, t in raw[nm]:
            k = SD.nz(t)
            if k in SKIP or k not in J: continue
            v_ = SHORT.get(J[k], J[k])
            if nm == '/GMSFONT.BIN' and o in BY_OFF: v_ = BY_OFF[o]
            if nm == '/TURNASC.BIN': v_ = v_.replace(NL + '  ', NL + ' ').replace(NL + ' ', NL)   # 들여쓰기 칸을 낱말 줄 자리로
            rows.append((o, t, v_))
        nat = []
        if nm == '/TURNASC.BIN':
            ix = {}
            for i_, c_ in enumerate(info['cells']): ix.setdefault(c_, i_)
            have_ = {r[0] for r in rows}
            for w in ('天候', '晴', '曇り', '雨', '雪', '通常', '雨1', '雨2', '雪1', '雪2', '累積度', '現在', '終了'):
                if not all(c in ix for c in w) or SD.nz(w) not in J: continue
                b_ = struct.pack('>%dH' % len(w), *[ix[c] for c in w]) + bytes([255, 255]); q_ = src.find(b_, 0x61000)
                if q_ >= 0 and q_ not in have_: rows.append((q_, w, J[SD.nz(w)])); have_.add(q_)
            import nation_f, ko_audit as A
            kk, _, _ = A.load_ko(); NJ = {}
            for l in open('work/text/ui.tsv', encoding='utf-8'):
                if l[0] != '#':
                    z = l.split('\t')
                    if z[0] in kk: NJ.setdefault(z[4].replace('　', ''), kk[z[0]][0][5])
            NJ.update(D.NATION); NJ.update(nation_f.NATION_F)
            q_ = 0x6189B
            while src[q_ + 12] == 0xFF:
                t_ = ''.join(info['cells'][x] for x in src[q_:q_ + 12] if x)
                if t_:
                    assert t_ in NJ, t_
                    assert len(NJ[t_]) <= 12, NJ[t_]
                    nat.append((q_, NJ[t_]))
                q_ += 13
        rows.sort()
        # 칸 정리
        LL = info['cells']                                  # 칸 번호 순 글자
        keep = {}
        for i, c in enumerate(LL):
            if i - sh > 1 and KEEPC.match(c): keep.setdefault(c, i - sh)        # 번호 = 칸 - sh
        for i, c in enumerate(LL):
            if c in SWAP:
                fd[fb + i * 128:fb + i * 128 + 128] = BD.glyph(SWAP[c]); keep[SWAP[c]] = i - sh
        need = []
        brk = None
        if nm == '/KASOU':                                  # 문장 줄바꿈 = 글꼴의 ？ 칸, 줄 폭 = 원문 최대
            brk = 1
            W = max(len(x) for o, t, v in rows for x in re.split('[？?/]', t))
        blank = 0
        for o, t, v in rows:
            for c in v.replace(NL, ''):
                if c != ' ' and c != '　' and c not in keep and c not in need: need.append(c)
        for q_, v in nat:
            for c in v:
                if c != ' ' and c not in keep and c not in need: need.append(c)
        free = [i for i, c in enumerate(LL) if i - sh > 1 and i - sh not in keep.values()]
        assert len(need) <= len(free), (nm, len(need), len(free))
        M = dict(keep)
        for c, i in zip(need, free):
            fd[fb + i * 128:fb + i * 128 + 128] = BD.glyph(c); M[c] = i - sh
        sep = brk if brk else FE

        def enc(v):
            o_ = []
            for q, part in enumerate(D.wrap(v, W).split(NL)):
                if q: o_.append(sep)
                o_ += [blank if c in ' 　' else M[c] for c in part]
            return o_
        base = BASES[nm]; idx = D.ptrs(src, base)
        top = fb + (max(i + sh for i in M.values()) + 1) * 128; end_ = fb + len(LL) * 128   # 안 쓰는 글꼴 칸 자리(파일과 함께 램에 있음)
        same_file = ff == sf
        new = {}; over = []
        for o, t, v in rows:
            q = o
            while struct.unpack_from('>H', src, q)[0] != FF: q += 2
            slot = (q - o) // 2
            if nm == '/GMSFONT.BIN' and slot >= 30:
                w_ = (slot - 1) // 2; ls = D.wrap(v, w_).split(NL)
                assert len(ls) == 2 and max(map(len, ls)) <= w_, (hex(o), v)
                e = [blank if c in ' 　' else M[c] for c in ls[0]] + [blank] * (w_ - len(ls[0])) + [sep] + [blank if c in ' 　' else M[c] for c in ls[1]]
            else: e = enc(v)
            new[o] = e
            if len(e) <= slot: struct.pack_into('>%dH' % slot, d, o, *(e + [blank] * (slot - len(e))))
            else: over.append((o, slot, len(e), bool(idx.get(o)), v))
        for q_, v in nat:
            e = [0 if c == ' ' else M[c] for c in v]; pad = (12 - len(e)) // 2
            d[q_:q_ + 12] = bytes([0] * pad + e + [0] * (12 - len(e) - pad))
        if nm == '/TURNASC.BIN' and over:                    # 맑음 등: 낱말 줄 묶음을 포인터로 다시 채움(FT 문장 여유 사용)
            q0 = src.find(struct.pack('>H', LL.index('晴')) + bytes([255, 255]), 0x61000)
            Ls, e0 = D.walk(src, q0, 0x6179C)
            D.reflow(d, src, Ls, e0, new, idx, base, log); over = []
        # 넘치는 줄: 포인터가 있으면 안 쓰는 글꼴 칸 자리로 옮김
        left = []; moved = 0; cur = top
        for o, slot, ln, hp, v in over:
            sz = (ln + 1) * 2
            if hp and same_file and cur + sz <= end_:
                e = new[o]; struct.pack_into('>%dH' % (ln + 1), fd if ff == sf else d, cur, *(e + [FF]))
                for a_ in idx[o]: struct.pack_into('>I', d, a_, cur + base)
                q = o
                while struct.unpack_from('>H', src, q)[0] != FF: q += 2
                d[o:q] = struct.pack('>H', blank) * ((q - o) // 2)
                cur += sz; moved += 1
            else: left.append((hex(o), slot, ln, hp, v[:30]))
        if same_file:                                        # 글꼴과 문자열이 한 파일: fd 를 d 에 합침
            d[fb:end_] = fd[fb:end_]
        report.append((nm, '줄', len(rows), '글자', len(need), '칸', len(free), '넘침', len(over), '옮김', moved, '못 넣음', len(left), left[:24]))
        log(*report[-1])
        out[sf] = bytes(d)
        if ff != sf: out[ff] = bytes(fd)
    return out


def patch_end(iso, ent, log=print):
    """ENDING.BIN 줄(글꼴 ENDFONT0/1, 번호 = 칸). 번역 E_SF_0/1 차례대로, 빈 줄 유지."""
    d0 = iso.read(*ent['/ENDING.BIN'][1:3]); d = bytearray(d0); base = 0x6060000; idx = D.ptrs(d0, base)
    ko = collections.defaultdict(list)
    for l in open('work/text/ko_final.tsv', encoding='utf-8'):
        if l[0] != '#':
            i, g, v = l.rstrip('\n').split('\t', 2)
            if g.startswith('E_SF_'): ko[g[-1]].append(v)
    Ls, e0 = D.walk(d0, 0x451C, 0x48AC - 2)
    words = {o: struct.unpack('>%dH' % ((d0.find(bytes([255, 255]), o) - o) // 2), d0[o:d0.find(bytes([255, 255]), o)]) for o in Ls}
    text = [o for o in Ls if any(words[o])]
    assert len(text) == 21 and len(ko['0']) == 10 and len(ko['1']) == 11, (len(text), len(ko['0']), len(ko['1']))
    out = {}; new = {}
    for fi, (g, tl, fn) in enumerate((('0', text[:10], '/ENDFONT0.BIN'), ('1', text[10:], '/ENDFONT1.BIN'))):
        f = bytearray(iso.read(*ent[fn][1:3])); M = {}
        kept = {}
        for o, v in zip(tl, ko[g]):
            for c in v:
                if c != ' ' and c not in M:
                    M[c] = len(M) + 1
        assert len(M) < len(f) // 128, (fn, len(M), len(f) // 128)
        for c, n in M.items(): f[n * 128:n * 128 + 128] = BD.glyph(c)
        for o, v in zip(tl, ko[g]):
            assert len(v) <= 17, v
            new[o] = [0 if c == ' ' else M[c] for c in v]
        out[fn] = bytes(f)
    D.reflow(d, d0, Ls, e0 + 2 if False else e0, new, idx, base, log)
    out['/ENDING.BIN'] = bytes(d)
    return out


if __name__ == '__main__':
    import asc_build as B
    iso, E = B.disc('F'); o = patch(iso, E, {})
    print({k: len(v) for k, v in o.items()})
