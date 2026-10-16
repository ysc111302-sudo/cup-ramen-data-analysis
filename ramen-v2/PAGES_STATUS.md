# 배포 검증 기록

- 제출 URL: https://ysc111302-sudo.github.io/cup-ramen-data-analysis/
- 저장소: https://github.com/ysc111302-sudo/cup-ramen-data-analysis
- 배포 워크플로: `.github/workflows/ramen-pages.yml`, 실행38855950871, 결론success.
- 배포 콘텐츠 커밋: `a9b20defdbd65dcf04dc9f6100d6b74cb04b0942`.
- 기존 master 이력에 일반 커밋 추가 후 push. 강제푸시·이력 초기화 없음.
- 기존 Pages 주소 유지, publishing source를 legacy에서 workflow로 변경. `ramen-v2/site/index.html`이 웹 루트 진입점.
- Pages에 허용 목록15파일만 게시. 공개 HTTP 대상13파일은 전부200·배포 해시 일치. `.nojekyll`은 웹 자원이 아닌제어파일로 HTTP검사 제외.
- 1920×1080·1366×768 전체12장 검증, SVG11개 정상. 요청실패·이미지누락·콘솔오류·잘림·본문/해석 겹침·가로넘침0건.
- 방향키·Space·PageUp/PageDown·Home/End·이전/다음 버튼 및 F/버튼 전체화면 정상.
- 브라우저 PDF12페이지 생성, 로컬파일 열기도 정상.
- 현재 이미지는 사용자 제공 Gemini 사진4개와 개념삽화1개다. 요청에서 말한 새사진5개와 달리 원본2는 한컵사진, 원본3은 진열대, 원본4는 크기비교였다. 국물·볶음 사진은 없어 기존개념삽화 유지. 모델·생성시각 미확인.
- 사진은 원본을 보존한WebP사본. 공개묶음 약1.9MB. 데이터와 차트엔진은 기존분석 유지.
- API키·.env·DPAPI·인증/키입력/이미지생성 도구·로그·캡처·임시파일·다른 프로젝트는 새업로드/Pages대상에서 제외. 기존4개 커밋에서도 자격증명 패턴 검출없음. 값은출력하지않음.
- 업데이트 절차는 `DEPLOYMENT.md`. 저장소명·도메인을 바꾸지않으면 같은URL로 갱신.

검증일: 2026-10-16. 상세 브라우저 캡처와 기계검사 원본은 로컬 `ramen-v2/review/pages-live/`에 보존하고 공개커밋에는 포함하지 않았다.
