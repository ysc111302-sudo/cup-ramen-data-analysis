"""Generate style-consistent editorial illustration assets (SVG) for the deck.

Output: assets/generated/flow-*.svg  (later rasterized to .webp)
"""
import os

OUT = os.path.join('assets', 'generated')
os.makedirs(OUT, exist_ok=True)

WARM = '#FDF6EC'; MUTED = '#C9B6A4'
RED = '#E23B2E'; RED2 = '#FF5A3C'; ORANGE = '#F7A531'; YELLOW = '#FFD166'
TEAL = '#2A9D8F'; GREEN = '#8AC926'

def defs():
    return f'''
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#241812"/><stop offset="1" stop-color="#140d0a"/>
    </linearGradient>
    <radialGradient id="glowA" cx="22%" cy="20%" r="55%">
      <stop offset="0" stop-color="{RED}" stop-opacity="0.30"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glowB" cx="82%" cy="82%" r="55%">
      <stop offset="0" stop-color="{ORANGE}" stop-opacity="0.26"/><stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="cupA" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{ORANGE}"/><stop offset="0.55" stop-color="{RED}"/><stop offset="1" stop-color="#9E171A"/>
    </linearGradient>
    <linearGradient id="cupB" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{YELLOW}"/><stop offset="0.55" stop-color="{ORANGE}"/><stop offset="1" stop-color="#B2191C"/>
    </linearGradient>
    <linearGradient id="cupC" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#57C6B8"/><stop offset="0.6" stop-color="{TEAL}"/><stop offset="1" stop-color="#14655C"/>
    </linearGradient>
    <linearGradient id="lid" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#FFE8B0"/><stop offset="1" stop-color="{YELLOW}"/>
    </linearGradient>
    <pattern id="dots" width="42" height="42" patternUnits="userSpaceOnUse">
      <circle cx="3" cy="3" r="2.4" fill="#FFFFFF" opacity="0.05"/>
    </pattern>
    <filter id="soft" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="16" stdDeviation="22" flood-color="#000000" flood-opacity="0.45"/>
    </filter>
  </defs>'''

def bg_rect(w, h):
    return (f'<rect width="{w}" height="{h}" fill="url(#bg)"/>'
            f'<rect width="{w}" height="{h}" fill="url(#dots)"/>'
            f'<rect width="{w}" height="{h}" fill="url(#glowA)"/>'
            f'<rect width="{w}" height="{h}" fill="url(#glowB)"/>')

def steam(x, y, s=1.0, op=0.85):
    return (f'<g transform="translate({x},{y}) scale({s})" stroke="{WARM}" stroke-width="12" '
            f'stroke-linecap="round" fill="none" opacity="{op}">'
            f'<path d="M-60 0 C-90 -45 -20 -60 -50 -110"/>'
            f'<path d="M20 6 C-10 -40 60 -55 30 -110"/>'
            f'<path d="M100 0 C70 -45 140 -60 110 -110"/></g>')

def cup(x, y, s=1.0, grad='cupA', rot=0, noodles=True):
    n = ''
    if noodles:
        n = (f'<g stroke="{YELLOW}" stroke-width="13" stroke-linecap="round" fill="none" opacity="0.95">'
             f'<path d="M-80 130 q60 -55 120 0 q60 55 120 0"/>'
             f'<path d="M-80 180 q60 -55 120 0 q60 55 120 0"/>'
             f'<path d="M-70 230 q55 -48 110 0 q55 48 110 0"/></g>')
    return (f'<g transform="translate({x},{y}) rotate({rot}) scale({s})" filter="url(#soft)">'
            f'<path d="M-150 40 L150 40 L116 300 Q113 322 90 322 L-90 322 Q-113 322 -116 300 Z" fill="url(#{grad})"/>'
            f'<rect x="-150" y="18" width="300" height="52" rx="14" fill="{WARM}" opacity="0.92"/>'
            f'<rect x="-104" y="120" width="208" height="120" rx="26" fill="{WARM}" opacity="0.16"/>'
            f'{n}'
            f'<ellipse cx="0" cy="40" rx="164" ry="30" fill="url(#lid)"/>'
            f'<ellipse cx="0" cy="40" rx="164" ry="30" fill="none" stroke="#B2191C" stroke-opacity="0.25" stroke-width="4"/>'
            f'</g>')

def card(x, y, w, h, op=0.9):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" fill="#2b1d16" opacity="{op}" stroke="#ffffff" stroke-opacity="0.10"/>'

def crawler(cx, cy):
    legs = ''.join(
        f'<path d="M{cx+dx*30} {cy+dy*18} L{cx+dx*74} {cy+dy*66}" stroke="{RED}" stroke-width="9" stroke-linecap="round"/>'
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 0), (1, 1)])
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="42" ry="34" fill="{RED}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="13" fill="{WARM}"/>' + legs)

def db(cx, cy):
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="86" ry="26" fill="{GREEN}"/>'
            f'<path d="M{cx-86} {cy} v70 a86 26 0 0 0 172 0 v-70" fill="{GREEN}" opacity="0.85"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="86" ry="26" fill="none" stroke="#0f0f0f" stroke-opacity="0.15" stroke-width="3"/>'
            f'<path d="M{cx-86} {cy+40} h172" stroke="#0f0f0f" stroke-opacity="0.15" stroke-width="3"/>')

