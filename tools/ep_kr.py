# -*- coding: utf-8 -*-
"""엔딩 EP 그림 한글화.  python tools/ep_kr.py 폴더 [이름 …]  (이름 없으면 19개 전부)
  EP = 16비트 704×336(왼쪽·오른쪽 352 폭, 위아래 3쪽 112 높이). 폴더/이름.bin, 폴더/prev_이름.png. 디스크는 안 건드림."""
import sys, os, glob, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, bdf
from iso9660 import Iso
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.stdout.reconfigure(encoding='utf-8')
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True); ONLY = sys.argv[2:]
F = bdf.Font(r'C:\claude\utils\font\Galmuri-v2.40.3\Galmuri11-Bold.bdf')
N = chr(92) + 'l'
LINE = 300
ko = {}
for l in open('work/text/ko_final.tsv', encoding='utf-8'):
    if l[0] != '#':
        i, g, v = l.rstrip('\n').split('\t', 2)
        if g.startswith('E_') and not g.startswith('E_SF'): ko[g[2:]] = v
p = glob.glob(SS.B + r'\*Koutetsu*')[0]; iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0])
eps = sorted((f for f in iso.walk() if f[0].endswith('.EP')), key=lambda f: f[0])


def width(t): return F.draw(t)[1]


def lines(t):
    out = []
    for para in t.split(N):
        cur = ''
        for w in re.findall(r'[^ ]+ ?', para):
            if cur and width((cur + w).rstrip()) > LINE: out.append(cur.rstrip()); cur = ''
            cur += w
        out.append(cur.rstrip())
    return out


def dil(m, n):
    for _ in range(n):
        q = m.copy()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)): q |= np.roll(np.roll(m, dy, 0), dx, 1)
        m = q
    return m


def inpaint(a, mask):
    a = a.copy(); known = ~mask; a[mask] = 0
    for _ in range(60):
        if known.all(): break
        s = np.zeros_like(a); c = np.zeros(mask.shape, np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            s += np.roll(np.roll(a * known[..., None], dy, 0), dx, 1); c += np.roll(np.roll(known.astype(np.float32), dy, 0), dx, 1)
        new = (c > 0) & ~known; a[new] = s[new] / c[new][:, None]; known |= new
    return a


GS = r'C:\Windows\Fonts\batang.ttc'


def wrapf(t, f):
    out = []
    for para in t.split(N):
        cur = ''
        for w in re.findall(r'[^ ]+ ?', para):
            if cur and f.getlength((cur + w).rstrip()) > LINE: out.append(cur.rstrip()); cur = ''
            cur += w
        out.append(cur.rstrip())
    return out


def page(rgb, t, ov=None):
    """쪽 하나(112×352): 흰 글자 지우고 궁서체로, 원본 글자 줄이 차지하던 위아래 폭을 채운다."""
    lum = rgb.sum(2); box = np.zeros(lum.shape, bool); box[6:106, 22:334] = True
    gx = np.abs(np.diff(lum, axis=1)) > 170                              # 글자 줄은 가로 명암 변화가 많다
    cnt = (gx & box[:, 1:]).sum(1); g = []; y = 0
    while y < 112:
        if cnt[y] >= 26:
            e = y
            while e < 112 and cnt[e] >= 26: e += 1
            if e - y >= 5: g.append((y, e))
            y = e
        else: y += 1
    if g:                                                                # 짧은 끝줄: 앞줄 바로 아래 약한 줄도 글자 줄
        while True:
            e = g[-1][1]; r = [y for y in range(e + 2, min(e + 12, 106)) if cnt[y] >= 3]
            if len(r) < 4: break
            g.append((r[0], r[-1] + 1))
    y0, y1 = (g[0][0], g[-1][1]) if g else (40, 70)
    if ov: y0, y1 = ov; g = [ov]
    dark = dil(lum < 300, 2)                                             # 글자는 어두운 그림자 옆의 밝은 화소
    m = box & (lum > 440) & dark
    k = np.zeros_like(m)
    for a0, a1 in g: k[max(0, a0 - 1):a1 + 1, 22:334] = True
    m = (m | (box & (lum > 530) & (rgb.max(2) - rgb.min(2) < 44) & dil(m, 6))) & k
    a = inpaint(rgb, dil(m, 2))
    H = y1 - y0
    size = 16; f = ImageFont.truetype(GS, size, index=2); L = wrapf(t, f)     # 전 쪽 같은 크기
    n = len(L); K = 4                                                     # 4배로 그려 줄여서 획을 매끈하게
    big = Image.new('L', (352 * K, 112 * K), 0); db = ImageDraw.Draw(big); fb = ImageFont.truetype(GS, size * K, index=2)
    x = 30
    step = max(19, int((H - size) / max(1, n - 1))) if n > 1 else 0          # 줄 간격 최소 18, 정수 위치(줄마다 번짐 달라지지 않게)
    top = int(y0 + (H - (step * (n - 1) + size)) / 2); top = max(5, min(top, 106 - step * (n - 1) - size))
    for i, s_ in enumerate(L):
        y = top + i * step
        db.text((x * K, y * K), s_, 255, font=fb)
    m = np.asarray(big.resize((352, 112), Image.BOX), np.float32) / 255
    m = np.clip(m * 1.5, 0, 1)                                           # 획이 얇아 살짝만 올림
    sh = np.zeros_like(m); sh[1:, 1:] = m[:-1, :-1]
    a = a * (1 - sh[..., None]) + np.array((10, 10, 8), np.float32) * sh[..., None]
    a = a * (1 - m[..., None]) + np.array((250, 248, 238), np.float32) * m[..., None]
    im = a
    return np.asarray(im, np.float32), n


OV = {('G_L_N', 2): (36, 74)}
mx = 0
for f in eps:
    n = f[0][1:-3]
    if ONLY and n not in ONLY: continue
    b = iso.read(f[1], f[2]); w = np.frombuffer(b, '>u2').reshape(336, 704); msb = w & 0x8000
    rgb = np.stack([(w & 31) << 3, (w >> 5 & 31) << 3, (w >> 10 & 31) << 3], 2).astype(np.float32); new = rgb.copy()
    for k in range(3):
        t = ko['%s_%d' % (n, k + 1)]
        for c in (0, 352):
            q, nl = page(rgb[k * 112:(k + 1) * 112, c:c + 352], t, OV.get((n, k))); new[k * 112:(k + 1) * 112, c:c + 352] = q; mx = max(mx, nl)
    r = np.clip(new, 0, 255).astype(np.uint16) >> 3
    (msb | r[:, :, 0] | r[:, :, 1] << 5 | r[:, :, 2] << 10).astype('>u2').tofile('%s/%s.bin' % (OUT, n))
    pg = Image.new('RGB', (704 * 2 + 8, 336 * 1), (0, 0, 0))
    pg.paste(Image.fromarray(rgb[:, 352:].astype(np.uint8)).resize((704, 672 // 2 * 2), 0).crop((0, 0, 704, 336)), (0, 0))
    S = 2; pg = Image.new('RGB', (352 * S * 2 + 8, 336 * S), (0, 0, 0))
    for i, q in enumerate((rgb[:, 352:], new[:, 352:])):
        pg.paste(Image.fromarray(np.clip(q, 0, 255).astype(np.uint8)).resize((352 * S, 336 * S), 0), (i * (352 * S + 8), 0))
    pg.save('%s/prev_%s.png' % (OUT, n))
print('최대 줄', mx)
