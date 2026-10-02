import re

p = 'index.html'
s = open(p, encoding='utf-8').read()

def rep(m):
    cid, h = m.group(1), m.group(2)
    return '<div class="chart-box" style="height:%spx"><canvas id="%s"></canvas></div>' % (h, cid)

s2, n = re.subn(r'<canvas id="(chart\w+)" height="(\d+)"></canvas>', rep, s)
open(p, 'w', encoding='utf-8').write(s2)
print('wrapped canvases:', n)