def tag(cx, cy):
    return (card(cx - 90, cy, 180, 70, op=0.9)
            + f'<circle cx="{cx-42}" cy="{cy+35}" r="15" fill="{YELLOW}"/>'
            + f'<rect x="{cx-12}" y="{cy+24}" width="82" height="22" rx="7" fill="{MUTED}" opacity="0.7"/>')

def write(name, w, h, body):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
           f'{defs()}{bg_rect(w,h)}{body}</svg>')
    open(os.path.join(OUT, name), 'w', encoding='utf-8').write(svg)
    print('wrote', name, len(svg))

# 1. COVER HERO ---------------------------------------------------------------
def scene_cover():
    w, h = 1600, 1000
    b = []
    # left third intentionally clean/dark for the title text
    # right: floating data cards
    b.append(card(1330, 150, 250, 200))
    b.append(''.join(f'<rect x="{1362+i*50}" y="{330-v}" width="36" height="{v}" rx="8" fill="{YELLOW if i%2 else ORANGE}"/>'
                     for i, v in enumerate([70, 130, 95, 165])))
    b.append(f'<path d="M1370 300 L1560 215" stroke="{TEAL}" stroke-width="5" fill="none" stroke-dasharray="8 8"/>')
    b.append(''.join(f'<circle cx="{1370+i*62}" cy="{300-(i*i*8)}" r="8" fill="{TEAL}"/>' for i in range(4)))
    b.append(card(1370, 620, 230, 200))
    b.append(''.join(f'<circle cx="{1412+(i%3)*72}" cy="{680+(i//3)*52}" r="10" fill="{RED if i%3==0 else ORANGE}" opacity="0.95"/>'
                     for i in range(9)))
    # cups (center-right)
    b.append(steam(990, 200, 1.25))
    b.append(cup(800, 600, 0.9, 'cupC', rot=-4))
    b.append(cup(990, 520, 1.25, 'cupA'))
    b.append(cup(1170, 640, 0.85, 'cupB', rot=5))
    # chopsticks (far right)
    b.append(f'<g transform="rotate(16 1560 300)">'
             f'<rect x="1520" y="40" width="22" height="470" rx="11" fill="#8B5E3C"/>'
             f'<rect x="1570" y="40" width="22" height="470" rx="11" fill="#A9744F"/></g>')
    return write('flow-cover-hero.svg', w, h, ''.join(b))

# 2. PROBLEM: convenience shelf ----------------------------------------------
def scene_shelf():
    w, h = 1400, 1000
    b = []
    # shelves
    for sy in (470, 780):
        b.append(f'<rect x="90" y="{sy}" width="1220" height="22" rx="8" fill="#3a281f"/>')
        b.append(f'<rect x="90" y="{sy}" width="1220" height="8" rx="4" fill="#5a3f2f"/>')
    # cups on shelves (varying sizes)
    sizes = [0.62, 0.82, 0.58, 0.94, 0.70]
    cols = ['cupB', 'cupA', 'cupC', 'cupA', 'cupB']
    x = 190
    for i in range(5):
        s = sizes[i]
        b.append(cup(x, 470 - 300 * s - 20, s, cols[i]))
        x += 235
    x = 220
    for i in range(4):
        s = [0.75, 0.60, 0.88, 0.66][i]
        b.append(cup(x, 780 - 300 * s - 20, s, cols[(i + 2) % 5]))
        x += 285
    # price tags / data sparklines above each cup
    for (px, py) in [(210, 150), (450, 120), (690, 160), (930, 110), (1160, 150)]:
        b.append(card(px, py, 150, 96, op=0.85))
        b.append(f'<path d="M{px+18} {py+72} l30 -22 l28 12 l32 -34 l24 10" stroke="{TEAL}" stroke-width="4" fill="none"/>')
        b.append(f'<text x="{px+20}" y="{py+34}" font-family="Arial" font-size="30" fill="{YELLOW}">?</text>')
    return write('flow-problem-shelf.svg', w, h, ''.join(b))

