"""Rasterize generated SVG scenes to WebP using headless Chrome + Pillow."""
import os, re, subprocess, pathlib
from PIL import Image

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUT = os.path.join('assets', 'generated')
TMP = os.environ.get('TEMP', '.')

names = ['flow-cover-hero', 'flow-problem-shelf', 'flow-data-pipeline',
         'flow-size-comparison', 'flow-soup-vs-stir', 'flow-closing']

for n in names:
    svg = os.path.join(OUT, n + '.svg')
    txt = open(svg, encoding='utf-8').read()
    m = re.search(r'viewBox="0 0 (\d+) (\d+)"', txt)
    w, h = int(m.group(1)), int(m.group(2))
    png = os.path.join(TMP, n + '.png')
    url = pathlib.Path(svg).resolve().as_uri()
    cmd = [CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars',
           '--default-background-color=00000000', '--force-device-scale-factor=1',
           f'--window-size={w},{h}', '--timeout=8000', f'--screenshot={png}', url]
    subprocess.run(cmd, capture_output=True)
    im = Image.open(png).convert('RGBA')
    im = im.crop((0, 0, min(w, im.width), min(h, im.height)))
    webp = os.path.join(OUT, n + '.webp')
    im.save(webp, 'WEBP', quality=86, method=6)
    print('webp', n, im.size, os.path.getsize(webp))
