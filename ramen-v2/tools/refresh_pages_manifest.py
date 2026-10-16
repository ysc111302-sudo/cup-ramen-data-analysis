import hashlib
import json
from prepare_pages import OUT, PUBLIC, verify

manifest = json.loads((OUT / 'deployment-manifest.json').read_text(encoding='utf-8'))
manifest['files'] = [{'path': name, 'bytes': (OUT / name).stat().st_size,
                      'sha256': hashlib.sha256((OUT / name).read_bytes()).hexdigest()}
                     for name in PUBLIC if name != 'deployment-manifest.json']
(OUT / 'deployment-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
verify()
print('Public manifest refreshed; exact allowlist and relative paths verified.')