# 3. DATA PIPELINE -----------------------------------------------------------
def scene_pipeline():
    w, h = 1600, 900
    b = []
    def chrome(x):
        return (f'<rect x="{x+30}" y="330" width="280" height="40" rx="10" fill="#3a281f"/>'
                + ''.join(f'<circle cx="{x+52+i*34}" cy="350" r="6" fill="{MUTED}" opacity="0.6"/>' for i in range(3)))
    def panel(x):
        return card(x, 300, 340, 300) + chrome(x)
    x1 = 130
    b.append(panel(x1))
    b.append(f'<rect x="{x1+55}" y="420" width="230" height="150" rx="12" fill="#241a15" stroke="{MUTED}" stroke-opacity="0.4"/>'
             f'<path d="M{x1+55} 458 h230" stroke="{MUTED}" stroke-opacity="0.4"/>')
    b.append(''.join(f'<rect x="{x1+80+i*52}" y="486" width="38" height="58" rx="6" fill="{ORANGE}" opacity="{0.55+i*0.12:.2f}"/>' for i in range(4)))
    b.append(f'<path d="M500 470 h90" stroke="{ORANGE}" stroke-width="11" stroke-linecap="round"/>'
             f'<path d="M580 445 l40 25 l-40 25 Z" fill="{ORANGE}"/>')
    x2 = 620
    b.append(panel(x2)); b.append(crawler(790, 500))
    b.append(f'<path d="M990 470 h90" stroke="{TEAL}" stroke-width="11" stroke-linecap="round"/>'
             f'<path d="M1070 445 l40 25 l-40 25 Z" fill="{TEAL}"/>')
    for i in range(4):
        b.append(f'<circle cx="{1002+i*22}" cy="{432}" r="5" fill="{YELLOW}" opacity="0.9"/>')
    x3 = 1110
    b.append(panel(x3)); b.append(db(1280, 470))
    return write('flow-data-pipeline.svg', w, h, ''.join(b))

# 4. SIZE COMPARISON ---------------------------------------------------------
def scene_size():
    w, h = 1400, 820
    b = []
    # small cup (left) / big cup (right)
    b.append(cup(370, 520, 0.52, 'cupB'))
    b.append(cup(1010, 420, 1.05, 'cupA'))
    # size measurement arrows below each cup
    b.append(f'<path d="M292 700 H448" stroke="{TEAL}" stroke-width="7" stroke-linecap="round"/>'
             f'<path d="M292 678 v44 M448 678 v44" stroke="{TEAL}" stroke-width="7" stroke-linecap="round"/>')
    b.append(f'<path d="M828 792 H1192" stroke="{ORANGE}" stroke-width="7" stroke-linecap="round"/>'
             f'<path d="M828 770 v44 M1192 770 v44" stroke="{ORANGE}" stroke-width="7" stroke-linecap="round"/>')
    # identical price tags (same price, different size)
    b.append(tag(370, 150)); b.append(tag(1010, 150))
    return write('flow-size-comparison.svg', w, h, ''.join(b))

# 5. SOUP VS STIR-FRIED ------------------------------------------------------
def scene_soup_stir():
    w, h = 1600, 900
    b = []
    # divider
    b.append(f'<rect x="798" y="150" width="4" height="600" rx="2" fill="#ffffff" opacity="0.14"/>')
    # left: soup (steam + broth surface)
    b.append(cup(380, 470, 1.0, 'cupC'))
    b.append(f'<ellipse cx="380" cy="510" rx="150" ry="44" fill="{TEAL}" opacity="0.45"/>')
    b.append(steam(380, 150, 1.0))
    # right: stir-fried (wok + swirl)
    b.append(cup(1220, 470, 1.0, 'cupA'))
    b.append(f'<g transform="translate(1220,250)">'
             + ''.join(f'<path d="M{-60+i*60} 110 q30 -70 0 -120" stroke="{RED2 if i%2 else ORANGE}" stroke-width="13" '
                       f'stroke-linecap="round" fill="none" opacity="0.9"/>' for i in range(3))
             + f'<path d="M-150 122 q150 -72 300 0 Z" fill="{ORANGE}" opacity="0.9"/></g>')
    # small category glyphs (bowl vs wok)
    b.append(f'<path d="M320 150 a60 40 0 0 0 120 0 Z" fill="{TEAL}"/>')
    b.append(f'<path d="M1160 140 a60 26 0 0 0 120 0 Z" fill="{ORANGE}"/>')
    return write('flow-soup-vs-stir.svg', w, h, ''.join(b))

# 6. CLOSING -----------------------------------------------------------------
def scene_closing():
    w, h = 1600, 1000
    b = []
    # scatter motif
    b.append(card(120, 140, 520, 300))
    b.append(''.join(f'<circle cx="{170+ (i*53)%470}" cy="{300- ((i*71)%190)}" r="9" fill="{RED if i%3==0 else ORANGE}"/>' for i in range(14)))
    b.append(f'<path d="M170 250 L600 180" stroke="{WARM}" stroke-opacity="0.5" stroke-width="3" stroke-dasharray="8 8"/>')
    # bar motif
    b.append(card(980, 140, 500, 300))
    b.append(''.join(f'<rect x="{1030+i*90}" y="{380-v}" width="52" height="{v}" rx="8" fill="{TEAL if i%2 else ORANGE}"/>'
                     for i, v in enumerate([90, 150, 120, 190])))
    # cups cluster
    b.append(cup(430, 600, 0.9, 'cupB', rot=-4))
    b.append(cup(720, 555, 1.12, 'cupA'))
    b.append(steam(720, 220, 1.2))
    b.append(cup(1010, 600, 0.9, 'cupC', rot=4))
    # up arrow motif (between the two cards)
    b.append(f'<path d="M690 430 L760 350 L830 430" stroke="{GREEN}" stroke-width="12" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    return write('flow-closing.svg', w, h, ''.join(b))

scene_cover()
scene_shelf()
scene_pipeline()
scene_size()
scene_soup_stir()
scene_closing()
print('assets generated')
