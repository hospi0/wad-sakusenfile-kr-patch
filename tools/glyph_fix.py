# -*- coding: utf-8 -*-
"""눈으로 읽은 글자 시트(gs_0~2, glyph_sheet.py 순서)로 판독 표를 고치고 문장을 다시 푼다(읽기 전용).
  python tools/glyph_fix.py → work/text/glyph_final.tsv, work/text/saku.tsv"""
import sys, os, glob, struct, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
SHEET = [
 '一　、「あいうえおがかきョぎくぐけげこさざし', 'じすずせそただらちっつづてでとどなにぬのはば', 'びぶへヘベペほぼまみむめもゆよるれろわをんア',
 'ァィイウ主エェオォ力ガキギクグコゴサシジスズ', 'セソタダチツッデテドトナニヌネノハバパヒピビ', 'フブプべホボポマミムメモやャヤユ立ュヨラルレ',
 'ワ＝ンヴカケ・覇ー～上下不与世丘中リ乗乱１」', '了予争事二五－交京人仁今仏付代令以件任伏体会', '伝伸位低休何余作使倒価侵挽保機倍候値停健備傲',
 '傷傾儀偉充先入両共兵内再冠凱出分切列初判利到', '制前功加労効務勝勢動包化北区＋川半南占印危却', '原厳参又及左友反収取受口古可台右号司向君各否',
 '含告呼命和員寄唱問善響哨嘉器回団困囲国土圧在',
 '地執堅報場境増壊士夏外多夜大天太失央本奇★々', '奏奪奮好始威存季孤守安完営定実宣有密寒対射将', '導小少届同局展山岳岸峡島峻嵐州差市布帝師帯帰',
 '常幅平年幹幾底府度逞建弊引％強形影役征後得御', '復徹心必応快思性恐悩態悪情想慢側意優慣協成我', '戦房所脈手打払抑投抗折抜被抵押拗拠拡持指挙挟',
 '挫挺掃排捉接換握援損携摩撃撤捕支☆攻敗敢数整', '敵敷文新断方施旋既日旨早時暇堡至量暗更最月末', '未り条来杯梁果東染格基棚森極構様標徐橋根撹権',
 '模次政放止正死残段殺母民気水求決沈沖河油沿況', '泊法波洋派流海消活渉渡温渾湖湾満源滅滞潟激測', '湿混．火点為烈無焦然熱爆物牲牽犠状独狭猛獲玉',
 '王珊現理瑚甚生産由甲申画当界間略異疎疲発難的',
 '皇急盟目直真固着督知石砕砲破順確礎祈相禄重移', '稜積空突窮端竹符第索築薄米粉精系討納転終経結', '維給統絶継続総緒線編練縄繰縮置翼考耗肉能脅脱',
 '膠膨蘭自春費航般船艇艦苛苦英率塞菊落驚蒙蓄蓋', '察組血衆行街衛衝術表衰裂装補襲西要見規視期解', '害言釘計設許試詰読課調諸冬講護豪＄ロ資走越超',
 '延足跡路隊躍車軍載輸辺込迅迎近返迫追退送逃逆', '逐途逸通速達進遂遅道連遠遣遮遽避還那邦郊都部', '配里訓鈍珠鋭域長開闘関防阻降限陣除陵陸険陥周',
 '階際隙障隻集雪零電面合頃崩須頑領頭頼題飛全食', '首駄駆験高絞網変！７’／。０２４５６８９：？', 'Ｂ［］Ｉ３Ｍ',
]
rows = [l.rstrip('\n').split('\t') for l in open('work/text/glyph.tsv', encoding='utf-8')]
order = sorted(range(len(rows)), key=lambda i: rows[i][1])
flat = ''.join(SHEET)
assert len(flat) == len(order) == 820, (len(flat), len(order))
hm = {rows[i][0]: c for i, c in zip(order, flat)}
with open('work/text/glyph_final.tsv', 'w', encoding='utf-8', newline='\n') as f:
    for h, c in hm.items(): f.write('%s\t%s\n' % (h, c))
R = r'C:\claude\roms\ss\World Advanced Daisenryaku\World Advanced Daisenryaku - Koutetsu no Senpuu (Japan) (Rev A) (10M)'
iso = Iso(glob.glob(R + r'\*(Track 1).bin')[0]); fs = iso.walk(); ent = {f[0]: f for f in fs}
d = iso.read(*ent['/SAKUSEN/SAKU_DT.BIN'][1:3])
F = {}
for k in range(1, 55):
    b = iso.read(*ent['/SAKUSEN/SAKU_F%02d.BIN' % k][1:3]); F[k] = [hashlib.md5(b[i:i + 128]).hexdigest()[:10] for i in range(0, len(b), 128)]
n = len(d) // 2; w = struct.unpack('>%dH' % n, d[:n * 2])
res = []; s = None
for i in range(0x17E98 // 2, n):
    x = w[i]
    if x == 0xFFFF:
        if s is not None: res.append((s * 2, w[s:i]))
        s = i + 1
    elif s is None: s = i
# 구역 나누기: 제목 줄은 글자 번호 32 부터. 그 앞의 짧은 «자국 사령부 파괴» 줄은 앞 시나리오 글꼴을 쓴다
seg = [[]]; mx = -1
for j, (o, ids) in enumerate(res):
    v = [x for x in ids if x < 0x100]
    nxt = [x for x in res[j + 1][1]] if j + 1 < len(res) else []
    if 32 in v[:3] and mx > 90 and seg[-1]:
        if len(ids) <= 9 and 32 in nxt[:3] or (len(ids) == 8 and 32 not in v[:1]):
            seg[-1].append((o, ids)); seg.append([]); mx = -1; continue
        seg.append([]); mx = -1
    seg[-1].append((o, ids))
    if v: mx = max(mx, max(v))
KANA = set('のはをにがでとしたるてい、。')
L = []; used = {}
for si, sg in enumerate(seg):
    best = (-1, 0)
    for k in F:
        c = 0
        for o, ids in sg:
            if len(ids) < 30: continue
            for x in ids:
                if x < len(F[k]) and hm[F[k][x]] in KANA: c += 1
                elif x >= len(F[k]) and x < 0x100: c -= 5
        best = max(best, (c, k))
    k = min(si + 1, 54); used.setdefault(k, []).append(si)
    for j, (o, ids) in enumerate(sg):
        if si and j == 0 and len(ids) == 8 and 0 < si < 54: pass
        t = ''.join(hm[F[k][x]] if x < len(F[k]) else '<%X>' % x for x in ids)
        L.append('%02d\t%02d\t%06X\t%d\t%s' % (si, k, o, len(ids), t))
open('work/text/saku.tsv', 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
print('줄', len(L), '글자', sum(int(l.split('\t')[3]) for l in L), '구역', len(seg), '구역 크기', [len(s) for s in seg])
print('구역→글꼴', [(si, k) for k, v in sorted(used.items()) for si in v][:60])
print('겹친 글꼴', {k: v for k, v in used.items() if len(v) > 1}, '안 쓴 글꼴', [k for k in F if k not in used])
