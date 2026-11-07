# -*- coding: utf-8 -*-
"""UI 문자열 걸러 TSV 로(스태프 제외). python tools/ui_tsv.py [--write]"""
import sys, os, re, collections, glob
sys.stdout.reconfigure(encoding='utf-8')
KEEP = {'/00000000.BIN', '/GAME2.BIN', '/GAMEOVER.BIN', '/GMS1.BIN', '/KASOU.BIN', '/ENDING.BIN', '/DEMO3D.BIN', '/SHINHEI.BIN', '/UNITDATA.BIN', '/RMC2.BIN'}
JP = re.compile('[ぁ-ヶ一-龥]')
NOISE = re.compile('済特|正特|正存|正ん|正済|春も末保|盟んん|容済|収収|収　|艇　|[a-zA-Z0-9=㎜]|^.*\.|□ウ|ブロ|セド|上陸発|^拡大$|撃了|解装|小セ|ブ設|況作|置中止決|キャペ|不　現|航部ド|吹急|洋巡|状　')
rows = [l.rstrip('\n').split('\t') for l in open('work/text/ui_raw.tsv', encoding='utf-8')]
U = collections.OrderedDict(); drop = 0
for tag, fn, o, n, t in rows:
    j = len(JP.findall(t)); plain = len(t.replace('　', ''))
    if fn not in KEEP or j < 2 or j / plain < 0.6 or 'PP' in t: drop += 1; continue
    if fn != '/00000000.BIN' and NOISE.search(t): drop += 1; continue
    U.setdefault(t, []).append((tag, fn, o, n))
print('남은 고유', len(U), '글자', sum(len(t) for t in U), '버림', drop, '□', sum('□' in t for t in U))
c = collections.Counter(r[1] for v in U.values() for r in v); print(c.most_common())
import random; random.seed(3); print(random.sample(list(U), 36))
if '--write' in sys.argv:
    n0 = sum(1 for l in open('work/text/master.tsv', encoding='utf-8')) - 1
    H = '#번호\t구분\t글자수\t쓰임\tJP\tKO\n'; body = []; pos = []
    for i, (t, rs) in enumerate(U.items(), n0 + 1):
        k = '%05d' % i; g = 'U' + ''.join(sorted({r[0] for r in rs})); body.append('%s\t%s\t%s\t%d\t%s\t\n' % (k, g, max(int(r[3]) for r in rs), len(rs), t))
        for r in rs: pos.append('%s\t%s\t%s\t%s\t%s\n' % (k, r[0], r[1], r[2], r[3]))
    open('work/text/ui.tsv', 'w', encoding='utf-8', newline='\n').write(H + ''.join(body)); open('work/text/ui_pos.tsv', 'w', encoding='utf-8', newline='\n').write(''.join(pos))
    open('my files/tsv/wad_007.tsv', 'w', encoding='utf-8', newline='\n').write(H + ''.join(body))
    print('wad_007', os.path.getsize('my files/tsv/wad_007.tsv'))
