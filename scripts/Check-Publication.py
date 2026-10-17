"""Check public file inventory, links, source hashes and common secret formats.

No imports from the application, network requests, device input or key loading.
This is a focused publication check, not a general-purpose secret scanner.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'config/source-manifest.json'
FOLDERS = {'backend', 'scripts', 'tests', 'resource', 'page', 'docs', 'config', '.github'}
BINARY_SUFFIXES = {'.png', '.ico', '.onnx', '.bin'}
PATTERNS = (
    re.compile(rb'gh[pousr]_[A-Za-z0-9]{30,}'),
    re.compile(rb'github_pat_[A-Za-z0-9_]{30,}'),
    re.compile(rb'\bsk-[A-Za-z0-9]{24,}\b'),
    re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(rb'[A-Za-z]:[\\/]+Users[\\/]+(?!Public[\\/])[^\s"\x27<>]+', re.I),
)


def public_files():
    if (ROOT / '.git').exists():
        result = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
                                cwd=ROOT, capture_output=True, check=True)
        return sorted(set(result.stdout.decode('utf-8').strip('\0').split('\0')) - {''})
    files = []
    for path in ROOT.rglob('*'):
        relative = path.relative_to(ROOT)
        if (not path.is_file() or '__pycache__' in relative.parts
                or path.suffix.lower() in {'.pyc', '.pyo', '.lnk', '.log', '.dpapi', '.sqlite3'}):
            continue
        if len(relative.parts) > 1 and relative.parts[0] not in FOLDERS:
            continue
        if relative.parts[0] == 'config' and relative.as_posix() != MANIFEST and not path.name.endswith('.example.json'):
            continue
        files.append(relative.as_posix())
    return sorted(files)


def digest(path):
    raw = path.read_bytes()
    if path.suffix.lower() not in BINARY_SUFFIXES:
        raw = raw.replace(b'\r\n', b'\n')
    return hashlib.sha256(raw).hexdigest()


def inspect(root, files):
    errors = []
    for name in files:
        path = root / name
        parts = Path(name).parts
        if any(part in {'.venv', '__pycache__', 'logs', 'debug', 'history'} for part in parts):
            errors.append(name + ': private/generated directory')
        if path.suffix.lower() in {'.dpapi', '.lnk', '.log', '.pyc', '.sqlite3', '.db'} or '.sqlite3' in name:
            errors.append(name + ': local runtime data')
        if parts[0] == 'config' and name != MANIFEST and not name.endswith('.example.json'):
            errors.append(name + ': non-example configuration')
        if path.name == '.env' or path.name.startswith('.env.'):
            errors.append(name + ': environment file')
        if not path.is_file():
            errors.append(name + ': tracked file missing')
            continue
        raw = path.read_bytes()
        if len(raw) > 50 * 1024 * 1024:
            errors.append(name + ': file exceeds project 50 MiB limit')
        if path.suffix.lower() in BINARY_SUFFIXES:
            continue
        if any(pattern.search(raw) for pattern in PATTERNS):
            errors.append(name + ': credential or personal path pattern (value suppressed)')
        if path.suffix == '.md':
            text = raw.decode('utf-8-sig')
            for target in re.findall(r'(?<!!)\[[^\]]*\]\(([^\s)]+)\)', text):
                if target.startswith(('https://', 'http://', '#', 'mailto:')):
                    continue
                resolved = (path.parent / target.split('#', 1)[0]).resolve()
                if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
                    errors.append(name + ': missing or escaping local link ' + target)
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-manifest', action='store_true')
    args = parser.parse_args()
    files = public_files()
    errors = inspect(ROOT, files)
    hashes = {name: digest(ROOT / name) for name in files if name != MANIFEST and (ROOT / name).is_file()}
    path = ROOT / MANIFEST
    if args.write_manifest and not errors:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(hashes, ensure_ascii=False, indent=2) + '\n', 'utf-8', newline='\n')
    elif not path.exists():
        errors.append('Missing source manifest; run with --write-manifest after reviewing changes')
    else:
        expected = json.loads(path.read_text('utf-8'))
        for name in sorted(set(expected) | set(hashes)):
            if expected.get(name) != hashes.get(name):
                errors.append(name + ': source manifest mismatch')
    print(json.dumps(dict(files=len(files), checked_hashes=len(hashes), errors=errors), ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
