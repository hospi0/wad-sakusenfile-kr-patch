# -*- coding: utf-8 -*-
"""자리표(ui_pos)에 없던 16×16 문자열·사본(2026-11-07 실기 지적으로 전수).  제자리, 원문 칸 안.
   FIX = 번역표 덮어쓰기(말풍선 칸 맞춤·하스피 지시)."""
import sys, os, struct, itertools, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asc_table as T

ROWS = [  # (원문, 번역, 파일)
    ('セーブ', '저장', '/GAME2.BIN'),                    # 말풍선 0x1A02E + 저장 창 제목
    ('A・・次の部隊　C・・部隊移動', 'A··다음 부대 C··이동', '/GAME2.BIN'),
    ('配置数', '배치수', '/GAME2.BIN'),
    ('進化改良表', '진화개량표', '/GAME2.BIN'),
    ('状況', '상황', '/GAME2.BIN'),
    ('部隊表', '부대표', '/GAME2.BIN'),
    ('開発表', '개발표', '/GAME2.BIN'),
    ('部隊', '부대', '/GAME2.BIN'),
    ('処分', '처분', '/GAME2.BIN'),
    ('生産表', '생산표', '/GAME2.BIN'),
    ('爆撃機', '폭격기', '/GAME2.BIN'),
    ('どちらにセーブしますか?', '어디에 저장할까요?', '/GAME2.BIN'),
    ('どちらからロードしますか?', '어디서 불러올까요?', '/GAME2.BIN'),
    ('本体RAM', '본체RAM', '/GAME2.BIN'),
    ('カートリッジRAM', '카트리지RAM', '/GAME2.BIN'),
    ('空き容量が不足しているため、記録は', '빈 용량이 부족하여 기록은', '/GAME2.BIN'),
    ('ゲームを続行しますか?', '게임을 계속할까요?', '/GAME2.BIN'),
    ('ゲームの記録を保存中です。', '기록을 저장 중입니다.', '/GAME2.BIN'),
    ('ゲームの記録をロード中です。', '기록을 불러오는 중입니다.', '/GAME2.BIN'),
    ('記録をロードしますか?', '기록을 불러올까요?', '/GAME2.BIN'),
    ('ロード', '로드', '/GAME2.BIN'),
    ('新しい記録を保存するための空き容量が', '새 기록을 저장할 빈 용량이', '/GAME2.BIN'),
    ('セーブされた記録がありません', '저장된 기록이 없습니다', '/GAME2.BIN'),
    ('設定変更', '설정변경', '/GAME2.BIN'),
    ('システム', '시스템', '/GAME2.BIN'),
    ('サウンド', '사운드', '/GAME2.BIN'),
    ('操　作', '조　작', '/GAME2.BIN'),
    ('その他', '기타', '/GAME2.BIN'),
    ('の勝利です。', '승리입니다.', '/GAMEOVER.BIN'),
    ('第20軍', '20군', '/00000000.BIN'),
    ('第19軍', '19군', '/00000000.BIN'),
    ('第38軍', '38군', '/00000000.BIN'),
    ('第64軍', '64군', '/00000000.BIN'),
    ('第62軍', '62군', '/00000000.BIN'),
    ('第15軍', '15군', '/00000000.BIN'),
    ('第31軍', '31군', '/00000000.BIN'),
    ('第35軍', '35군', '/00000000.BIN'),
    ('第32軍', '32군', '/00000000.BIN'),
    ('第18軍', '18군', '/00000000.BIN'),
    ('第36軍', '36군', '/00000000.BIN'),
    ('第6SS装甲軍', '6SS 기갑군', '/00000000.BIN'),
    ('あなたの司令部は破壊され、', '아군 사령부가 파괴되어,', '/GAMEOVER.BIN'),
    ('上書きしますか?', '덮어쓸까요?', '/GAME2.BIN'),
    ('シナリオデパッガー', '시나리오 디버거', '/00000000.BIN'),
    ('デパッグ用', '디버그용', '/00000000.BIN'),
    ('スタンダードモード', '스탠다드 모드', '/00000000.BIN'),
    ('キャンペーンモード', '캠페인 모드', '/00000000.BIN'),
    ('08\u3000モスクワ4Pz', '08\u3000모스크바 4Pz', '/00000000.BIN'),
    ('09\u3000モスクワ2Pz', '09\u3000모스크바 2Pz', '/00000000.BIN'),
    ('10\u3000コーカサス', '10\u3000코카서스', '/00000000.BIN'),
    ('16\u3000ファレーズ', '16\u3000팔레즈', '/00000000.BIN'),
    ('23\u3000マレー', '23\u3000말레이', '/00000000.BIN'),
    ('25\u3000MO作戦', '25\u3000MO 작전', '/00000000.BIN'),
    ('26\u3000MI作戦', '26\u3000MI 작전', '/00000000.BIN'),
    ('33\u3000インパール', '33\u3000임팔', '/00000000.BIN'),
    ('38\u3000沖縄IJN', '38\u3000오키나와IJN', '/00000000.BIN'),
    ('39\u3000沖縄32Army', '39\u3000오키나와32군', '/00000000.BIN'),
    ('53\u3000沖縄', '53\u3000오키나와', '/00000000.BIN'),
]
FIX = {'00645': '잔　　부대', '00608': '간접 무기는 이동 후 불가', '00721': '아군 사령부가 적에게 점령돼,', '00709': '현재의 메인설정', '00713': '전투영상', '00548': '총보급', '00549': '다음', '00551': '설정', '00580': '사고중'}


