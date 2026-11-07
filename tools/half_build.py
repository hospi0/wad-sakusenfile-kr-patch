# -*- coding: utf-8 -*-
"""반각(8×8) 글꼴·문자열 빌더.  python tools/half_build.py [K|F]  = 검사(디스크 안 씀)
   공통(무기·지형·UI 낱말) = 한글, 고유 이름(유닛·세력·거점·작전) = 영문(romaji·romaji2).
   글꼴 칸 = 가나 82칸 + 안 쓰는 기호 7칸 + 빈 칸 0x1B. 값 = 시트 번호+1, 01 = 빈칸."""
import sys, os, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.append(r'C:\claude\project\gdm-kr-patch\tools')
import asc_build as B, unit_names as UN, ko_audit as A, half_scan as HS
import han8gdm

INK = 0xA                              # ASC8X8 글자 색(원본 실측)
FREE = list(range(0x4D, 0x9F)) + [0x42, 0x48, 0x49, 0x4A, 0x1B]   # 시트 번호: 가나 + ・ ? ! % + 빈 칸. ⛔0x3F=9·0x40=#·0x44==·0x4C=: 는 HUD 가 쓴다
TRIM = {'모래사장': '모래밭', '삼림': '산림', '진흙탕': '진창', '사운드 테스트': 'SoundTest', '오디오': 'Audio', 'BGM 선택': 'BGM SEL'}   # 칸 수 맞춤
EXTRA = {'ターン': '턴', 'リクジョウ': '육상', 'コウクウ': '항공', 'カイジョウ': '해상',
         'ダイトシ': '대도시', 'チュウトシ': '중도시', 'ショウトシ': '소도시', 'ダイコウザン': '대광산', 'チュウコウザン': '중광산', 'ショウコウザン': '소광산', 'ホウカイコウザン': '붕괴 광산',
         'ミチ': '도로', 'ダミー': 'Dummy', 'クウコウダミー': 'Dummy', 'ミナトダミー': 'Dummy', 'ハシカワダミー': 'Dummy', 'ハシウミダミー': 'Dummy',
         'カエン': 'Flame', 'ロケット ホウ': '로켓포', 'タンク': 'Tank'}
K8 = {v: k + 1 for k, v in UN.S.items()}
for _k, _c in zip(range(0xA1, 0xAD), 'ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ'): K8[_c] = _k
K8[' '] = 1; K8['-'] = K8['ー']
WORDS = (('ターン', 3), ('ジコク', 4), ('ドウメイ', 4), ('テキコク', 4), ('カイメツ', 4), ('セイゾン', 4), ('オーディオ', 9), ('BGMセレクト', 7), ('サウンドテスト', 9),
         ('リクジョウ', 5), ('コウクウ', 4), ('カイジョウ', 5))


def rows(f):
    return [l.rstrip('\n').split('\t') for l in open('work/text/%s.tsv' % f, encoding='utf-8') if l[0] != '#']


def table():
    """원문 → 출력. 공통 한글 + 영문."""
    k, _, _ = A.load_ko()
    com = dict(EXTRA)
    for p in rows('small'):
        if p[1] == 'W': com[p[4]] = k[p[0]][0][5]
    K2 = {p[0]: p[-1] for p in rows('ko_small2') if len(p) > 1}
    for p in rows('small2'):
        if p[1] in 'GW': com[p[4]] = K2[p[0]]
    K3 = {p[0]: p[-1] for p in rows('ko_small3') if len(p) > 1}
    for p in rows('small3'):
        if int(p[0]) < 1880: com[p[4]] = K3[p[0]]
    com = {a: TRIM.get(b, b) for a, b in com.items()}
    rom = {p[1]: p[2] for p in rows('romaji')}
    for p in rows('romaji2'): rom.setdefault(p[0], p[1])
    return com, rom


