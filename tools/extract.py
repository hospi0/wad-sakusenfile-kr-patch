# -*- coding: utf-8 -*-
"""본편·작전파일 SAKU_DT 문장 추출 → work/text/master.tsv(통짜) · master_pos.tsv · my files/tsv/wad_NNN.tsv(18 KB).
  글자표 = work/text/glyph_final.tsv(본편), glyph_sf_final.tsv(작전). 「？」(글꼴 1번)는 줄바꿈 코드 → \\l.
  python tools/extract.py [--write]"""
import sys, os, glob, struct, hashlib, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso9660 import Iso
sys.stdout.reconfigure(encoding='utf-8')
B = r'C:\claude\roms\ss\World Advanced Daisenryaku'
SPLIT = 18 * 1024
SF_SHEET = [
 '一　、「あいうえおがかきぎくぐけげこさしじす', 'ずせそぞただらちっつてでとどなにぬねのはばび', 'ふぶべへほぼまみむめもゆよるれろわをんアイウ',
 'ユ主エオ力ギキクグコサザジシスズセゼソタダチ', 'ツッテトドナニネハバパヒフブプベホポマミムメ', 'モやャュヨラルレワ＝ンカ・義覇ー万三上下不与',
 '世中リ乱１」了予争事－交亡今他付令以件伏会体', '休何余作倒侵保信候値健備橋儀充先免入両共兵内', '再Ⅲ冠凄凶出刃分切列初判利到制前劇功加労勝勢',
 '勧動包化北＋十川半南占即却去参及友反取受叫可', '右司名向各含告味命和喉喜官器回団困囲国土圧在', '地埋報場境増壊士声夕外多夢大太失本奇★々奏奪',
 '女始姿威季守安完営定宣有宮容寒対封刻射将小少',
 '尚同層展岐岸島巡市帝帯幅平年広底府度建引％弱', '張強形彩待後従御復徹心必忌志思急性悪悲情惨想', '側意感慎優慮憑協成我戒戦戻手打投抗抜択被抵押',
 '招拠持指挟挫捨排描揮援損撃擁捕☆攻敗敢散数整', '敵立新朝断方旗既日早易時留焼堡量暗暴診最月望', '末机り条栄東果植楔業極構様徐横機樹権模次欲政',
 '歓放止正武死残段殿比民気肌決沈河沸治沿況法注', '流海消活渡温港準滅漠潜激．火灯灰点為烈焉無焦', '然熊熱爆爪片壮物牲犠状狂独猛献王理生甲明界畔',
 '略疲痕発難白的皇息盟監目直省眠眼固着短砂砕砦', '砲破順確示相祝重移種穴空突窓笛答算範築億薄籍', '粉第精約転終綻経結維給統絶続線練縦編置派群習',
 '翼考者聖肉胆背胸能脅脆認臨自舞航艦色苦率塞華',
 '落衆行街衛術表装補福襲西要見規視親期解触害言', '記許訴試誇誤調請論謀冬講警護＄負盾費ロ赤走越', '隊躍車軍較鷲辺込迅迎近返迫追退逃逆逐通速達進',
 '遂遅運過道連違遣選邸都部配酔訓鉄鋭域長開闘防', '阻降限陣除陸陽陥周隠雄集雌離雪非面合頓領頭全', '食首駆駐験骸網鳥麗黄鼓！７’／。身勇幸０２４',
 '５６８９：？［］３',
]


def sf_table():
    rows = [l.rstrip('\n').split('\t') for l in open('work/text/glyph_sf.tsv', encoding='utf-8')]
    order = sorted(range(len(rows)), key=lambda i: rows[i][1]); flat = ''.join(SF_SHEET)
    assert len(flat) == len(order) == 713, (len(flat), len(order))
    return {rows[i][0]: c for i, c in zip(order, flat)}


