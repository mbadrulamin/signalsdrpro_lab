#!/usr/bin/env python3
"""
validate_flowgraph.py - Validate GRC (GNU Radio Companion) flowgraph files.

Two levels of checking:

  STRUCTURAL (always available, needs only PyYAML)
      1. YAML syntax is valid
      2. Required top-level keys exist (options, blocks, connections)
      3. Block names are unique and every block has an id and parameters
      4. Connections reference blocks that exist

  DEEP (used automatically when GNU Radio is importable)
      5. Every block id exists in the INSTALLED GNU Radio block library
      6. Every parameter expression evaluates in the flowgraph's namespace
      7. Every port type matches across every connection
      8. No required port is left unconnected

  The deep check is the one that matters.  The structural check cannot tell
  you that `filter_freq_xlating_fir_filter_xxx` is not a real block id (it is
  `freq_xlating_fir_filter_xxx`), or that a `ccf` filter cannot accept a float
  stream.  The deep check catches both, because it asks GNU Radio itself.

  With --compile it goes further and actually generates the Python, which is
  the same thing GRC does when you press F5.

Usage:
    python3 validate_flowgraph.py <file.grc>
    python3 validate_flowgraph.py <directory>        # every .grc beneath it
    python3 validate_flowgraph.py ../02_flowgraphs --compile
    python3 validate_flowgraph.py <file.grc> --structural-only

Exit status: 0 if everything passed, 1 otherwise.
"""
import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:                                          # pragma: no cover
    sys.exit("PyYAML is required:  pip install pyyaml")


# --------------------------------------------------------------------------
#  Deep validation via the installed GNU Radio
# --------------------------------------------------------------------------
def load_platform():
    """Return a GRC Platform with the installed block library, or None."""
    try:
        from gnuradio import gr
        from gnuradio.grc.core.platform import Platform
    except ImportError:
        return None
    try:
        p = Platform(name='validator', prefs=gr.prefs(), version=gr.version(),
                     version_parts=(gr.major_version(), gr.api_version(),
                                    gr.minor_version()))
        p.build_library()
        return p
    except Exception as exc:                                 # pragma: no cover
        print(f"  (could not build the GNU Radio block library: {exc})")
        return None


def deep_check(platform, path):
    """Returns (errors, info) where info is a short description on success."""
    try:
        data = platform.parse_flow_graph(str(path))
        fg = platform.make_flow_graph()
        fg.import_data(data)
        fg.rewrite()
        fg.validate()
    except Exception as exc:
        return [f"could not load flowgraph: {exc}"], None

    errors = []
    for b in fg.blocks:
        for msg in b.get_error_messages():
            errors.append(f"[{b.name} / {b.key}] " + msg.replace('\n', ' ').replace('\t', ' '))
    info = f"{len(fg.blocks)} blocks, {len(fg.connections)} connections"
    return errors, info


def compile_check(path):
    """Actually generate the Python, exactly as GRC's F5 does."""
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run(['grcc', '-o', tmp, str(path)],
                           capture_output=True, text=True, timeout=300)
        out = r.stdout + r.stderr
        if 'Compilation error' in out or r.returncode != 0:
            tail = [ln for ln in out.splitlines()
                    if ln.strip() and 'Welcome' not in ln and 'Block paths' not in ln]
            return tail[-6:]
        generated = sorted(Path(tmp).glob('*.py'))
        for g in generated:                       # syntax-check what came out
            c = subprocess.run([sys.executable, '-m', 'py_compile', str(g)],
                               capture_output=True, text=True)
            if c.returncode != 0:
                return [f"generated {g.name} does not compile: {c.stderr.strip()}"]
        return []


