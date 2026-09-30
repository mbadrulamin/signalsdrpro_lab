#!/usr/bin/env python3
"""
sync_speaker_notes.py — copy the presenter notes into the slide deck.

The full presenter notes live in ONE place: 06_training/PRESENTER_NOTES.md.
Each slide has a section that starts with a heading like

    ## S12 · You fix it with a download (2 min)

The number after "S" is the slide number. This script turns each section into
simple HTML and puts it in that slide's <aside class="notes"> in
06_training/intro_to_sdr.html, which is what the speaker view (press S) shows.
So the printed notes and the speaker view always say the same thing.

Markdown understood: paragraphs, **bold**, *italic*, `code`, [links](shown as text), <kbd>keys</kbd>, lists
("- " and "1. "), tables, and quotes ("> "), which the speaker view shows as
the words to say.

Usage:
    python3 sync_speaker_notes.py            # update the deck
    python3 sync_speaker_notes.py --check    # only report whether it is up to date

The same works for any other deck built on the same slide engine, such as the
client briefing:

    python3 sync_speaker_notes.py --notes ../07_client_demo/PRESENTER_SCRIPT.md \
                                  --deck  ../07_client_demo/client_brief.html
"""
import argparse
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TRAINING = os.path.join(HERE, '..', '06_training')
NOTES = os.path.join(TRAINING, 'PRESENTER_NOTES.md')
DECK = os.path.join(TRAINING, 'intro_to_sdr.html')

HEADING = re.compile(r'^## S(\d+) · (.+)$')


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r'&lt;(/?)kbd&gt;', r'<\1kbd>', text)   # keep <kbd> keys
    codes = []                                      # protect code spans first

    def keep(m):
        codes.append('<code>' + m.group(1) + '</code>')
        return '\x00%d\x00' % (len(codes) - 1)
    text = re.sub(r'`([^`]+)`', keep, text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)   # [text](link) -> text: links do not work in the speaker view
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', text)
    return re.sub(r'\x00(\d+)\x00', lambda m: codes[int(m.group(1))], text)


def to_html(lines):
    """A small Markdown subset -> HTML, one block per blank-line-separated chunk."""
    blocks, cur = [], []
    for line in lines + ['']:
        if line.strip():
            cur.append(line.rstrip())
        elif cur:
            blocks.append(cur)
            cur = []
    out = []
    for b in blocks:
        if all(l.startswith('>') for l in b):
            paras = ' '.join(l[1:].strip() if l[1:].strip() else '\n' for l in b).split('\n')
            out.append('<blockquote>' + ''.join('<p>' + inline(p.strip()) + '</p>' for p in paras if p.strip()) + '</blockquote>')
        elif all(l.startswith('|') for l in b):
            rows = [[c.strip() for c in l.strip().strip('|').split('|')] for l in b
                    if not re.match(r'^\|[\s:|-]+\|?$', l)]
            head, body = rows[0], rows[1:]
            out.append('<table><tr>' + ''.join('<th>' + inline(c) + '</th>' for c in head) + '</tr>' +
                       ''.join('<tr>' + ''.join('<td>' + inline(c) + '</td>' for c in r) + '</tr>' for r in body) +
                       '</table>')
        elif re.match(r'^\d+\. ', b[0]) and all(re.match(r'^(\d+\. |   )', l) for l in b):
            items = []
            for l in b:
                if re.match(r'^\d+\. ', l):
                    items.append(re.sub(r'^\d+\. ', '', l).strip())
                else:
                    items[-1] += ' ' + l.strip()
            out.append('<ol>' + ''.join('<li>' + inline(i) + '</li>' for i in items) + '</ol>')
        elif all(l.startswith(('- ', '  ')) for l in b) and b[0].startswith('- '):
            items, it = [], []
            for l in b:
                if l.startswith('- '):
                    if it:
                        items.append(' '.join(it))
                    it = [l[2:].strip()]
                else:
                    it.append(l.strip())
            items.append(' '.join(it))
            out.append('<ul>' + ''.join('<li>' + inline(i) + '</li>' for i in items) + '</ul>')
        else:
            out.append('<p>' + inline(' '.join(l.strip() for l in b)) + '</p>')
    return ''.join(out)


def read_notes(path):
    notes, num, body = {}, None, []
    for line in open(path, encoding='utf-8').read().split('\n'):
        m = HEADING.match(line)
        if m or line.startswith('# ') or line.strip() == '<!-- end of slide notes -->':
            if num is not None:
                while body and body[-1].strip() in ('', '---'):
                    body.pop()
                notes[num] = to_html(body)
            num, body = (int(m.group(1)), []) if m else (None, [])
            continue
        if num is not None:
            body.append(line)
    if num is not None:
        notes[num] = to_html(body)
    return notes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--notes', default=NOTES, help='the Markdown notes (default: 06_training/PRESENTER_NOTES.md)')
    ap.add_argument('--deck', default=DECK, help='the HTML deck (default: 06_training/intro_to_sdr.html)')
    a = ap.parse_args()

    notes = read_notes(a.notes)
    deck = open(a.deck, encoding='utf-8').read()
    starts = [m.start() for m in re.finditer(r'<section class="slide', deck)]
    missing = [n for n in range(1, len(starts) + 1) if n not in notes]
    extra = [n for n in notes if not 1 <= n <= len(starts)]
    if missing or extra:
        sys.exit(f'notes and deck do not match: missing notes for slides {missing}, notes for non-existent slides {extra}')

    out, pos = [], 0
    for i, s in enumerate(starts, 1):
        end = deck.index('</section>', s)
        a0 = deck.index('<aside class="notes">', s)
        if a0 > end:
            sys.exit(f'slide {i} has no <aside class="notes">')
        a1 = deck.index('</aside>', a0) + len('</aside>')
        out.append(deck[pos:a0])
        out.append('<aside class="notes">' + notes[i] + '</aside>')
        pos = a1
    out.append(deck[pos:])
    new = ''.join(out)

    if a.check:
        print('speaker notes are up to date' if new == deck else 'speaker notes are OUT OF DATE: run sync_speaker_notes.py')
        return 0 if new == deck else 1
    if new != deck:
        open(a.deck, 'w', encoding='utf-8').write(new)
        print(f'updated the notes of {len(starts)} slides in {os.path.relpath(a.deck)}')
    else:
        print('already up to date')
    return 0


if __name__ == '__main__':
    sys.exit(main())
