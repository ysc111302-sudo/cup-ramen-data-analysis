import json, re, csv, os

ROOT = 'scrape'

def read(p):
    with open(os.path.join(ROOT, p), encoding='utf-8-sig') as f:
        return f.read()

def clean(s):
    s = s.replace('\\', '')
    s = s.replace('**', '').replace('_', '')
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def num(s):
    if s is None:
        return None
    s = str(s).replace(',', '').strip()
    try:
        f = float(s)
        return int(f) if f.is_integer() else f
    except ValueError:
        return None

rows = []

# ---------------- Nongshim ----------------
nong_pat = re.compile(
    r'\*\*\[상품명\s*:(.+?)\]\((https://nongshimmall\.com/product/detail\.html\?product_no=\d+)[^)]*\)\*\*'
    r'\s*\n\s*-\s*([\d,]+)원')
seen = set()
for fn in ['nongshim.md', 'nongshim_p2.md', 'nongshim_p3.md', 'nongshim_p4.md', 'nongshim_p5.md']:
    txt = read(fn)
    prev_end = 0
    for m in nong_pat.finditer(txt):
        raw = m.group(1).strip()
        url = m.group(2)
        price = num(m.group(3))
        weight = count = None
        # weight/count live in the product thumbnail alt of the same block
        block = txt[prev_end:m.start()]
        prev_end = m.end()
        alts = re.findall(r'!\[([^\]]+)\]\(', block)
        for alt in reversed(alts):
            wm = re.search(r'\((\d+(?:\.\d+)?)\s*g\s*[*xX]\s*(\d+)\)', alt)
            if wm:
                weight, count = num(wm.group(1)), int(wm.group(2))
                break
            wm2 = re.search(r'\((\d+(?:\.\d+)?)\s*g\)', alt)
            if wm2:
                weight = num(wm2.group(1))
                break
        if weight is None:
            wm = re.search(r'(\d+(?:\.\d+)?)\s*g\s*[*xX]\s*(\d+)', raw)
            if wm:
                weight, count = num(wm.group(1)), int(wm.group(2))
        if count is None:
            cm = re.search(r'(\d+)\s*입', raw)
            count = int(cm.group(1)) if cm else None
        name = clean(re.sub(r'\(\s*\d+(?:\.\d+)?\s*g[^)]*\)', '', raw))
        key = ('농심', name, weight, count, url)
        if key in seen:
            continue
        seen.add(key)
        rows.append(dict(brand='농심', name=name, weight=weight, count=count,
                         price=price, url=url, src='농심몰'))

# ---------------- Samyang ----------------
sy_txt = read('samyang_all.md')
# map product no -> (name, price)
sy_products = {}
for m in re.finditer(r'\[(.+?)\]\((https://www\.samyangfoods\.co\.kr/goods/view\?no=(\d+))\)', sy_txt):
    label = clean(m.group(1))
    if label.startswith('!') or '](' in label or 'http' in label:
        continue
    if not ('삼양식품' in label or re.search(r'\d+\s*g', label) or '입' in label):
        continue
    no = m.group(3)
    tail = sy_txt[m.end():m.end() + 300]
    pm = re.search(r'\*\*([\d,]+)\*\*\s*₩', tail)
    price = num(pm.group(1)) if pm else None
    name = re.sub(r'^\[삼양식품\]\s*', '', label)
    if no not in sy_products or (len(name) > len(sy_products[no][0])):
        sy_products[no] = (name, price, m.group(2))

# details nutrition
sy_nut = {}
det = json.load(open(os.path.join(ROOT, 'samyang_details.json'), encoding='utf-8-sig'))
for x in det:
    md = x['markdown']
    meta = x['metadata']
    no = None
    for k in ('ogUrl', 'sourceURL', 'url'):
        if meta.get(k):
            mm = re.search(r'no=(\d+)', meta[k])
            if mm:
                no = mm.group(1)
                break
    if no is None:
        mm = re.search(r'no=(\d+)', meta.get('keywords', ''))
        no = mm.group(1) if mm else None
    nut = {}
    mm = re.search(r'([\d.]+)kcal', md)
    if mm:
        nut['kcal'] = num(mm.group(1))
    for key, pat in [('나트륨', r'나트륨\s*([\d,]+)mg'),
                     ('탄수화물', r'탄수화물\s*([\d.]+)g'),
                     ('당류', r'당류\s*([\d.]+)g'),
                     ('지방', r',\s*지방\s*([\d.]+)g'),
                     ('단백질', r'단백질\s*([\d.]+)g')]:
        mm = re.search(pat, md)
        if mm:
            nut[key] = num(mm.group(1))
    sy_nut[no] = nut

for no, (name, price, url) in sy_products.items():
    wm = re.search(r'(\d+(?:\.\d+)?)\s*g\s*[xX]\s*(\d+)\s*입', name)
    weight = num(wm.group(1)) if wm else None
    count = int(wm.group(2)) if wm else None
    base = re.sub(r'\s*\d+(?:\.\d+)?\s*g\s*[xX]\s*\d+\s*입.*$', '', name).strip()
    base = re.sub(r'\s*\(유통기한[^)]*\)', '', base).strip()
    rows.append(dict(brand='삼양', name=base, weight=weight, count=count,
                     price=price, url=url, src='삼양식품', **sy_nut.get(no, {})))

