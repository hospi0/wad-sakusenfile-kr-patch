# -*- coding: utf-8 -*-
"""Beetle Saturn 스테이트 변수 표(읽기 전용). 섹션 = 32 B 이름 + u32 크기, 변수 = 길이 바이트 + 이름 + u32 크기.
  from mstate import load; v = load(path); v['VDP1/VRAM'] …   python tools/mstate.py 파일"""
import sys, os, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import state as ST


def raw(path):
    return bytes(ST.unrzip(open(path, 'rb').read()))


def load(path):
    s = raw(path)
    o = s.find(b'MDFNSVST')
    p = 12 if o < 0 else o + 32
    if s[:7] == b'RASTATE':
        # RASTATE: 'MEM ' + u32 크기 뒤가 Mednafen 몸통
        q = s.find(b'MEM ') + 8
        p = q + 32 if s[q:q + 8] == b'MDFNSVST' else q
    out = {}
    n = len(s)
    while p + 36 <= n:
        name = s[p:p + 32].split(b'\0')[0]
        sz = struct.unpack_from('<I', s, p + 32)[0] & 0x7FFFFFFF
        if not name or not all(32 <= c < 127 for c in name) or sz > n: break
        b = p + 36; e = b + sz; q = b
        while q < e:
            L = s[q]; nm = s[q + 1:q + 1 + L]
            if q + 1 + L + 4 > e: break
            vs = struct.unpack_from('<I', s, q + 1 + L)[0]
            out[name.decode() + '/' + nm.decode('latin1')] = (q + 5 + L, vs)
            q += 5 + L + vs
        p = e
    return s, out


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    s, v = load(sys.argv[1]); print(len(s), s[:48], len(v))
    big = sorted(((x[1], k) for k, x in v.items()), reverse=True)[:24]
    print(big)
    print([k for k in v if 'VDP' in k][:40])
