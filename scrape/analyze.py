"""Curate + analyze cup-ramen dataset.

Input : cup_ramen.csv (raw scrape output produced by build.py)
Output: data/cup_ramen.csv  (curated single-serving products, derived vars)
        data/analysis.json  (aggregates + correlations for the slide deck)
"""
import csv, json, os, math

RAW = 'cup_ramen.csv'

# Curated selection: one representative (single-serve) SKU per distinct product.
SELECT = {
    '농심': ['신라면컵', '신라면큰사발', '육개장사발면', '김치사발면', '너구리컵',
             '오징어짬뽕컵', '새우탕컵', '짜파게티범벅', '짜파게티큰사발',
             '사리곰탕큰사발', '튀김우동큰사발', '카구리큰사발면'],
    '오뚜기': ['진라면 매운맛 용기 110G', '진라면 순한맛 용기 110G', '진라면 매운맛 컵 65G',
              '참깨라면 용기 110G', '참깨라면 컵 65G', '육개장 컵 104G',
              '진짬뽕 용기 115G', '크림진짬뽕 용기 105G', '진비빔면 용기 134G',
              '마열라면 용기 105G'],
    '삼양': ['큰컵 삼양라면', '큰컵 간짬뽕', '컵 불닭볶음면', '큰컵 불닭볶음면',
             '큰컵 까르보불닭볶음면', '큰컵 치즈불닭볶음면', '큰컵 4가지치즈불닭볶음면',
             '큰컵 짜짜로니', '큰컵 나가사끼짬뽕', '큰컵 맵탱 흑후추소고기라면'],
    '팔도': ['아리 모던누들 간장버터 컵', '아리 모던누들 후추라볶이 컵',
             '아리 모던누들 김볶음면 오리지널 컵', '남자라면컵',
             '팔도 틈새라면 고기짬뽕 컵', '김치 왕뚜껑', '갓뚜껑 김치찌개',
             '볼케이노 까르보나라 왕컵'],
}

def fnum(v):
    if v in (None, '', 'N/A'):
        return None
    try:
        f = float(str(v).replace(',', ''))
        return int(f) if f.is_integer() else f
    except ValueError:
        return None

rows = list(csv.DictReader(open(RAW, encoding='utf-8-sig')))

picked = {}
for r in rows:
    b, n = r['브랜드'], r['제품명']
    if n not in SELECT.get(b, []):
        continue
    cnt = fnum(r['구성수량']) or 1
    key = (b, n)
    if key not in picked or cnt < (fnum(picked[key]['구성수량']) or 1):
        picked[key] = r

products = []
for (b, n), r in picked.items():
    weight = fnum(r['중량(g)'])
    price = fnum(r['가격(원)'])
    count = fnum(r['구성수량']) or 1
    unit = price / count if price else None
    kcal = fnum(r['열량(kcal)'])
    na = fnum(r['나트륨(mg)'])
    carb = fnum(r['탄수화물(g)'])
    sugar = fnum(r['당류(g)'])
    fat = fnum(r['지방(g)'])
    protein = fnum(r['단백질(g)'])
    p = {
        '브랜드': b, '제품명': n, '중량_g': weight, '판매가격_원': price,
        '묶음수량': count, '개당가격_원': round(unit) if unit else None,
        '열량_kcal': kcal, '나트륨_mg': na, '탄수화물_g': carb, '당류_g': sugar,
        '지방_g': fat, '단백질_g': protein,
        '소컵_큰컵': r['용기 크기(소컵/큰컵)'] or None,
        '국물형_볶음형': r['국물형/볶음형'] or None,
        '출처_URL': r['출처 URL'],
    }
    # derived (always per single serving -> use unit price)
    p['100g당_가격_원'] = round(unit / weight * 100, 1) if (unit and weight) else None
    p['100g당_열량_kcal'] = round(kcal / weight * 100, 1) if (kcal and weight) else None
    p['100g당_나트륨_mg'] = round(na / weight * 100, 1) if (na and weight) else None
    p['1000원당_중량_g'] = round(weight / unit * 1000, 1) if (weight and unit) else None
    p['1000원당_단백질_g'] = round(protein / unit * 1000, 2) if (protein and unit) else None
    products.append(p)

# ---- write curated csv ----
cols = ['브랜드', '제품명', '중량_g', '판매가격_원', '묶음수량', '개당가격_원',
        '열량_kcal', '나트륨_mg', '탄수화물_g', '당류_g', '지방_g', '단백질_g',
        '소컵_큰컵', '국물형_볶음형', '100g당_가격_원', '100g당_열량_kcal',
        '100g당_나트륨_mg', '1000원당_중량_g', '1000원당_단백질_g', '출처_URL']
