import hashlib
import json
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
DECK = ROOT / 'ramen-v2'
OUT = DECK / 'site'
PHOTOS = ['cover-hero', 'problem-shelf', 'size-comparison', 'closing']
PUBLIC = ['index.html', 'css/style.css', 'js/data.js', 'js/deck.js',
          'data/cup_ramen.csv', 'data/analysis.json', 'assets/generated/flow-soup-vs-stir.webp',
          *[f'assets/generated/nano-{name}.webp' for name in PHOTOS],
          'references/S03_ramen_audit.md', 'references/S05_user_gemini_images.md', '.nojekyll',
          'deployment-manifest.json']


class Resources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for name in ['src', 'href']:
            if attrs.get(name):
                self.urls.append(attrs[name])


def verify():
    actual = {p.relative_to(OUT).as_posix() for p in OUT.rglob('*') if p.is_file()}
    if actual != set(PUBLIC):
        raise SystemExit('공개 허용 목록 이외 파일이 있거나 필수 파일이 누락됐습니다.')
    html = (OUT / 'index.html').read_text(encoding='utf-8')
    if len(re.findall(r'<section\b', html)) != 12:
        raise SystemExit('발표 슬라이드가 12장이 아닙니다.')
    parser = Resources()
    parser.feed(html)
    for url in parser.urls:
        parsed = urlsplit(url)
        if parsed.scheme or url.startswith('#'):
            continue
        path = unquote(parsed.path)
        if path.startswith('/') or '..' in Path(path).parts or path not in actual:
            raise SystemExit('대소문자를 포함한 상대경로 검증 실패: ' + path)
    forbidden = re.compile(r'AIza[0-9A-Za-z_-]{25,}|(?:ghp_|gho_|github_pat_)[0-9A-Za-z_]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
    for name in actual:
        if Path(name).suffix in ['.html', '.css', '.js', '.json', '.csv', '.md']:
            text = (OUT / name).read_text(encoding='utf-8-sig')
            if forbidden.search(text):
                raise SystemExit('비밀값으로 의심되는 내용 발견. 값은 출력하지 않습니다: ' + name)
    for name in ['js/data.js', 'js/deck.js']:
        text = (OUT / name).read_text(encoding='utf-8')
        if re.search(r'generativelanguage|GEMINI_API_KEY|GOOGLE_API_KEY|CryptUnprotectData', text):
            raise SystemExit('배포 JavaScript에 생성 API 또는 인증 처리가 있습니다.')


def main():
    OUT.mkdir(exist_ok=True)
    unexpected = [p for p in OUT.rglob('*') if p.is_file() and p.relative_to(OUT).as_posix() not in PUBLIC]
    if unexpected:
        raise SystemExit('기존 공개 폴더에 알 수 없는 파일이 있습니다. 삭제하거나 덮어쓰지 않았습니다.')
    html = (DECK / 'index.html').read_text(encoding='utf-8')
    for name in PHOTOS:
        source = DECK / f'assets/generated/nano-{name}.png'
        target = OUT / f'assets/generated/nano-{name}.webp'
        target.parent.mkdir(parents=True, exist_ok=True)
        from PIL import Image
        with Image.open(source) as image:
            image.convert('RGB').save(target, format='WEBP', quality=90, method=6)
        html = html.replace(f'nano-{name}.png', f'nano-{name}.webp')
    for name in ['S03_ramen_audit.md', 'S05_user_gemini_images.md']:
        html = html.replace('../references/notes/' + name, 'references/' + name)
        target = OUT / 'references' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / 'references/notes' / name, target)
    (OUT / 'index.html').write_text(html, encoding='utf-8')
    for name in ['css/style.css', 'js/data.js', 'js/deck.js', 'data/cup_ramen.csv', 'data/analysis.json', 'assets/generated/flow-soup-vs-stir.webp']:
        target = OUT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(DECK / name, target)
    (OUT / '.nojekyll').write_text('', encoding='utf-8')
    records = [{'path': name, 'bytes': (OUT / name).stat().st_size,
                'sha256': hashlib.sha256((OUT / name).read_bytes()).hexdigest()}
               for name in PUBLIC if name != 'deployment-manifest.json']
    (OUT / 'deployment-manifest.json').write_text(json.dumps({'entry': 'index.html', 'slides': 12,
        'photo_count': 4, 'concept_illustration_count': 1,
        'source': 'ramen-v2/index.html; user-provided Gemini photos; exact model and generation time unknown',
        'files': records}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    verify()
    print(f'Public site verified: {len(PUBLIC)} allowlisted files, {sum((OUT / n).stat().st_size for n in PUBLIC):,} bytes')


if __name__ == '__main__':
    main()
