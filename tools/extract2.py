# -*- coding: utf-8 -*-
"""화면 전용 글꼴 문자열 추출: 턴 이벤트·맵 이름·백업 메시지·연표 → work/text/extra.tsv, my files/tsv/wad_012.tsv.
  python tools/extract2.py [--write]"""
import sys, os, glob, struct, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprite_scan as SS, asc_table
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
NL = chr(92) + 'l'
pk = glob.glob(SS.B + r'\*Koutetsu*')[0]; ik = Iso(sorted(glob.glob(pk + r'\*(Track 1).bin'))[0]); ek = {f[0]: f for f in ik.walk()}
rk = lambda n: ik.read(*ek[n][1:3])
mp = rk('/VIEWCG/ASC16MAP.BIN'); cg = rk('/VIEWCG/ASC16X16.BIN') + rk('/VIEWCG/ASC16_2.BIN')
w = struct.unpack('>%dH' % (len(mp) // 2), mp); G = {}
for i in range(len(w) // 4):
    g = b''.join(cg[(t - 0x800) * 32:(t - 0x800) * 32 + 32] for t in w[i * 4:i * 4 + 4]); G.setdefault(g, {283: 'ヘ', 317: 'バ', 322: 'ボ', 463: 'ビ', 438: 'ピ'}.get(i, asc_table.SHEET[i]))


def font(d, base, cnt, fix={}):
    return [fix.get(i, G.get(d[base + i * 128:base + i * 128 + 128], '?').replace('□', '?')) for i in range(cnt)]


rows = []
# 턴
T = rk('/TURNASC.BIN'); L = font(T, 0, 188, {7: '北', 8: '方', 9: 'よ', 25: '連', 37: '向', 100: '西', 144: '衆', 145: '平', 146: '央', 147: '面', 148: '師', 160: '蒙', 161: '古', 162: '満', 163: '州', 169: '支', 170: '援', 179: 'ヒ', 180: '守', 187: '太'})
d = rk('/GAME2.BIN'); a = d.find(struct.pack('>H', 0xFFFF), 0x5D860)
i = 0x5D800
v = struct.unpack('>%dH' % 700, d[i:i + 1400]); s = ''; st = None; seg = []
for k, x in enumerate(v):
    if x == 0xFFFF:
        if s.strip('　'): seg.append((st, s.strip('　')))
        s = ''; st = None
    elif x == 0xFFFE: s += NL
    elif x < 188:
        if st is None: st = i + k * 2
        s += L[x]
    else: s = ''; st = None
seg = [q for q in seg if re.search('[ぁ-ヶ一-龥]', q[1]) and '?' not in q[1] and len(q[1]) >= 1][:40]
for o, t in seg: rows.append(('T', t, 'GAME2', o))
print('턴', len(seg), [t for o, t in seg][:6])
# 맵 이름
g = rk('/GMS2.BIN'); L = font(g, 0xD95C, 99)
v = struct.unpack('>%dH' % ((0x1A00 - 0x14A0) // 2), g[0x14A0:0x1A00]); s = ''; st = None
for k, x in enumerate(v):
    if x == 0xFFFF or x > 200:
        t = s.strip('　')
        if len(t) >= 2 and re.search('[ァ-ヶ]', t) and '?' not in t: rows.append(('M', t, 'GMS2', st))
        s = ''; st = None
    elif x == 0: s += '　'
    elif 1 <= x <= 99:
        if st is None: st = 0x14A0 + k * 2
        s += L[x - 1]
# 백업
r = rk('/RMC2.BIN'); L = font(r, 0x44, 88); L = ['面' if c == '?' and i == 41 else c for i, c in enumerate(L)]
L = [c.replace('?', 'よ') if i == 20 else c for i, c in enumerate(L)]
v = struct.unpack('>%dH' % ((0x2F40 - 0x2C48) // 2), r[0x2C48:0x2F40]); s = ''; st = None
for k, x in enumerate(v):
    if x == 0xFFFF:
        if s.strip('　'): rows.append(('R', s.strip('　').replace('画?', '画面'), 'RMC2', st))
        s = ''; st = None
    elif x == 0xFFFE: s += NL
    elif x == 0: s += '　'
    elif 1 <= x <= 88:
        if st is None: st = 0x2C48 + k * 2
        s += L[x - 1]
    else: s = ''; st = None
# 연표
m = rk('/W_MAP2.BIN'); FX = {14: '」', 46: '北', 78: '連', 93: 'よ', 108: '満', 111: '支', 128: 'ヒ', 151: '州', 163: '方', 185: '溥', 187: '執', 188: '政', 197: '授', 201: '裁', 209: '認', 215: '創', 220: '唆', 228: '帯', 230: '承', 232: '競', 233: '争', 239: '勃', 240: '義', 241: '勇', 244: '枢', 245: '軸', 248: '紛', 249: '蘆', 250: '溝', 252: '面', 253: '的', 261: '暦', 263: '平', 265: '帥', 266: '謀', 271: '徴', 277: '準', 288: '恫', 289: '喝', 323: '奪', 348: '向', 353: '太', 359: '敢', 367: '沈', 383: '逆', 403: '守'}
L = font(m, 0x4E128, 900, FX)
a = 0x4A040; n = (0x4E128 - a) // 2; v = struct.unpack('>%dH' % n, m[a:a + n * 2])
s = ''
for x in v:
    if x == 0: s += '|'
    elif x == 1: s += '　'
    elif 2 <= x < 902: s += L[x - 2]
    else: s += '#'
s = s[s.index('1919年'):]
out = []
for e in re.split('　{2,}', s):                                    # 빈칸 둘 이상 = 항목 끝, 0 둘 이상 = 항목 안 줄 끝
    e = e.strip('|　#').split('#')[0]
    if not e: continue
    lines = [q.strip('　|').replace('|', '　') for q in re.split('\\|{2,}', e)]
    t = NL.join(q for q in lines if q)
    if re.search('[ぁ-ヶ一-龥]', t) and not re.fullmatch('[0-9]+年', t): out.append(t)
for e in s.split('#')[1:]:                                         # 뒷부분 = FFFF 로 끊긴 문장
    t = e.strip('|　').replace('|', '　')
    if len(t) >= 8 and re.search('[ぁ-ん]', t) and t.count('?') <= 3: out.append(t)
print('연표 항목', len(out), '글자', sum(len(t) for t in out), '최대 줄', max(len(l) for t in out for l in t.split(NL)))
print(' ## '.join(out[:6])[:500]); print(' ## '.join(out[-3:])[:300])
for t in out: rows.append(('Y', t, 'W_MAP2', 0))
FIXW = (('スロパキア', 'スロバキア'), ('アルパニア', 'アルバニア'), ('一挨', '一揆'), ('ミュンへン', 'ミュンヘン'), ('パストーニュ', 'バストーニュ'), ('ポストン', 'ボストン'), ('パルジ', 'バルジ'), ('ラパウル', 'ラバウル'))
U = {}
for g_, t, f, o in rows:
    for x, y in FIXW: t = t.replace(x, y)
    U.setdefault((g_, t), (f, o))
print('합', len(U), collections_len := sum(len(k[1]) for k in U))
if '--write' in sys.argv:
    H = '#번호\t구분\t글자수\t쓰임\tJP\tKO\n'; n0 = 1599; b = ''
    for i, ((g_, t), (f, o)) in enumerate(U.items(), 1):
        b += '%05d\t%s\t%d\t1\t%s\t\n' % (n0 + i, g_, max(len(x) for x in t.split(NL)), t)
    open('work/text/extra.tsv', 'w', encoding='utf-8', newline='\n').write(H + b)
    print('크기', len(b.encode()))
if '--raw' in sys.argv:
    p0 = s.index('保護国に'); print(repr(s[p0:p0 + 700])); print(len(s), s.count('#'))
    print(hex(a + 2 * (0)), [hex(x) for x in v[s.count('#') and 0:0]])
