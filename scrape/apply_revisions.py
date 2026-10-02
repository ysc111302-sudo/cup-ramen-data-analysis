import re

p = 'index.html'
s = open(p, encoding='utf-8').read()

# --- Q badges on chart captions (traceability back to questions A~G) ---
subs = [
    ('<p class="chart-note">평균 1,353~1,550원',
     '<p class="chart-note"><span class="qbadge">Q3</span>평균 1,353~1,550원'),
    ('<p class="chart-note">상관 <b>r = 0.41</b>',
     '<p class="chart-note"><span class="qbadge">Q1</span>상관 <b>r = 0.41</b>'),
    ('<p class="chart-note">팔도 <b>1,516mg</b>',
     '<p class="chart-note"><span class="qbadge">Q4</span>팔도 <b>1,516mg</b>'),
    ('<p class="chart-note">중량↑ → 나트륨↑',
     '<p class="chart-note"><span class="qbadge">Q5</span>중량↑ → 나트륨↑'),
    ('<p class="chart-note">볶음형 당류가 국물형의',
     '<p class="chart-note"><span class="qbadge">Q6</span>볶음형 당류가 국물형의'),
    ('<p class="chart-note">최저 <b>1,005원</b>',
     '<p class="chart-note"><span class="qbadge">Q7</span>최저 <b>1,005원</b>'),
]
n = 0
for a, b in subs:
    if a in s:
        s = s.replace(a, b, 1)
        n += 1
    else:
        print('MISS:', a[:45])

# --- A~G summary strip under the dataset slide ---
qa_chips = (
    '<div class="qa-strip reveal" style="--d:5">'
    '<span class="qa-t">질문 A–G → 결과</span>'
    '<span class="qa-chip"><b>A</b>가격↔중량 약함(r0.41)</span>'
    '<span class="qa-chip"><b>B</b>가격↔열량 약함(r0.41)</span>'
    '<span class="qa-chip"><b>C</b>브랜드 가격차 ~200원</span>'
    '<span class="qa-chip"><b>D</b>팔도 나트륨 +30%</span>'
    '<span class="qa-chip"><b>E</b>중량↔나트륨 강함(r0.71)</span>'
    '<span class="qa-chip"><b>F</b>국물 나트륨↑·볶음 당류↑</span>'
    '<span class="qa-chip"><b>G</b>최저 1,005원/100g</span>'
    '</div>'
)
anchor = '''      <div class="ov-stats">
          <div class="stat reveal" style="--d:1"><span class="stat-v count" data-target="40">0</span><span class="stat-l">분석 제품 수</span></div>
          <div class="stat reveal" style="--d:2"><span class="stat-v count" data-target="32">0</span><span class="stat-l">가격·중량 보유</span></div>
          <div class="stat reveal" style="--d:3"><span class="stat-v count" data-target="14">0</span><span class="stat-l">영양성분 보유</span></div>
          <div class="stat reveal" style="--d:4"><span class="stat-v">103<span class="unit">g</span></span><span class="stat-l">평균 중량</span></div>
        </div>
      </div>'''
if anchor in s:
    s = s.replace(anchor, anchor + '\n      ' + qa_chips, 1)
    n += 1
else:
    print('MISS: ov-stats anchor')

open(p, 'w', encoding='utf-8').write(s)
print('applied edits:', n)
