# -*- coding: utf-8 -*-
"""작전파일 전용 글꼴 문자열 풀기 → work/text/f_raw.tsv + 미판독 시트(읽기 전용).  python tools/f_text.py"""
import sys, os, glob, struct, hashlib, collections, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, asc_table, extract as X
from iso9660 import Iso
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.stdout.reconfigure(encoding='utf-8')
def op(pat):
    p = glob.glob(SS.B + pat)[0]; i = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); return i, {f[0]: f for f in i.walk()}
a, ea = op(r'\*Koutetsu*'); b, eb = op(r'\*Sakusen*')
ra = lambda n: a.read(*ea[n][1:3]); rb = lambda n: b.read(*eb[n][1:3])
mp = ra('/VIEWCG/ASC16MAP.BIN'); w = struct.unpack('>%dH' % (len(mp) // 2), mp)
FIX = {283: 'ヘ', 317: 'バ', 322: 'ボ', 463: 'ビ', 438: 'ピ'}
G = {}
for cg in (ra('/VIEWCG/ASC16X16.BIN') + ra('/VIEWCG/ASC16_2.BIN'), rb('/VIEWCG/ASC16X16.BIN') + rb('/VIEWCG/ASC16_2.BIN')):
    for i in range(len(w) // 4):
        c = FIX.get(i, asc_table.SHEET[i])
        if c == '□': continue
        g = b''.join(cg[(t - 0x800) * 32:(t - 0x800) * 32 + 32] for t in w[i * 4:i * 4 + 4]); G.setdefault(hashlib.md5(g).hexdigest()[:10], c)
G.update({k: v for k, v in X.sf_table().items() if k not in G})
for l in open('work/text/glyph_final.tsv', encoding='utf-8'):
    k, v = l.rstrip('\n').split('\t'); G.setdefault(k, v)
F = [('/TURNASC.BIN', '/TURNASC.BIN', 0, 206, '/GAME2.BIN'), ('/GMSFONT.BIN', '/GMSFONT.BIN', 0, 371, '/GMS1.BIN'), ('/KASOU', '/KASOU.BIN', 0x12CFC, 452, '/KASOU.BIN'), ('/GAMEOVER', '/GAMEOVER.BIN', 0xFE8, 270, '/GAMEOVER.BIN')]
FXX = {'/TURNASC.BIN': {76: '絡', 124: '邦', 125: '師', 154: '峡', 159: '避', 182: '央'},
 '/GMSFONT.BIN': {137: '満', 138: '州', 144: '巨', 146: '轟', 158: '森', 164: '番', 170: '瀬', 171: '戸', 189: '仮', 196: '投', 199: '導', 207: '穀', 208: '倉', 232: '史', 236: '竹', 261: '亜', 265: '織', 273: '濃', 274: '厚', 281: '圏', 284: '奪', 297: '真', 308: '楽', 311: '避', 317: '質', 326: 'よ', 328: '支', 336: '深', 341: '昔', 342: '懐', 348: '単', 350: '原', 352: '知', 353: '人', 358: '美'},
 '/KASOU': {67: '豊', 78: '莫', 81: '益', 94: '裕', 107: '満', 110: '繁', 122: '錯', 123: '覚', 126: 'づ', 146: '布', 155: '寝', 156: '耳', 200: '閣', 206: '危', 215: '窮', 219: '割', 234: '緊', 252: '致', 253: 'ご', 267: '槌', 280: '遠', 281: '征', 283: '叩', 285: '来', 291: '支', 304: '態', 335: '秩', 336: '序', 352: '得', 354: '劣', 355: '跳', 360: '元', 364: '搾', 366: '膨', 371: '脱', 375: '刺', 380: 'や', 384: '締', 385: '申', 386: '拒', 387: '否', 396: '符', 404: '継', 405: '総'},
 '/GAMEOVER': {71: '奪', 96: '邦', 98: '師', 134: '峡', 139: '避', 165: '央', 248: '満', 249: '州', 252: '巨', 254: '轟', 260: '森', 263: '番', 267: '瀬', 268: '戸'}}
un = []; rows = []; LMAP = {}
for nm, ff, base, n, sf in F:
    d = rb(ff); L = []
    for i in range(n):
        g = d[base + i * 128:base + i * 128 + 128]; c = G.get(hashlib.md5(g).hexdigest()[:10])
        if c is None: c = FXX.get(nm, {}).get(i, '?'); (c == '?') and un.append((nm, i, g))
        L.append(c)
    cells_ = list(L); sh_ = 0
    if nm == '/KASOU':                                               # 글자 번호 어긋남 찾기: 조사가 가장 많이 나오는 값
        s0 = rb(sf); W0 = struct.unpack('>%dH' % ((0x2D000 - 0x2C8AE) // 2), s0[0x2C8AE:0x2D000]); best = (0, 0)
        for sh in range(-80, 81):
            c0 = sum(1 for v in W0 if 0 <= v + sh < n and L[v + sh] in 'のはをにがでとしたる、。')
            best = max(best, (c0, sh))
        print('KASOU 어긋남', best); sh_ = best[1]; L = (['?'] * 80 + L + ['?'] * 80)[80 + best[1]:][:n + 80] if best[1] else L
    LMAP[nm] = dict(L=L, cells=cells_, sh=sh_, base=base, n=n)
    s = rb(sf); W = struct.unpack('>%dH' % (len(s) // 2), s[:len(s) // 2 * 2])
    ff_ = [i for i, x in enumerate(W) if x == 0xFFFF]; c = 0
    for x, y in zip(ff_, ff_[1:]):
        q = W[x + 1:y]
        if not 2 <= len(q) <= 300 or any(v >= n and v != 0xFFFE for v in q): continue
        t = ''.join('/' if v == 0xFFFE else L[v] for v in q).strip('　')
        if len(re.findall('[ぁ-ヶ一-龥]', t)) >= 2 and len(set(t)) >= 2:
            rows.append((nm, (x + 1) * 2, t)); c += 1
    print(nm, n, L.count('?'), '문자열', c, flush=True)
    for r in [r for r in rows if r[0] == nm][:8]: print('  ', hex(r[1]), r[2][:80])
import json; json.dump(LMAP, open('work/text/f_L.json', 'w', encoding='utf-8'), ensure_ascii=False)
open('work/text/f_raw.tsv', 'w', encoding='utf-8', newline='\n').write(''.join('%s\t%X\t%s\n' % r for r in rows))
N = ImageFont.truetype(r'C:\Windows\Fonts\msgothic.ttc', 11)
pg = Image.new('L', (20 * 58, ((len(un) + 19) // 20) * 66), 20); dr = ImageDraw.Draw(pg)
for j, (nm, i, g) in enumerate(un):
    bb = np.frombuffer(g, np.uint8); q = np.stack([bb >> 4, bb & 15], 1).reshape(4, 8, 8); o = np.zeros((16, 16), np.uint8)
    o[:8, :8], o[:8, 8:], o[8:, :8], o[8:, 8:] = q
    x, y = j % 20 * 58, j // 20 * 66; pg.paste(Image.fromarray(o * 17).resize((48, 48), 0), (x + 2, y + 2)); dr.text((x + 2, y + 52), '%s%d' % (nm[1], i), font=N, fill=200)
pg.save('work/view/f_un.png'); print(len(un), pg.size)