# ---------------- Paldo ----------------
pdet = json.load(open(os.path.join(ROOT, 'paldo_details.json'), encoding='utf-8-sig'))
for x in pdet:
    url = x['metadata'].get('sourceURL', '')
    md = x['markdown']
    mm = re.search(r'###\s+(.+)', md)
    if not mm:
        continue
    name = clean(re.split(r'\s_', mm.group(1))[0])
    nut = {}
    for key in ['열량', '나트륨', '탄수화물', '당류', '지방', '단백질']:
        v = re.search(r'-\s*' + key + r'\s*[:：]\s*([\d.,]+)', md)
        if v:
            nut[key] = num(v.group(1))
    if '열량' in nut:
        nut['kcal'] = nut.pop('열량')
    is_cup = ('컵' in name) or ('왕뚜껑' in name) or ('왕컵' in name) or ('갓뚜껑' in name)
    if not is_cup:
        continue
    rows.append(dict(brand='팔도', name=name, weight=None, count=None,
                     price=None, url=url, src='팔도', **nut))

# ---------------- Otoki (otokimall) ----------------
o_pat = re.compile(r'\[([^\]]+?)\]\((https://www\.otokimall\.com/front/product/(\d+))\)')
seen = set()
for fn in ['otokimall2.md', 'otokimall_p2b.md']:
    txt = read(fn)
    for m in o_pat.finditer(txt):
        text = m.group(1)
        pid = m.group(3)
        # name = first line that is not an image/thumbnail
        parts = [p.strip() for p in text.split('\n') if p.strip()]
        name = None
        for p in parts:
            if p.startswith('!['):
                continue
            name = p
            break
        if not name:
            continue
        name = clean(name)
        pm = re.search(r'([\d,]+)원', text)
        price = num(pm.group(1)) if pm else None
        if name in seen:
            continue
        seen.add(name)
        wm = re.search(r'(\d+)\s*(?:G|g)\s*[xX]?\s*(\d+)?', name)
        weight = num(wm.group(1)) if wm else None
        count = int(wm.group(2)) if (wm and wm.group(2)) else None
        url = 'https://www.otokimall.com/front/product/' + pid
        rows.append(dict(brand='오뚜기', name=name, weight=weight, count=count,
                         price=price, url=url, src='오뚜기몰'))

# ---------------- Kurly ----------------
rows.append(dict(brand='농심', name='농심 컵라면 6입 6종 (택2) 골라담기', weight=None, count=None,
                 price=6120, url='https://lounge.kurly.com/mykurlytem/3c94e7d4-4a67-4113-81b7-de8a5b6e27ae',
                 src='컬리'))

# ---------------- classify ----------------
def container(name, brand):
    if any(k in name for k in ['큰사발', '사발', '왕뚜껑', '왕컵', '갓뚜껑', '큰컵', '大컵', '용기', '왕컵']):
        return '큰컵'
    if '컵' in name or '뚜껑' in name:
        return '소컵'
    return None

def style(name):
    if any(k in name for k in ['볶음', '볶이', '비빔', '짜장', '짜파게티', '라볶이', '파스타', '까르보',
                               '로제', '야키소바', '스파게티', '짜슐랭', '범벅', '볶음면']):
        return '볶음형'
    if any(k in name for k in ['라면', '사발', '탕', '국', '짬뽕', '우동', '뚜껑', '해장', '곰탕', '카레',
                               '마라', '육개장', '미역국', '칼국수', '부대찌개', '완탕', '장국']):
        return '국물형'
    return None

EXCLUDE = ['선물세트', '주차번호판', '굿즈', '스토퍼', '뽑기', '뇽이', '누룽지팝', '스티커', '머그', '텀블러', '키링', '인형']

cols = ['브랜드', '제품명', '중량(g)', '가격(원)', '구성수량', '개당가격(원)',
        '열량(kcal)', '나트륨(mg)', '탄수화물(g)', '당류(g)', '지방(g)', '단백질(g)',
        '용기 크기(소컵/큰컵)', '국물형/볶음형', '출처 URL']

# dedupe exact
final = []
seen = set()
for r in rows:
    if any(k in r['name'] for k in EXCLUDE):
        continue
    key = (r['brand'], r['name'], r.get('weight'), r.get('count'), r.get('price'))
    if key in seen:
        continue
    seen.add(key)
    gc = container(r['name'], r['brand'])
    st = style(r['name'])
    cnt = r.get('count')
    price = r.get('price')
    unit = round(price / cnt) if (price and cnt and cnt > 1) else (price if price else None)
    final.append([
        r['brand'], r['name'], r.get('weight', ''), price if price is not None else '',
        cnt if cnt else '', unit if unit is not None else '',
        r.get('kcal', ''), r.get('나트륨', ''), r.get('탄수화물', ''), r.get('당류', ''),
        r.get('지방', ''), r.get('단백질', ''), gc if gc else '', st if st else '', r['url']
    ])

with open('cup_ramen.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(cols)
    w.writerows(final)

print('total rows:', len(final))
from collections import Counter
print(Counter(r[0] for r in final))
