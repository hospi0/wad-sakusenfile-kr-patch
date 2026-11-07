# -*- coding: utf-8 -*-
"""화면 문구가 디스크·스테이트 메모리 어디에 있는지(읽기 전용).  python tools/probe.py"""
import sys, os, re, collections, glob, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso9660 import Iso
import state as ST
sys.stdout.reconfigure(encoding='utf-8')
R = r'C:\claude\roms\ss\World Advanced Daisenryaku\World Advanced Daisenryaku - Koutetsu no Senpuu (Japan) (Rev A) (10M)'
iso = Iso(glob.glob(R + r'\*(Track 1).bin')[0])
fs = iso.walk()
W = ['移動後不可能なコマンド', 'どちらにセーブしますか', 'フランス侵攻作戦', '本作戦は', '宣戦布告', '作戦情報', 'ゲームを続行', '記録をセーブ', '勝利条件', '全敵司令部', '急降下爆撃機', '開発表', '生産表',
     'ゲーム・セレクト', 'カートリッジ', 'ベルサイユ条約', 'ドイツ帝国', '天候', '部隊表示']
pats = {}
for t in W:
    for enc in ('cp932', 'euc_jp', 'utf-16-be'):
        pats[t.encode(enc)] = (t, enc)
hit = collections.defaultdict(collections.Counter); head = collections.Counter(); data = {}
for f in fs:
    if f[0].endswith(('.CPK', '.MUS')): continue
    try: d = iso.read(f[1], f[2])
    except EOFError: continue
    data[f[0]] = d
    head[(f[0].rsplit('/', 2)[-2] if f[0].count('/') > 1 else '', d[:4].hex())] += 1
    for b, k in pats.items():
        n = d.count(b)
        if n: hit[k][f[0]] += n
print('디스크')
for k in pats.values():
    if hit[k]: print(' ', k, sum(hit[k].values()), hit[k].most_common(3))
print('없는 문구', [t for t in W if not any(k[0] == t and hit[k] for k in hit)])
print(head.most_common(24))
print([n for n in dir(ST) if not n.startswith('_')])
print('SENSHI', data['/SENSHI.TXT'][:120].decode('cp932', 'replace').replace('\r\n', '|'))
print('README', data['/README.TXT'][:300].decode('cp932', 'replace').replace('\r\n', '|'))
print('DAI_TXT', len(data['/DAI_TXT.DC']), data['/DAI_TXT.DC'][:48].hex(' '))
print([f[0] for f in fs if f[0].count('/') == 1 and not f[0].endswith(('.CPK', '.MUS'))][:60])
print('큰 BIN', sorted(((f[2], f[0]) for f in fs if f[0].endswith('.BIN')), reverse=True)[:14])
