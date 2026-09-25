#!/usr/bin/env python3
"""
check_links.py — find broken links in the repository's Markdown pages.

It checks every relative link, like [text](../lab01/README.md#goal):
  - that the file exists, and
  - that the #anchor matches a heading in that file (GitHub's rules).

Web links (http://, https://) are not checked — that needs the internet.

Usage:
    python3 check_links.py            # check the whole repository
    python3 check_links.py README.md  # check some files only

Exit code is 0 when every link is good, 1 otherwise.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

LINK = re.compile(r'(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)|!\[[^\]]*\]\(([^)\s]+)\)')
HTML_LINK = re.compile(r'(?:href|src)="([^"]+)"')
HEADING = re.compile(r'^(#{1,6})\s+(.*?)\s*#*\s*$')
FENCE = re.compile(r'^\s*(```|~~~)')


def github_slug(text):
    """Turn a heading into the anchor GitHub makes for it."""
    text = re.sub(r'<[^>]+>', '', text)          # drop inline HTML
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)  # [x](y) -> x
    text = text.replace('`', '').replace('*', '').replace('~', '')
    text = text.strip().lower()
    out = []
    for ch in text:
        if ch.isalnum() or ch in '-_':
            out.append(ch)
        elif ch == ' ':
            out.append('-')
        # every other character (punctuation, emoji) is dropped
    return ''.join(out)


def anchors_of(path, cache={}):
    if path in cache:
        return cache[path]
    seen, found, in_fence = {}, set(), False
    for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING.match(line)
        if not m:
            for a in re.findall(r'<a\s+(?:name|id)="([^"]+)"', line):
                found.add(a)
            continue
        slug = github_slug(m.group(2))
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        found.add(slug if n == 0 else f'{slug}-{n}')
    cache[path] = found
    return found


def links_in(path):
    in_fence = False
    for lineno, line in enumerate(path.read_text(encoding='utf-8', errors='replace').splitlines(), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        line = re.sub(r'`[^`]*`', '', line)   # ignore links inside inline code
        for m in LINK.finditer(line):
            yield lineno, m.group(1) or m.group(2)
        for m in HTML_LINK.finditer(line):
            yield lineno, m.group(1)


def check(path):
    problems = []
    for lineno, target in links_in(path):
        if re.match(r'^[a-z]+:', target) or target.startswith('//'):
            continue                                   # http:, mailto:, data: ...
        file_part, _, anchor = target.partition('#')
        dest = path if not file_part else (path.parent / file_part).resolve()
        if not dest.exists():
            problems.append((lineno, target, 'file not found'))
            continue
        if anchor and dest.suffix == '.md' and anchor not in anchors_of(dest):
            problems.append((lineno, target, 'no such heading'))
    return problems


def main():
    files = [Path(a).resolve() for a in sys.argv[1:]] or sorted(
        p for p in REPO.rglob('*.md') if '.git' not in p.parts)
    total = 0
    for f in files:
        for lineno, target, why in check(f):
            total += 1
            name = f.relative_to(REPO) if f.is_relative_to(REPO) else f
            print(f'{name}:{lineno}: {why}: {target}')
    print(f'\n{len(files)} file(s) checked, {total} broken link(s).')
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main())