def cells(tag, com, rom):
    """파일별 자리 (fn, off, 칸, 원문, 출력). 표에 없는 가나 줄은 miss."""
    R, iso, E = HS.scan(tag); out = []; miss = collections.Counter()
    rd = lambda n: iso.read(*E[n][1:3])
    tr = lambda t: com[t] if t in com else rom.get(t)
    for g, fn, o, n, t in R:
        v = tr(t)
        if v is None: miss[t] += 1; continue
        out.append((fn, o, n, t, v))
    g2 = rd('/GAME2.BIN')
    # 작전 이름 표 10칸 + 00
    a = g2.find(bytes(K8[c] for c in 'フランス') + b'\x01' * 6 + b'\0'); o = a
    while a >= 0 and g2[o + 10] == 0 and HS.dec(g2[o:o + 10]) and '<' not in HS.dec(g2[o:o + 10]):
        t = HS.dec(g2[o:o + 10]); v = tr(t)
        if HS.HASK.search(t):
            if v is None: miss[t] += 1
            else: out.append(('/GAME2.BIN', o, 10, t, v))
        o += 11
    # 작전 시나리오 이름 표(8칸 + 00 + 코드 3칸)
    if tag == 'F':
        o = 0x1C9AF
        while o + 12 <= len(g2) and g2[o + 8] == 0 and all(1 <= x <= 0xAD for x in g2[o:o + 8]):
            t = HS.dec(g2[o:o + 8]); v = tr(t)
            if HS.HASK.search(t):
                if v is None: miss[t] += 1
                else: out.append(('/GAME2.BIN', o, 8, t, v))
            o += 12
    # 지형 10칸: GAME2 앞쪽 짧은 표(자리표) + 뒤쪽 긴 표(GAME2·SHINHEI 사본)
    for g, t, tg, fn, oh, n in rows('small2_pos'):
        if g == 'G' and tg == tag:
            v = tr(t)
            if v is None: miss[t] += 1
            else: out.append((fn, int(oh, 16), int(n), t, v))
    dm = bytes(K8[c] for c in 'ダミー') + b'' * 7
    for fn in E:
        if fn in ('/GAME2.BIN', '/SHINHEI.BIN'):
            d = rd(fn); end = 0
            for m in re.finditer(re.escape(dm), d):
                o = m.start()
                if o < end: continue
                while o + 10 <= len(d) and all(1 <= x <= 0xAD for x in d[o:o + 10]):
                    t = HS.dec(d[o:o + 10])
                    if HS.HASK.search(t):
                        v = tr(t)
                        if v is None: miss[t] += 1
                        else: out.append((fn, o, 10, t, v))
                    o += 10
                end = o
    # 낱말들(지형·작전 표 구역 밖)
    for w, n in WORDS:
        b = bytes(K8[c] for c in w)
        for m in re.finditer(re.escape(b), g2):
            q = m.start()
            sh = 0x510 if tag == 'F' else 0                    # 작전 GAME2 앞쪽은 0x510 밀림(묶음 위치 차이)
            if (0x19CE0 + sh < q < 0x19D40 + sh) or (0x1AF00 + sh < q < 0x1B000 + sh) or (tag == 'F' and 0x1B500 < q < 0x1B600) or (0x21000 < q < 0x24000) or (0x7B000 < q < 0x80000):
                out.append(('/GAME2.BIN', q, n, w, com[w]))

    def unit(fn, d, o):
        t = HS.dec(d[o:o + 9])
        if HS.HASK.search(t) and '<' not in t:
            v = tr(t)
            if v is None: miss[t] += 1
            else: out.append((fn, o, 9, t, v))
    for fn in E:
        if '/UNITPACK/UPK' in fn:
            d = rd(fn)
            for m in re.finditer(b'\xff\xff', d):
                q = m.start()
                if q >= 0x1C and all(0 < x < 0xAE for x in d[q - 0x1C:q - 0x13]) and d[q - 0x1C] != 1: unit(fn, d, q - 0x1C)
    for fn in ('/GAME2.BIN', '/SHINHEI.BIN'):
        d = rd(fn); a = d.find(bytes([0x7F, 0x50, 1, 1]))
        if a < 0: continue
        s = a
        while s > 0 and (d[s - 1] == 0 or 1 <= d[s - 1] <= 0xAD): s -= 1
        e = a
        while e < len(d) and (d[e] == 0 or 1 <= d[e] <= 0xAD): e += 1
        p = s
        for x in d[s:e].split(b'\0'):
            t = HS.dec(x); v = tr(t)
            if v is not None and len(x) >= 3: out.append((fn, p, len(x), t, v))
            elif len(x) >= 3 and HS.HASK.search(t) and '<' not in t: miss[t] += 1
            p += len(x) + 1
    return sorted(set(out)), miss, iso, E


