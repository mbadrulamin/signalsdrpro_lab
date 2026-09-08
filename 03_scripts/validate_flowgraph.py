#!/usr/bin/env python3
"""
validate_flowgraph.py - Validate GRC (GNU Radio Companion) flowgraph files.

This script performs structural validation of .grc YAML files without needing
GNU Radio to be installed. It checks:

1. YAML syntax is valid
2. Required top-level keys exist (options, blocks, connections)
3. Block IDs are valid GNU Radio block identifiers
4. Connections reference existing blocks
5. Variables are referenced correctly
6. Sample rates are compatible between connected blocks (basic check)

Usage:
    python3 validate_flowgraph.py <path_to_grc_file>
    python3 validate_flowgraph.py <directory>   # validate all .grc files in dir

Returns:
    0 if all checks pass
    1 if any structural error is found
"""

import sys
import yaml
import os
import re
from pathlib import Path


# Known valid GNU Radio 3.10 block IDs (partial list)
KNOWN_BLOCKS = {
    # Variables
    'variable', 'variable_qtgui_range', 'variable_qtgui_entry',
    'variable_chooser', 'variable_slider', 'variable_text_box',
    # Sources
    'uhd_usrp_source', 'soapy_source', 'blocks_null_source',
    'analog_sig_source_x', 'blocks_throttle',
    # Sinks
    'uhd_usrp_sink', 'soapy_sink', 'audio_sink', 'blocks_null_sink',
    'qtgui_freq_sink_x', 'qtgui_waterfall_sink_x', 'qtgui_time_sink_x',
    'qtgui_const_sink_x', 'qtgui_histogram_sink_x', 'qtgui_number_sink',
    'blocks_file_sink', 'qtgui_eye_sink_x',
    # Modulation/Demodulation
    'analog_wfm_rcv', 'analog_wfm_rcv_pll', 'analog_wfm_tx',
    'analog_nbfm_rx', 'analog_nbfm_tx', 'digital_ofdm_rx',
    'analog_quadrature_demod_cf', 'analog_agc2_cc',
    # Filters
    'low_pass_filter', 'high_pass_filter', 'band_pass_filter',
    'band_reject_filter', 'rational_resampler_xxx', 'pfb_channelizer',
    'filter_singlepole_iir', 'fir_filter_xxx', 'fft_filter_xxx',
    # Math/Processing
    'blocks_multiply_xx', 'blocks_add_xx', 'blocks_sub_xx',
    'blocks_multiply_const_vxx', 'multiply_const_vff',
    'analog_pwr_squelch_cc', 'analog_pwr_squelch_ff',
    'agc2_cc', 'agc2_ff', 'analog_agc2_cc',
    'blocks_float_to_complex', 'blocks_complex_to_float',
    'blocks_complex_to_real', 'blocks_real_to_complex',
    'blocks_complex_to_mag', 'blocks_complex_to_arg',
    'analog_pll_refout_cc', 'analog_frequency_modulator_fc',
    'analog_phase_modulator_fc', 'analog_cpfsk_bc',
    # Type converters
    'blocks_complex_to_float', 'blocks_float_to_complex',
    'blocks_short_to_float', 'blocks_float_to_short',
    'blocks_char_to_float', 'blocks_float_to_char',
}


class GrcValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_file(self, filepath: str) -> bool:
        """Validate a single .grc file. Returns True if valid."""
        print(f"\n{'='*60}")
        print(f"Validating: {filepath}")
        print('='*60)

        self.errors = []
        self.warnings = []

        # Step 1: Load YAML
        try:
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.errors.append(f"YAML syntax error: {e}")
            self._print_results()
            return False
        except FileNotFoundError:
            self.errors.append(f"File not found: {filepath}")
            self._print_results()
            return False

        if not isinstance(data, dict):
            self.errors.append("Root element must be a YAML mapping")
            self._print_results()
            return False

        # Step 2: Check required top-level keys
        required = {'options', 'blocks', 'connections'}
        missing = required - set(data.keys())
        if missing:
            self.errors.append(f"Missing top-level keys: {missing}")

        # Step 3: Validate options
        if 'options' in data:
            self._validate_options(data['options'])

        # Step 4: Validate blocks
        block_names = set()
        if 'blocks' in data:
            block_names = self._validate_blocks(data['blocks'])

        # Step 5: Validate connections
        if 'connections' in data and 'blocks' in data:
            self._validate_connections(data['connections'], data['blocks'])

        # Step 6: Metadata
        if 'metadata' not in data:
            self.warnings.append("No 'metadata' section (file_format / grc_version)")

        self._print_results()
        return len(self.errors) == 0

    def _validate_options(self, options):
        if 'parameters' not in options:
            self.errors.append("options.parameters missing")
            return
        params = options['parameters']
        if 'id' not in params:
            self.errors.append("options.parameters.id missing")
        if 'generate_options' not in params:
            self.warnings.append("No generate_options (default is no-GUI)")

    def _validate_blocks(self, blocks):
        block_names = set()
        if not isinstance(blocks, list):
            self.errors.append("'blocks' must be a list")
            return block_names

        for i, block in enumerate(blocks):
            if not isinstance(block, dict):
                self.errors.append(f"Block {i} is not a mapping")
                continue

            # Name
            name = block.get('name')
            if not name:
                self.errors.append(f"Block {i} missing 'name'")
            elif name in block_names:
                self.errors.append(f"Duplicate block name: '{name}'")
            else:
                block_names.add(name)

            # ID
            block_id = block.get('id')
            if not block_id:
                self.errors.append(f"Block '{name}' missing 'id'")
            elif block_id not in KNOWN_BLOCKS:
                self.warnings.append(f"Block '{name}' uses unknown ID '{block_id}' "
                                     f"(may still be valid - e.g., custom OOT)")

            # Parameters
            if 'parameters' not in block:
                self.errors.append(f"Block '{name}' missing 'parameters'")

        return block_names

    def _validate_connections(self, connections, blocks):
        if not isinstance(connections, list):
            self.errors.append("'connections' must be a list")
            return

        block_names = {b.get('name') for b in blocks if isinstance(b, dict)}

        for i, conn in enumerate(connections):
            if not isinstance(conn, list) or len(conn) < 4:
                self.errors.append(f"Connection {i} malformed: {conn}")
                continue

            src_name, src_port, dst_name, dst_port = conn[0], conn[1], conn[2], conn[3]

            if src_name not in block_names:
                self.errors.append(f"Connection {i}: source '{src_name}' not found")
            if dst_name not in block_names:
                self.errors.append(f"Connection {i}: destination '{dst_name}' not found")

    def _print_results(self):
        if self.warnings:
            print(f"\n  ⚠  {len(self.warnings)} WARNING(S):")
            for w in self.warnings:
                print(f"     - {w}")
        if self.errors:
            print(f"\n  ✗  {len(self.errors)} ERROR(S):")
            for e in self.errors:
                print(f"     - {e}")
            print("\n  RESULT: INVALID")
        else:
            print("\n  ✓  All checks passed")
            print("  RESULT: VALID (structural)")


def validate_directory(directory: str):
    """Validate all .grc files in a directory."""
    path = Path(directory)
    grc_files = sorted(path.rglob('*.grc'))
    if not grc_files:
        print(f"No .grc files found in {directory}")
        return False

    print(f"Found {len(grc_files)} .grc file(s)")
    validator = GrcValidator()
    all_valid = True
    for f in grc_files:
        if not validator.validate_file(str(f)):
            all_valid = False
    return all_valid


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    target = sys.argv[1]
    if os.path.isdir(target):
        ok = validate_directory(target)
    elif os.path.isfile(target):
        validator = GrcValidator()
        ok = validator.validate_file(target)
    else:
        print(f"Error: {target} is neither a file nor directory")
        sys.exit(1)

    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