def rows(d_of, have, spans={}):
    """d_of(fn) = 원본 바이트, have[fn] = 이미 있는 위치. → [(fn, off, 칸, 번역)], 못 찾은 원문."""
    S = T.SHEET; inv = collections.defaultdict(list)
    for i, c in enumerate(S): inv[c].append(i + 2 if i >= 562 else i)
    inv['　'] = [0]
    out = []; miss = []
    for jp, ko, fn in ROWS:
        d = d_of(fn); found = False
        cand = [inv[c][:3] for c in jp]
        if not all(cand): miss.append(jp); continue
        for cb in itertools.product(*cand):
            b = struct.pack('>%dH' % len(jp), *cb); q = -1
            while True:
                q = d.find(b, q + 1)
                if q < 0: break
                nx = d[q + len(b):q + len(b) + 2]
                if q % 2 or not (nx == bytes([255, 255]) or (jp in ZERO_END and nx == bytes(2))): continue
                found = True
                if q in have.get(fn, ()) or any(p <= q < p + 2 * n + 2 for p, n in spans.get(fn, ())): continue
                # 앞에 다른 글자가 붙은 조각(セーブ終了 뒤쪽 등) 제외: 앞 워드가 글자(1~1190)이고 표지·빈칸이 아니면 넘김. 단 포인터 뒤 문자열은 앞 워드가 큰 값
                pv = struct.unpack_from('>H', d, q - 2)[0] if q >= 2 else 0xFFFF
                if 0 < pv < 1190 and jp not in KEEP_AFTER_TEXT: continue
                out.append((fn, q, len(jp), ko))
        if not found: miss.append(jp)
    return out, miss


ZERO_END = {'システム', 'サウンド', '操　作', 'その他'} | {r[0] for r in ROWS if r[2] == '/00000000.BIN'}   # 뒤가 빈칸 채움
# 앞 워드가 글자처럼 보여도(포인터 하위 워드·칸 번호) 실제 독립 문자열인 것
KEEP_AFTER_TEXT = {r[0] for r in ROWS if r[2] == '/00000000.BIN'} | {'あなたの司令部は破壊され、', '上書きしますか?', 'ゲームを続行しますか?', 'どちらにセーブしますか?', 'どちらからロードしますか?', '空き容量が不足しているため、記録は', 'ゲームの記録を保存中です。', 'ゲームの記録をロード中です。',
                   '記録をロードしますか?', '新しい記録を保存するための空き容量が', 'セーブされた記録がありません', 'ロード', 'セーブ', '設定変更', '爆撃機', 'の勝利です。', '配置数', '進化改良表', '状況', 'システム', 'サウンド', '操　作', 'その他'}


AUTO_FILES = ('/GAME2.BIN', '/00000000.BIN', '/GAMEOVER.BIN', '/GMS2.BIN', '/GMS1.BIN', '/SHINHEI.BIN')


def auto_rows(d_of, files, have, spans, k, drop):
    """ui.tsv 번역이 있는 줄(2자 이상)을 파일 전체에서: 뒤가 FFFF, 앞이 글자 아님. 잡음 번호는 뺌."""
    S = T.SHEET; inv = collections.defaultdict(list)
    for i, c in enumerate(S): inv[c].append(i + 2 if i >= 562 else i)
    inv['　'] = [0]
    out = []
    for l in open('work/text/ui.tsv', encoding='utf-8'):
        if l[0] == '#': continue
        p = l.rstrip('\n').split('\t')
        i, t = p[0], p[4]
        if i not in k or i in drop or len(t) < 2 or any(not inv[c] for c in t): continue
        v = FIX.get(i, k[i][0][5])
        for cb in itertools.islice(itertools.product(*[inv[c][:2] for c in t]), 8):
            b = struct.pack('>%dH' % len(t), *cb) + bytes([255, 255])
            for fn in files:
                d = d_of(fn); q = -1
                while True:
                    q = d.find(b, q + 1)
                    if q < 0: break
                    if q % 2 or q in have.get(fn, ()) or any(a <= q < a + 2 * n + 2 for a, n in spans.get(fn, ())): continue
                    pv = struct.unpack_from('>H', d, q - 2)[0] if q >= 2 else 0xFFFF
                    if 0 < pv < 1190 and len(t) < 4: continue          # 짧은 낱말은 앞이 글자면 조각
                    out.append((fn, q, len(t), v)); spans.setdefault(fn, []).append((q, len(t)))
    return out
