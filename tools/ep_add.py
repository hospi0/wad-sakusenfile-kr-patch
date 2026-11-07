# -*- coding: utf-8 -*-
"""작전파일 엔딩(ENDING.BIN 0x451C~, 글꼴 ENDFONT0/1, 줄당 17칸) → wad_010 뒤에 덧붙임."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
L = ['激戦の末、遂にベルリンを解放。', '一陣の薫風とともに、国会議事堂に', '我が国旗が翻った。', 'ヒトラーの自殺により、', 'ドイツ国内も、', '降伏に向かって動き出し、', '戦乱の街は、再び静寂を取り戻す。', '社会主義の勝利と、', '掴んだ威光の輝きの中で、', '静かに「鋼鉄の時代」は幕を閉じる。',
     '１年半に渡る戦いに終わりがようや', 'く訪れた。我が国も他の国も多くの命', 'を失った。', '世界はこの戦乱による傷跡を何年も', '引きずるであろう。', '復興の後には永遠の平和は訪れるので', 'あろうか？', '復興は国民の戦勝酔いをさますこと', 'から始まる。', 'その成否によって、我が国の正義が世', '界に認められるのである。']
p = 'work/text/ending.tsv'; R = open(p, encoding='utf-8').read().rstrip('\n').split('\n')
assert not any('激戦の末' in r for r in R)
n = int(R[-1].split('\t')[0])
body = ['%05d\tE_SF_%d\t17\t1\t%s\t' % (n + i, 0 if i <= 10 else 1, t) for i, t in enumerate(L, 1)]
for q in (p, 'my files/tsv/wad_010.tsv'): open(q, 'w', encoding='utf-8', newline='\n').write('\n'.join(R + body) + '\n')
print(n + len(L))