def plan(tag='K'):
    com, rom = table(); C, miss, iso, E = cells(tag, com, rom)
    syl = collections.Counter(c for _, _, _, _, v in C for c in v if '가' <= c <= '힣')
    return com, rom, C, miss, iso, E, syl


HAND = {'총': ['...#....', '.#####..', '..#.#...', '...#....', '#######.', '..###...', '.#...#..', '..###...']}   # 공용 글꼴은 종과 같은 그림


def cell_bytes(ch):
    g = [[c == '#' for c in r] for r in HAND[ch]] if ch in HAND else han8gdm.glyph(ch); b = bytearray()
    for y in range(8):
        for x in range(0, 8, 2): b.append((INK if g[y][x] else 0) << 4 | (INK if g[y][x + 1] else 0))
    return bytes(b)


def patch(tag, extra, log=print):
    """{파일: 바이트} 에 반각 패치. extra 에 이미 있으면 그 위에."""
    com, rom, C, miss, iso, E, syl = plan(tag)
    order = [c for c, _ in syl.most_common()]
    assert len(order) <= len(FREE), (len(order), len(FREE))
    M = {c: v + 1 for c, v in zip(order, FREE)}
    enc = dict(K8); enc.update(M)
    F = {}
    def get(fn):
        if fn not in F: F[fn] = bytearray(extra.get(fn) or iso.read(*E[fn][1:3]))
        return F[fn]
    over = []
    for fn, o, n, t, v in C:
        if len(v) > n: over.append((fn, hex(o), t, v)); continue
        get(fn)[o:o + n] = bytes(enc[c] for c in v) + b'\x01' * (n - len(v))
    assert not over, over[:10]
    sheet = bytearray(iso.read(*E['/VIEWCG/ASC8X8.BIN'][1:3]))
    wm = get('/W_MAP2.BIN'); wo = bytes(wm).find(sheet[32:32 * 40]) - 32
    print('W_MAP2 반각 사본', hex(wo))
    for c, v in M.items():
        g = cell_bytes(c); sheet[(v - 1) * 32:v * 32] = g
        if wo >= 0 and v - 1 < 157: wm[wo + (v - 1) * 32:wo + v * 32] = g
    F['/VIEWCG/ASC8X8.BIN'] = sheet
    log('반각: 자리 %d, 음절 %d/%d, 파일 %d' % (len(C), len(M), len(FREE), len(F)))
    return {k: bytes(v) for k, v in F.items()}, M


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    tag = sys.argv[1] if len(sys.argv) > 1 else 'K'
    com, rom, C, miss, iso, E, syl = plan(tag)
    print('자리', len(C), '파일', len({c[0] for c in C}), collections.Counter(c[0].split('/')[1][:8] for c in C).most_common(8))
    print('표에 없음', len(miss), miss.most_common(60))
    print('칸 넘침', [c for c in C if len(c[4]) > c[2]][:30])
    print('음절', len(syl), '칸', len(FREE), '한 번뿐', sum(1 for x in syl.values() if x == 1))
    print(''.join(c for c, _ in syl.most_common()))
    pos = collections.defaultdict(list)
    for c in C: pos[c[0]].append((c[1], c[1] + c[2], c[3]))
    bad = 0
    for fn, v in pos.items():
        v = sorted(set(v))
        for a, b in zip(v, v[1:]):
            if a[1] > b[0]: bad += 1; print('겹침', fn, hex(a[0]), a[2], hex(b[0]), b[2])
    print('겹침', bad)
