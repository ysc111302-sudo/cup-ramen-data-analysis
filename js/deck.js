/* Cup-ramen data-story slide deck engine + interactive charts */
(function () {
  const DATA = window.RAMEN_DATA;
  const STATIC = /[?&]static/.test(location.search);
  if (STATIC) document.body.classList.add('static');
  const slides = Array.from(document.querySelectorAll('.slide'));
  const deck = document.getElementById('deck');
  const progressBar = document.getElementById('progressBar');
  const curNo = document.getElementById('curNo');
  let current = -1;
  const charts = {};

  const BRAND_COLOR = { '농심': '#E23B2E', '오뚜기': '#F7A531', '삼양': '#2A9D8F', '팔도': '#FFD166' };
  const CREAM = '#FDF6EC', MUTED = '#C9B6A4', GRID = 'rgba(253,246,236,.10)';

  Chart.defaults.color = MUTED;
  Chart.defaults.font.family = '"Pretendard","Malgun Gothic","Noto Sans KR",sans-serif';
  Chart.defaults.font.size = 15;
  Chart.defaults.plugins.legend.labels.color = CREAM;
  Chart.defaults.plugins.legend.labels.boxWidth = 14;
  Chart.defaults.plugins.legend.labels.usePointStyle = true;
  Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(20,14,11,.95)';
  Chart.defaults.plugins.tooltip.titleColor = CREAM;
  Chart.defaults.plugins.tooltip.bodyColor = MUTED;
  Chart.defaults.plugins.tooltip.padding = 12;
  Chart.defaults.plugins.tooltip.borderColor = 'rgba(253,246,236,.15)';
  Chart.defaults.plugins.tooltip.borderWidth = 1;
  const axis = {
    grid: { color: GRID, drawBorder: false },
    ticks: { color: MUTED, font: { size: 15 } }
  };
  // bars grow one after another so the audience follows the order
  const barAnim = (dur = 900, step = 70) => ({
    duration: STATIC ? 0 : dur,
    delay: ctx => (ctx.type === 'data' && ctx.mode === 'default' ? ctx.dataIndex * step : 0)
  });

  const products = DATA.products;
  const valid = products.filter(p => !p.is_outlier);
  const nice = v => (v == null ? 'N/A' : v.toLocaleString());
  const r1 = v => (v == null ? null : Math.round(v * 10) / 10);

  function reg(pairs) {
    const pts = pairs.filter(a => a[0] != null && a[1] != null);
    const n = pts.length; if (n < 2) return null;
    const mx = pts.reduce((s, p) => s + p[0], 0) / n;
    const my = pts.reduce((s, p) => s + p[1], 0) / n;
    let num = 0, den = 0;
    pts.forEach(p => { num += (p[0] - mx) * (p[1] - my); den += (p[0] - mx) ** 2; });
    const m = num / den, b = my - m * mx;
    const xs = pts.map(p => p[0]);
    return [{ x: Math.min(...xs), y: m * Math.min(...xs) + b },
            { x: Math.max(...xs), y: m * Math.max(...xs) + b }];
  }

  /* ---------------- chart builders ---------------- */
  const builders = {
    chartBrands() {
      const labels = ['농심', '오뚜기', '삼양', '팔도'];
      const counts = labels.map(b => products.filter(p => p.브랜드 === b).length);
      return new Chart(document.getElementById('chartBrands'), {
        type: 'bar',
        data: {
          labels,
          datasets: [{ data: counts, backgroundColor: labels.map(l => BRAND_COLOR[l]),
            borderRadius: 8, maxBarThickness: 46 }]
        },
        options: {
          indexAxis: 'y', responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false },
            tooltip: { callbacks: { label: c => ` ${c.label} ${c.parsed.x}종` } } },
          scales: { x: { ...axis, beginAtZero: true, title: { display: true, text: '제품 수 (종)', color: CREAM } },
                    y: { grid: { display: false }, ticks: { color: CREAM, font: { size: 17 } } } },
          animation: barAnim(800, 90)
        }
      });
    },

    chartSources() {
      const col = (DATA.collection || []).slice();
      return new Chart(document.getElementById('chartSources'), {
        type: 'bar',
        data: {
          labels: col.map(c => c.site),
          datasets: [{ data: col.map(c => c.collected),
            backgroundColor: col.map((c, i) => ['#E23B2E', '#F7A531', '#FFD166', '#2A9D8F', '#8AC926'][i % 5]),
            borderRadius: 8, maxBarThickness: 34 }]
        },
        options: {
          indexAxis: 'y', responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false },
            tooltip: { callbacks: { label: c => ` 후보 ${c.parsed.x}건` } } },
          scales: { x: { ...axis, beginAtZero: true, title: { display: true, text: '수집 후보 (건)', color: CREAM } },
                    y: { grid: { display: false }, ticks: { color: CREAM, font: { size: 16 } } } },
          animation: barAnim(800, 90)
        }
      });
    },

    chartPrice() {
      const order = ['농심', '오뚜기', '삼양'];
      const vals = order.map(b => (DATA.brand_stats.find(s => s.brand === b) || {}).avg_price);
      return new Chart(document.getElementById('chartPrice'), {
        type: 'bar',
        data: { labels: order, datasets: [{ data: vals,
          backgroundColor: order.map(b => BRAND_COLOR[b]), borderRadius: 10, maxBarThickness: 92 }] },
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false },
            tooltip: { callbacks: { label: c => ` 평균 ${nice(c.parsed.y)}원` } } },
          scales: { x: axis, y: { ...axis, beginAtZero: true, suggestedMax: 1800,
            ticks: { color: MUTED, callback: v => v.toLocaleString() } } },
          animation: barAnim()
        }
      });
    },

    chartPrice100() {
      const order = ['농심', '오뚜기', '삼양'];
      const vals = order.map(b => (DATA.brand_stats.find(s => s.brand === b) || {}).avg_price_per_100g);
      return new Chart(document.getElementById('chartPrice100'), {
        type: 'bar',
        data: { labels: order, datasets: [{ data: vals,
          backgroundColor: order.map(b => BRAND_COLOR[b]), borderRadius: 10, maxBarThickness: 92 }] },
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false },
            tooltip: { callbacks: { label: c => ` 100g당 ${nice(c.parsed.y)}원` } } },
          scales: { x: axis, y: { ...axis, beginAtZero: true, suggestedMax: 2000,
            ticks: { color: MUTED, callback: v => v.toLocaleString() } } },
          animation: barAnim()
        }
      });
    },

    chartPriceWeight() {
      const groups = {};
      valid.filter(p => p.개당가격_원 && p.중량_g).forEach(p => {
        (groups[p.브랜드] = groups[p.브랜드] || []).push({ x: p.개당가격_원, y: p.중량_g, name: p.제품명 });
      });
      const datasets = Object.keys(groups).map(b => ({
        label: b, data: groups[b], backgroundColor: BRAND_COLOR[b], pointRadius: 7,
        pointHoverRadius: 10, pointBorderColor: '#171210', pointBorderWidth: 2
      }));
      const trend = reg(valid.filter(p => p.개당가격_원 && p.중량_g).map(p => [p.개당가격_원, p.중량_g]));
      if (trend) datasets.push({ label: '추세선', type: 'line', data: trend, borderColor: 'rgba(253,246,236,.55)',
        borderWidth: 2, borderDash: [7, 7], pointRadius: 0, fill: false });
      return new Chart(document.getElementById('chartPriceWeight'), {
        type: 'scatter',
        data: { datasets },
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom' },
            tooltip: { callbacks: {
              title: c => c[0].raw.name || '',
              label: c => ` ${c.parsed.x.toLocaleString()}원 · ${c.parsed.y}g` } } },
          scales: {
            x: { ...axis, title: { display: true, text: '개당 가격 (원)', color: CREAM }, beginAtZero: false },
            y: { ...axis, title: { display: true, text: '중량 (g)', color: CREAM }, beginAtZero: false }
          },
          animation: { duration: 900 }
        }
      });
    },

    chartPriceKcal() {
      const ps = valid.filter(p => p.개당가격_원 && p.열량_kcal);
      const trend = reg(ps.map(p => [p.개당가격_원, p.열량_kcal]));
      const datasets = [{ label: '제품',
        data: ps.map(p => ({ x: p.개당가격_원, y: p.열량_kcal, name: p.제품명 })),
        backgroundColor: ps.map(p => BRAND_COLOR[p.브랜드]),
        pointRadius: 9, pointBorderColor: '#171210', pointBorderWidth: 2 }];
      if (trend) datasets.push({ label: '추세선 (r=0.41)', type: 'line', data: trend,
        borderColor: 'rgba(253,246,236,.6)', borderWidth: 2, borderDash: [7, 7], pointRadius: 0 });
      return new Chart(document.getElementById('chartPriceKcal'), {
        type: 'scatter',
        data: { datasets },
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom' },
            tooltip: { callbacks: {
              title: c => c[0].raw.name || '',
              label: c => ` ${c.parsed.x.toLocaleString()}원 · ${c.parsed.y}kcal` } } },
          scales: {
            x: { ...axis, title: { display: true, text: '개당 가격 (원)', color: CREAM } },
            y: { ...axis, title: { display: true, text: '열량 (kcal)', color: CREAM } }
          },
          animation: { duration: 900 }
        }
      });
    },

    chartKcal() {
      const ps = valid.filter(p => p.열량_kcal).sort((a, b) => a.열량_kcal - b.열량_kcal);
      return new Chart(document.getElementById('chartKcal'), {
        type: 'bar',
        data: {
          labels: ps.map(p => (p.브랜드 + ' ' + p.제품명).slice(0, 22)),
          datasets: [{ data: ps.map(p => p.열량_kcal),
            backgroundColor: ps.map(p => BRAND_COLOR[p.브랜드]), borderRadius: 7, maxBarThickness: 26 }]
        },
        options: {
          indexAxis: 'y', responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false },
            tooltip: { callbacks: { label: c => ` ${c.parsed.x}kcal` } } },
          scales: { x: { ...axis, beginAtZero: true, title: { display: true, text: 'kcal (1회 제공량)', color: CREAM } },
                    y: { grid: { display: false }, ticks: { color: MUTED, font: { size: 14 } } } },
          animation: barAnim()
        }
      });
    },

    chartSodiumBrand() {
      const order = ['삼양', '팔도'];
      const vals = order.map(b => (DATA.brand_stats.find(s => s.brand === b) || {}).avg_sodium);
      return new Chart(document.getElementById('chartSodiumBrand'), {
        type: 'bar',
        data: { labels: order, datasets: [{ data: vals,
          backgroundColor: order.map(b => BRAND_COLOR[b]), borderRadius: 10, maxBarThickness: 110 }] },
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false },
            tooltip: { callbacks: { label: c => ` 평균 ${nice(c.parsed.y)}mg` } } },
          scales: { x: axis, y: { ...axis, beginAtZero: true, suggestedMax: 1700,
            ticks: { color: MUTED, callback: v => v.toLocaleString() } } },
          animation: barAnim()
        }
      });
    },

    chartWeightSodium() {
      const ps = valid.filter(p => p.중량_g && p.나트륨_mg);
      const trend = reg(ps.map(p => [p.중량_g, p.나트륨_mg]));
      const datasets = [{ label: '제품', data: ps.map(p => ({ x: p.중량_g, y: p.나트륨_mg, name: p.제품명 })),
        backgroundColor: ps.map(p => BRAND_COLOR[p.브랜드]), pointRadius: 9, pointBorderColor: '#171210', pointBorderWidth: 2 }];
      if (trend) datasets.push({ label: '추세선 (r=0.71)', type: 'line', data: trend,
        borderColor: 'rgba(253,246,236,.6)', borderWidth: 2, borderDash: [7, 7], pointRadius: 0 });
      return new Chart(document.getElementById('chartWeightSodium'), {
        type: 'scatter',
        data: { datasets },
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom' },
            tooltip: { callbacks: {
              title: c => c[0].raw.name || '', label: c => ` ${c.parsed.x}g · ${c.parsed.y}mg` } } },
          scales: {
            x: { ...axis, title: { display: true, text: '중량 (g)', color: CREAM } },
            y: { ...axis, title: { display: true, text: '나트륨 (mg)', color: CREAM } }
          },
          animation: { duration: 900 }
        }
      });
    },

    chartCategory() {
      const cats = ['탄수화물', '당류', '지방', '단백질'];
      const map = { '탄수화물': 'avg_carb', '당류': 'avg_sugar', '지방': 'avg_fat', '단백질': 'avg_protein' };
      return new Chart(document.getElementById('chartCategory'), {
        type: 'bar',
        data: {
          labels: cats,
          datasets: [
            { label: '국물형', backgroundColor: '#E23B2E', borderRadius: 8,
              data: cats.map(c => DATA.category_stats['국물형'][map[c]]) },
            { label: '볶음형', backgroundColor: '#F7A531', borderRadius: 8,
              data: cats.map(c => DATA.category_stats['볶음형'][map[c]]) }
          ]
        },
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom' },
            tooltip: { callbacks: { label: c => ` ${c.dataset.label} ${c.parsed.y}g` } } },
          scales: { x: axis, y: { ...axis, beginAtZero: true, title: { display: true, text: '평균 (g)', color: CREAM } } },
          animation: barAnim()
        }
      });
    },

    chartValue() {
      const ps = valid.filter(p => p['100g당_가격_원']).sort((a, b) => a['100g당_가격_원'] - b['100g당_가격_원']);
      const sel = ps.slice(0, 6).concat(ps.slice(-6));
      const colorFor = (i, n) => {
        const t = i / (n - 1);
        const c1 = [138, 201, 38], c2 = [226, 59, 46];
        return `rgb(${c1.map((v, k) => Math.round(v + (c2[k] - v) * t)).join(',')})`;
      };
      return new Chart(document.getElementById('chartValue'), {
        type: 'bar',
        data: {
          labels: sel.map(p => (p.브랜드 + ' ' + p.제품명).slice(0, 24)),
          datasets: [{ data: sel.map(p => p['100g당_가격_원']),
            backgroundColor: sel.map((p, i) => colorFor(i, sel.length)), borderRadius: 7, maxBarThickness: 24 }]
        },
        options: {
          indexAxis: 'y', responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false },
            tooltip: { callbacks: { label: c => ` ${nice(c.parsed.x)}원 / 100g` } } },
          scales: { x: { ...axis, beginAtZero: true, title: { display: true, text: '원 / 100g', color: CREAM } },
                    y: { grid: { display: false }, ticks: { color: MUTED, font: { size: 14 } } } },
          animation: barAnim()
        }
      });
    }
  };

  const SLIDE_CHARTS = {
    2: ['chartSources'],
    3: ['chartBrands'],
    4: ['chartPrice', 'chartPrice100'],
    5: ['chartPriceWeight'],
    6: ['chartPriceKcal', 'chartKcal'],
    7: ['chartSodiumBrand', 'chartWeightSodium'],
    8: ['chartCategory'],
    9: ['chartValue']
  };

  const visited = new Set();
  const ACT_ORDER = ['문제', '데이터', '분석', '발견', '결론'];
  const SLIDE_ACT = ['문제', '문제', '데이터', '분석', '분석', '분석', '분석', '분석', '분석', '발견', '발견', '결론'];

  function updateSteps(i) {
    const cur = ACT_ORDER.indexOf(SLIDE_ACT[i]);
    document.querySelectorAll('#steps span').forEach(sp => {
      const k = ACT_ORDER.indexOf(sp.dataset.act);
      sp.classList.toggle('on', k === cur);
      sp.classList.toggle('done', k < cur);
    });
  }

  function ensureCharts(i) {
    (SLIDE_CHARTS[i] || []).forEach(id => {
      if (!charts[id] && builders[id]) {
        try {
          charts[id] = builders[id]();
          if (STATIC) { charts[id].options.animation = false; charts[id].update('none'); }
        } catch (e) { console.warn(id, e); }
      }
    });
  }

  // replay the bar/point animation each time a slide is (re)entered
  function replayCharts(i) {
    if (STATIC) return;
    (SLIDE_CHARTS[i] || []).forEach(id => {
      const c = charts[id];
      if (c && visited.has(id)) { c.reset(); c.update(); }
      visited.add(id);
    });
  }

  function runCounts(slide) {
    slide.querySelectorAll('.count').forEach(el => {
      const target = +el.dataset.target; const suf = el.dataset.suffix || '';
      if (STATIC) { el.textContent = target.toLocaleString() + suf; return; }
      const dur = 950; let t0 = null;
      function step(ts) {
        if (!t0) t0 = ts;
        const p = Math.min(1, (ts - t0) / dur);
        const val = Math.round(target * (0.15 + 0.85 * p));
        el.textContent = val.toLocaleString() + suf;
        if (p < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    });
  }

  function goTo(i) {
    i = Math.max(0, Math.min(slides.length - 1, i));
    if (i === current) return;
    slides.forEach((s, k) => {
      s.classList.toggle('is-active', k === i);
      s.classList.toggle('leaving', k === current && k !== i);
      if (k !== current) setTimeout(() => s.classList.remove('leaving'), 500);
    });
    current = i;
    curNo.textContent = i + 1;
    progressBar.style.width = ((i + 1) / slides.length * 100) + '%';
    if (('#' + (i + 1)) !== location.hash) history.replaceState(null, '', '#' + (i + 1));
    ensureCharts(i);
    replayCharts(i);
    updateSteps(i);
    runCounts(slides[i]);
  }

  function fit() {
    const s = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
    deck.style.transform = `scale(${s})`;
  }

  /* controls */
  addEventListener('keydown', e => {
    if (['ArrowRight', 'ArrowDown', 'PageDown', ' ', 'Enter'].includes(e.key)) { e.preventDefault(); goTo(current + 1); }
    else if (['ArrowLeft', 'ArrowUp', 'PageUp'].includes(e.key)) { e.preventDefault(); goTo(current - 1); }
    else if (e.key === 'Home') goTo(0);
    else if (e.key === 'End') goTo(slides.length - 1);
    else if (e.key.toLowerCase() === 'f') toggleFs();
  });
  document.getElementById('nextBtn').onclick = () => goTo(current + 1);
  document.getElementById('prevBtn').onclick = () => goTo(current - 1);
  function toggleFs() {
    if (!document.fullscreenElement) document.documentElement.requestFullscreen().catch(() => {});
    else document.exitFullscreen();
  }
  document.getElementById('fsBtn').onclick = toggleFs;

  let sx = 0;
  addEventListener('touchstart', e => sx = e.touches[0].clientX, { passive: true });
  addEventListener('touchend', e => {
    const dx = e.changedTouches[0].clientX - sx;
    if (Math.abs(dx) > 60) goTo(current + (dx < 0 ? 1 : -1));
  }, { passive: true });

  addEventListener('resize', () => { fit(); Object.values(charts).forEach(c => c.resize()); });

  addEventListener('hashchange', () => {
    const h = parseInt((location.hash || '').slice(1), 10);
    if (!isNaN(h)) goTo(h - 1);
  });

  fit();
  const initial = parseInt((location.hash || '').slice(1), 10);
  goTo(isNaN(initial) ? 0 : initial - 1);
})();
