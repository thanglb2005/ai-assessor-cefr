"""Read-only credential-pattern review; reports locations, never matched values."""
import json
import re
import subprocess
from pathlib import Path

patterns = {
    'github_pat': rb'(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{60,})',
    'aws_access_id': rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    'private_key_header': rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'openai_key': rb'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{40,}',
}
names = subprocess.check_output(['git', 'ls-files', '-z']).split(b'\0')
hits = []
scanned = 0
for raw_name in names:
    if not raw_name:
        continue
    path = Path(raw_name.decode())
    data = path.read_bytes()
    if b'\0' in data[:8192]:
        continue
    scanned += 1
    for label, pattern in patterns.items():
        for match in re.finditer(pattern, data):
            hits.append({'file': str(path), 'line': data[:match.start()].count(b'\n')+1, 'pattern': label})
print(json.dumps({'checked_revision': subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(), 'text_files_scanned': scanned, 'findings': hits, 'limits': 'Four credential-pattern families only; binary attachments and semantic PII not exhaustively scanned.'}))
raise SystemExit(bool(hits))