with open('data/cup_ramen.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(cols)
    for p in products:
        w.writerow(['' if p[c] is None else p[c] for c in cols])

def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(sum(xs) / len(xs), 1) if xs else None

# ---- outlier detection (100g price, 1.5*IQR rule) ----
import statistics as _st
_vals = sorted(p['100g당_가격_원'] for p in products if p['100g당_가격_원'])
_q1 = _st.quantiles(_vals, n=4)[0]
_q3 = _st.quantiles(_vals, n=4)[2]
_upper = _q3 + 1.5 * (_q3 - _q1)
for p in products:
    p['is_outlier'] = bool(p['100g당_가격_원'] and p['100g당_가격_원'] > _upper)
valid = [p for p in products if not p['is_outlier']]
excluded = [{'브랜드': p['브랜드'], '제품명': p['제품명'],
             '100g당_가격_원': p['100g당_가격_원'],
             '사유': '100g당 가격이 Q3+1.5*IQR 초과(동일 브랜드 유사 제품 대비 가격 이상치)'}
            for p in products if p['is_outlier']]

# ---- brand stats ----
brands = ['농심', '오뚜기', '삼양', '팔도']
brand_stats = []
for b in brands:
    ps = [p for p in valid if p['브랜드'] == b]
    brand_stats.append({
        'brand': b,
        'n': len(ps),
        'avg_price': mean([p['개당가격_원'] for p in ps]),
        'avg_price_per_100g': mean([p['100g당_가격_원'] for p in ps]),
        'avg_kcal': mean([p['열량_kcal'] for p in ps]),
        'avg_sodium': mean([p['나트륨_mg'] for p in ps]),
        'avg_weight': mean([p['중량_g'] for p in ps]),
        'avg_protein': mean([p['단백질_g'] for p in ps]),
    })

# ---- category stats (soup vs stir-fried) ----
cat_stats = {}
for key in ['국물형', '볶음형']:
    ps = [p for p in valid if p['국물형_볶음형'] == key]
    cat_stats[key] = {
        'n': len(ps),
        'n_nutrition': sum(1 for p in ps if p['열량_kcal']),
        'avg_kcal': mean([p['열량_kcal'] for p in ps]),
        'avg_sodium': mean([p['나트륨_mg'] for p in ps]),
        'avg_carb': mean([p['탄수화물_g'] for p in ps]),
        'avg_sugar': mean([p['당류_g'] for p in ps]),
        'avg_fat': mean([p['지방_g'] for p in ps]),
        'avg_protein': mean([p['단백질_g'] for p in ps]),
    }

# ---- correlations ----
def pearson(pairs):
    xs = [a for a, b in pairs if a is not None and b is not None]
    ys = [b for a, b in pairs if a is not None and b is not None]
    n = len(xs)
    if n < 3:
        return {'r': None, 'n': n}
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    r = cov / (sx * sy) if sx and sy else None
    return {'r': round(r, 3) if r is not None else None, 'n': n}

corr = {
    'price_vs_weight': pearson([(p['개당가격_원'], p['중량_g']) for p in valid]),
    'price_vs_kcal': pearson([(p['개당가격_원'], p['열량_kcal']) for p in valid]),
    'weight_vs_sodium': pearson([(p['중량_g'], p['나트륨_mg']) for p in valid]),
    'price_vs_protein': pearson([(p['개당가격_원'], p['단백질_g']) for p in valid]),
}

fields = ['중량_g', '개당가격_원', '열량_kcal', '나트륨_mg', '탄수화물_g', '당류_g', '지방_g', '단백질_g']
missing = {f: sum(1 for p in products if p[f] is None) for f in fields}

json.dump({'products': products, 'valid_count': len(valid), 'outliers': excluded,
           'missing': missing, 'brand_stats': brand_stats,
           'category_stats': cat_stats, 'correlations': corr,
           'sources': sorted({p['출처_URL'].split('/')[2] for p in products})},
          open('data/analysis.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

print('products:', len(products))
print('by brand:', {b: sum(1 for p in products if p['브랜드'] == b) for b in brands})
print('with nutrition:', sum(1 for p in products if p['열량_kcal']))
print('with price+weight:', sum(1 for p in products if p['판매가격_원'] and p['중량_g']))
print('correlations:', json.dumps(corr, ensure_ascii=False))
for s in brand_stats:
    print(s)
print('category:', json.dumps(cat_stats, ensure_ascii=False))
