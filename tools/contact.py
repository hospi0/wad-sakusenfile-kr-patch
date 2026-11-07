# -*- coding: utf-8 -*-
"""받은 스샷 모아 보기. python tools/contact.py"""
import glob, os
from PIL import Image, ImageDraw
fs = sorted(glob.glob('work/states/*.png'), key=lambda p: (len(p), p)) + sorted(glob.glob('work/states2/*.png'), key=lambda p: (len(p), p)) + sorted(glob.glob('work/states_sf/*.png'))
print(len(fs)); W = 5; CW, CH = 320, 240; per = 20
for s in range(0, len(fs), per):
    pg = Image.new('RGB', (W * CW, ((min(per, len(fs) - s) + W - 1) // W) * CH), (0, 0, 0)); d = ImageDraw.Draw(pg)
    for j, f in enumerate(fs[s:s + per]):
        im = Image.open(f).convert('RGB').resize((CW - 4, CH - 4)); x, y = j % W * CW, j // W * CH; pg.paste(im, (x, y))
        d.rectangle((x, y, x + 70, y + 12), fill=(0, 0, 0)); d.text((x + 2, y), os.path.basename(os.path.dirname(f))[-6:] + '/' + os.path.basename(f)[:-4], fill=(255, 255, 0))
    pg.save('work/view/contact_%d.png' % (s // per))