def disc(tag):
    p = glob.glob(B + (r'\*Koutetsu*' if tag == 'K' else r'\*Sakusen*'))[0]
    iso = Iso(sorted(glob.glob(p + r'\*(Track 1).bin'))[0]); fs = iso.walk(); ent = {f[0]: f for f in fs}
    d = iso.read(*ent['/SAKUSEN/SAKU_DT.BIN'][1:3])
    if tag == 'K':
        hm = dict(l.rstrip('\n').split('\t') for l in open('work/text/glyph_final.tsv', encoding='utf-8'))
        names = {k: '/SAKUSEN/SAKU_F%02d.BIN' % k for k in range(1, 55)}; t0 = 0x17E98
    else:
        hm = sf_table()
        names = {int(f[0][-7:-4]): f[0] for f in fs if '/SAK_F' in f[0]}; t0 = 0x1401C
    F = {}
    for i, k in enumerate(sorted(names), 1):
        b = iso.read(*ent[names[k]][1:3]); F[i] = [hashlib.md5(b[j:j + 128]).hexdigest()[:10] for j in range(0, len(b), 128)]
    n = len(d) // 2; w = struct.unpack('>%dH' % n, d[:n * 2])
    res = []; s = None
    for i in range(t0 // 2, n):
        x = w[i]
        if x == 0xFFFF:
            if s is not None: res.append((s * 2, w[s:i]))
            s = i + 1
        elif x >= 0x400: s = None
        elif s is None: s = i
    # 구역: 포인터 표 앞머리 = 시나리오마다 5개(제목·브리핑·결과 셋). 제목 위치부터 다음 제목 앞까지가 그 시나리오 글꼴.
    p0 = 0x25E3C if tag == 'K' else 0x1C040
    nums = range(54) if tag == 'K' else list(range(34)) + list(range(170, 177))   # 작전 표 = 시나리오 번호 칸(171~177 은 F171~)
    titles = [struct.unpack_from('>I', d, p0 + i * 20)[0] - 0x2C0000 for i in nums]
    assert titles == sorted(titles), '제목 포인터 순서'
    out = []
    for o, ids in res:
        k = max(1, sum(1 for t in titles if t <= o))
        out.append((k, o, ids))
    L = []
    for k, o, ids in out:
        t = ''
        for x in ids:
            if x >= 0x100: t += '<%X>' % x
            elif x >= len(F[k]): t += '〓'
            else: t += hm[F[k][x]]
        L.append((k, o, len(ids), t.replace('？', '\\l')))
    return L


def main():
    rows = [('K',) + r for r in disc('K')] + [('F',) + r for r in disc('F')]
    bad = [r for r in rows if '〓' in r[4]]
    print('줄', len(rows), '글자', sum(r[3] for r in rows), '범위 넘은 번호', len(bad), [(r[0], r[1], hex(r[2])) for r in bad[:6]])
    print(collections.Counter(r[0] for r in rows), '시나리오', len({(r[0], r[1]) for r in rows}))
    uniq = collections.OrderedDict()
    for r in rows: uniq.setdefault(r[4], []).append(r)
    print('고유 줄', len(uniq), '글자', sum(len(t) for t in uniq), '「？」 남음', sum('？' in t for t in uniq))
    print([t for t in uniq if t.startswith('自国司令部')][:14])
    if '--write' not in sys.argv: return
    H = '#번호\t구분\t글자수\t쓰임\tJP\tKO\n'
    body = []; pos = []
    for i, (t, rs) in enumerate(uniq.items(), 1):
        k = '%05d' % i; g = ''.join(sorted({r[0] for r in rs})); body.append('%s\t%s\t%d\t%d\t%s\t\n' % (k, g, len(t.replace('\\l', '')), len(rs), t))
        for r in rs: pos.append('%s\t%s\t%d\t%06X\t%d\n' % (k, r[0], r[1], r[2], r[3]))
    open('work/text/master.tsv', 'w', encoding='utf-8', newline='\n').write(H + ''.join(body))
    open('work/text/master_pos.tsv', 'w', encoding='utf-8', newline='\n').write('#번호\t디스크\t구역\t위치\t길이\n' + ''.join(pos))
    chunks = []; cur = []; n = len(H.encode())
    for l in body:
        b = len(l.encode())
        if n + b > SPLIT: chunks.append(cur); cur = []; n = len(H.encode())
        cur.append(l); n += b
    if cur: chunks.append(cur)
    os.makedirs('my files/tsv', exist_ok=True)
    for f in glob.glob('my files/tsv/wad_*.tsv'): os.remove(f)
    for i, c in enumerate(chunks, 1):
        open('my files/tsv/wad_%03d.tsv' % i, 'w', encoding='utf-8', newline='\n').write(H + ''.join(c))
    tot = sum(len(c) for c in chunks); assert tot == len(body)
    print('파일', len(chunks), '줄', tot, '가장 큰', max(os.path.getsize(f) for f in glob.glob('my files/tsv/wad_*.tsv')))


if __name__ == '__main__':
    main()
