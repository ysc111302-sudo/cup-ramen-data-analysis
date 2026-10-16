# 컵라면 발표 GitHub Pages

제출 URL: https://ysc111302-sudo.github.io/cup-ramen-data-analysis/

2026-10-16 배포 성공. 공개 주소에서 1920×1080·1366×768의 전체12장, SVG11개, 사진4개·삽화1개, 방향키·버튼·키보드/버튼 전체화면을 검증했다. 콘솔 오류·자원 실패·잘림·겹침·가로넘침0건. 배포 실행: https://github.com/ysc111302-sudo/cup-ramen-data-analysis/actions/runs/38855950871

기존 원격 저장소: https://github.com/ysc111302-sudo/cup-ramen-data-analysis

배포 진입점은 `ramen-v2/site/index.html`이며, 현재 `ramen-v2/index.html`의 발표 내용을 복사해 만든다. 기존 루트 덱·다른 프로젝트·커밋 이력은 유지한다. GitHub Actions는 `ramen-v2/site`만 Pages에 게시한다.

## 같은 URL로 업데이트

현재 작업 폴더에서 HTML·CSS·이미지·데이터를 수정한 뒤:

```powershell
python ramen-v2/tools/prepare_pages.py
git add -- ramen-v2/site
git commit -m "발표 수정: 컵라면 자료 업데이트"
git push origin master
gh run list --workflow ramen-pages.yml --limit 3
```

원격 저장소만 새로 받아 수정할 때는 공개된 `ramen-v2/site/index.html`, CSS·JS·이미지를 직접 수정해도 된다. 다만 `deployment-manifest.json`의 해시도 갱신해야 하므로 아래 명령을 사용한다.

```powershell
python ramen-v2/tools/refresh_pages_manifest.py
git add -- ramen-v2/site
git commit -m "발표 수정: 공개 발표자료 업데이트"
git push origin master
```

`prepare_pages.py`는 원본 Gemini PNG4개를 해상도 유지 WebP로 변환해 전송 용량을 줄인다. Python과 Pillow가 필요하다. 원본은 보존한다. 현재 구성은 사진4개와 국물·볶음 개념 삽화1개이며, 제공되지 않은 비교 사진을 새로 생성하지 않는다.

공개 허용 목록은 `prepare_pages.py`에 고정되어 있다. HTML·CSS·JS·완성 이미지·공개 제품 데이터·출처 메모·무자격증명 파일 목록만 포함한다. API 키, .env, DPAPI, 인증/키입력/이미지생성 도구, 로그, 리뷰 캡처, 임시파일, 원본 번호 이미지, 다른 프로젝트는 새 커밋/Pages 묶음에 포함하지 않는다.

워크플로가 성공하면 같은 Pages URL의 내용이 갱신된다. 저장소 이름·Pages 도메인 설정을 바꾸지 않는 한 제출 URL은 유지된다.
