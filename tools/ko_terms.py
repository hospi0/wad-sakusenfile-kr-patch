# -*- coding: utf-8 -*-
"""용어·말투·조사 검사(읽기 전용).  python tools/ko_terms.py"""
import sys, os, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ko_audit as A
sys.stdout.reconfigure(encoding='utf-8')
m = A.load_master(); k, _, _ = A.load_ko()
KO = {i: k[i][0][5] for i in m}
# 1 지명·이름: wad_009 대응이 본문에 쓰였나
pl = {}
for i, c in m.items():
    if c[1] == 'P':
        j = c[4].strip('()'); o = KO[i].strip('()')
        j2 = re.sub('(ガワ|ショトウ|ハントウ|トウ|カイ|レットウ)$', '', j)
        pl[j] = o
bad = collections.Counter(); ex = {}
for i, c in m.items():
    if c[1][:1] in 'KF' or c[1][:1] == 'E':
        for j, o in pl.items():
            if len(j) >= 3 and j in c[4] and o.replace(' ', '') not in KO[i].replace(' ', ''):
                bad[(j, o)] += 1; ex.setdefault((j, o), (i, KO[i][:40]))
print('지명 불일치', len(bad))
for (j, o), n in bad.most_common(50): print(' ', j, o, n, ex[(j, o)])
# 2 핵심 낱말
T = ['わが軍', '我が軍', 'わが国', '我が国', '連合軍', '枢軸', '総統', '大統領', '皇帝', '帝国', '第三帝国', '合衆国', 'ソ連', '司令部', '部隊', '索敵', '軍事費', '補給', '占領', '撃破', '壊滅', '撤退', '戦線', '上陸', '橋頭堡', '艦隊', '機動部隊', '空母', '戦艦', '駆逐艦', '潜水艦', '戦車', '装甲', '師団', '軍団', '方面軍', '軍集団', '正面軍', '任務部隊', '海兵', '航空機', '爆撃', '大本営', '本土', '進撃', '侵攻', '敵', '休戦', '講和', 'ターン', 'ヘックス', '引き分け', '大勝', '勝利', '敗北', '経験値', '訓練値', '敵勢力', '増援部隊', '自国', '開発', '生産', 'セーブ', 'ロード', '作戦', '工事', '進化', '改良', '合流', '処分', '発進', '着艦', '変型', '武装']
CAND = {'わが軍': '아군 우리 군 우리군', '我が軍': '아군 우리 군 우리군', 'わが国': '우리나라 아국 우리 나라 아 국', '我が国': '우리나라 아국 우리 나라', '司令部': '사령부', '部隊': '부대', '索敵': '색적 탐색 정찰', 'ソ連': '소련', 'ターン': '턴', 'セーブ': '세이브 저장', 'ロード': '로드 불러오', '変型': '변형', '引き分け': '무승부 비김 무승', '大勝': '대승', '敗北': '패배', '経験値': '경험치', '訓練値': '훈련치 훈련도', '進化': '진화', '改良': '개량', '処分': '처분 폐기', '合流': '합류', '発進': '발진 출격', '着艦': '착함', '工事': '공사', '橋頭堡': '교두보', '方面軍': '방면군', '正面軍': '정면군 전선군', '軍集団': '집단군 군집단', '大本営': '대본영', '総統': '총통', '大統領': '대통령', '合衆国': '합중국 미국', '休戦': '휴전', '講和': '강화', '壊滅': '궤멸 괴멸', '撤退': '철수 퇴각 후퇴', '空母': '항공모함 공모 항모', 'ヘックス': '헥스', '任務部隊': '임무부대 기동부대 임무 부대', '第三帝国': '제3제국 제삼제국 제3 제국', '敵勢力': '적 세력 적세력'}
print('=== 낱말 분포')
for j, cs in CAND.items():
    c = collections.Counter(); n = 0
    for i, r in m.items():
        if j in r[4]:
            n += 1
            for w in cs.split():
                if w in KO[i]: c[w] += 1
    print(j, n, dict(c))
# 3 말투
print('=== 말투')
end = collections.Counter(); ex = {}
for i, c in m.items():
    if c[1][:1] in 'KF' and len(c[4]) > 30:
        for s in re.split(r'(?<=[.!?])\s*|\\l', KO[i]):
            s = s.strip()
            if len(s) < 6: continue
            e = re.sub(r'[.!?。]+$', '', s)[-2:]
            end[e] += 1; ex.setdefault(e, (i, s[-22:]))
print(end.most_common(40)); print([(e, ex[e]) for e, n in end.items() if n <= 2][:30])
# 4 조사
print('=== 조사')
def jong(ch):
    o = ord(ch) - 0xAC00
    return o % 28 if 0 <= o < 11172 else -1
J = []
for i in m:
    s = KO[i]
    for mm in re.finditer(r'([가-힣0-9a-zA-Z)）」』])(을|를|와|과|으로|로)(?=[ ,.\\…·]|$)', s):
        p, q = mm.group(1), mm.group(2); j = jong(p)
        if j < 0: continue
        if q == '을' and j == 0 or q == '를' and j > 0 or q == '와' and j > 0 or q == '과' and j == 0 or q == '로' and j not in (0, 8) or q == '으로' and j in (0, 8):
            J.append((i, s[max(0, mm.start() - 6):mm.end() + 2]))
print(len(J), J[:40])