# --------------------------------------------------------------------------
#  Structural validation (no GNU Radio required)
# --------------------------------------------------------------------------
def structural_check(path):
    errors, warnings = [], []
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        return [f"YAML syntax error: {exc}"], []
    except FileNotFoundError:
        return [f"file not found: {path}"], []

    if not isinstance(data, dict):
        return ["root element must be a YAML mapping"], []

    missing = {'options', 'blocks', 'connections'} - set(data)
    if missing:
        errors.append(f"missing top-level keys: {sorted(missing)}")

    opts = data.get('options', {})
    if 'parameters' not in opts:
        errors.append("options.parameters is missing")
    else:
        if 'id' not in opts['parameters']:
            errors.append("options.parameters.id is missing")
        if 'generate_options' not in opts['parameters']:
            warnings.append("no generate_options (defaults to a no-GUI flowgraph)")

    names, undocumented = set(), []
    blocks = data.get('blocks', [])
    if not isinstance(blocks, list):
        errors.append("'blocks' must be a list")
        blocks = []
    for i, b in enumerate(blocks):
        if not isinstance(b, dict):
            errors.append(f"block {i} is not a mapping")
            continue
        name = b.get('name')
        if not name:
            errors.append(f"block {i} has no 'name'")
        elif name in names:
            errors.append(f"duplicate block name: {name!r}")
        else:
            names.add(name)
        if not b.get('id'):
            errors.append(f"block {name!r} has no 'id'")
        params = b.get('parameters')
        if params is None:
            errors.append(f"block {name!r} has no 'parameters'")
        elif b.get('id') not in ('note', 'import') and not params.get('comment'):
            undocumented.append(name)

    conns = data.get('connections', [])
    if not isinstance(conns, list):
        errors.append("'connections' must be a list")
        conns = []
    for i, c in enumerate(conns):
        if not isinstance(c, list) or len(c) < 4:
            errors.append(f"connection {i} is malformed: {c}")
            continue
        if c[0] not in names:
            errors.append(f"connection {i}: source {c[0]!r} does not exist")
        if c[2] not in names:
            errors.append(f"connection {i}: destination {c[2]!r} does not exist")

    if 'metadata' not in data:
        warnings.append("no 'metadata' section (file_format / grc_version)")
    if undocumented:
        shown = ', '.join(undocumented[:6]) + ('...' if len(undocumented) > 6 else '')
        warnings.append(f"{len(undocumented)} block(s) have no 'comment': {shown}")
    return errors, warnings


# --------------------------------------------------------------------------
def validate(path, platform, do_compile):
    print(f"\n{'=' * 70}\n{path}\n{'=' * 70}")
    errors, warnings = structural_check(path)
    depth = "structural"

    if not errors and platform is not None:
        deep_errors, info = deep_check(platform, path)
        errors += deep_errors
        depth = "structural + deep"
        if not deep_errors and info:
            print(f"  {info}")

    if not errors and do_compile:
        cerrors = compile_check(path)
        errors += [f"compile: {e}" for e in cerrors]
        depth += " + compile"

    for w in warnings:
        print(f"  warning: {w}")
    for e in errors:
        print(f"  ERROR:   {e}")
    print(f"  {'FAIL' if errors else 'PASS'}  ({depth})")
    return not errors


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('target', help='a .grc file or a directory to search')
    ap.add_argument('--compile', action='store_true',
                    help='also generate the Python with grcc and syntax-check it')
    ap.add_argument('--structural-only', action='store_true',
                    help='skip the GNU Radio block-library checks')
    args = ap.parse_args()

    target = Path(args.target)
    if target.is_dir():
        files = sorted(target.rglob('*.grc'))
        if not files:
            print(f"no .grc files found under {target}")
            return 1
    elif target.is_file():
        files = [target]
    else:
        print(f"error: {target} is neither a file nor a directory")
        return 1

    platform = None if args.structural_only else load_platform()
    if platform is None and not args.structural_only:
        print("NOTE: GNU Radio is not importable - running structural checks only.")
        print("      Install GNU Radio 3.10 for block-id and port-type validation.")

    results = [validate(f, platform, args.compile) for f in files]
    passed = sum(results)
    print(f"\n{'=' * 70}")
    print(f"{passed}/{len(results)} flowgraph(s) passed")
    return 0 if passed == len(results) else 1


if __name__ == '__main__':
    sys.exit(main())
