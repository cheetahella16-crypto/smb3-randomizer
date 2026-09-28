# SMB3 Randomizer

A generic ROM-based randomizer framework for Super Mario Bros 3.

## Overview

This project implements a flexible framework for randomizing ROM content. It's driven by a mapping JSON specification that defines regions of the ROM and operations to perform on each region.

## Features

- **Shuffle**: Randomize the order of fixed-size chunks within a region
- **Randomize Bytes**: Replace bytes with random values from an allowed set
- **Replace Values**: Map specific byte values to new values
- **IPS Patch Support**: Create and apply standard IPS patches for distributing modifications
- **Command-line Interface**: Easy-to-use CLI for generating patches
- **Comprehensive Testing**: 22 test cases covering all functionality

## Requirements

- **Python**: 3.10 or higher
- **OS**: Linux, macOS, or Windows

**Important**: This project does not include or distribute any ROM files. You must provide your own legal dump of Super Mario Bros 3.

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/cheetahella16-crypto/smb3-randomizer.git
cd smb3-randomizer

# Install the package in development mode
pip install -e .

# Install development dependencies (optional)
pip install -e ".[dev]"
# or use requirements.txt
pip install -r requirements.txt
```

## Quick Start

### 1. Prepare Your Mapping

Create or modify a JSON mapping file describing which ROM regions to randomize. See `mappings/smb3_example.json` for an example:

```json
{
  "regions": [
    {
      "name": "Level Data",
      "offset": 12345,
      "length": 128,
      "op": "shuffle",
      "chunk_size": 2
    },
    {
      "name": "Enemy Types",
      "offset": 23456,
      "length": 64,
      "op": "replace_values",
      "mapping": {1: 5, 2: 7}
    }
  ]
}
```

### 2. Generate a Patch

```bash
python cli.py \
  --rom /path/to/your/smb3.nes \
  --mapping mappings/smb3_example.json \
  --out smb3-randomized.ips \
  --seed 42
```

### 3. Apply the Patch

Use an IPS patcher tool (e.g., Lunar IPS, Flips) to apply `smb3-randomized.ips` to your ROM.

## CLI Usage

### Basic Usage

```bash
python cli.py --rom smb3.nes --mapping mappings/smb3.json --out patch.ips
```

### With Seed (Reproducible Randomization)

```bash
python cli.py --rom smb3.nes --mapping mappings/smb3.json --out patch.ips --seed 42
```

### Write Modified ROM (Testing Only)

```bash
python cli.py --rom smb3.nes --mapping mappings/smb3.json --out patch.ips --write-rom randomized.nes
```

### Command-line Options

| Option | Required | Description |
|--------|----------|-------------|
| `--rom` | ✓ | Path to source SMB3 .nes ROM |
| `--mapping` | ✓ | JSON mapping/spec file |
| `--out` | ✓ | Output IPS patch path |
| `--seed` | | Seed for deterministic randomization (optional) |
| `--write-rom` | | Path to write full modified ROM for testing (optional) |

## Randomization Operations

### Shuffle

Shuffles fixed-size chunks within a region.

```json
{
  "name": "LevelPointers",
  "offset": 12345,
  "length": 48,
  "op": "shuffle",
  "chunk_size": 2
}
```

**Parameters:**
- `offset`: Starting offset in ROM (0-based)
- `length`: Number of bytes to shuffle (must be divisible by chunk_size)
- `chunk_size`: Size of each chunk to shuffle

### Randomize Bytes

Replaces bytes with random values from an allowed set.

```json
{
  "name": "Items",
  "offset": 34567,
  "length": 64,
  "op": "randomize_bytes",
  "allowed": [0, 1, 2, 3]
}
```

**Parameters:**
- `offset`: Starting offset in ROM
- `length`: Number of bytes to randomize
- `allowed`: List of allowed byte values (if omitted, uses all 0-255)

### Replace Values

Maps specific byte values to new values.

```json
{
  "name": "Enemies",
  "offset": 23456,
  "length": 128,
  "op": "replace_values",
  "mapping": {1: 5, 2: 7}
}
```

**Parameters:**
- `offset`: Starting offset in ROM
- `length`: Number of bytes to process
- `mapping`: Dictionary mapping old byte values to new values

## Python API

### Basic Usage

```python
from randomizer import run_randomization
from ips import make_ips

# Load your ROM
with open('smb3.nes', 'rb') as f:
    original_rom = f.read()

# Define your spec
spec = {
    "regions": [
        {"name": "test", "offset": 0, "length": 10, "op": "shuffle", "chunk_size": 2}
    ]
}

# Apply randomization
randomized_rom = run_randomization(original_rom, spec, seed=42)

# Create IPS patch
make_ips(original_rom, randomized_rom, 'smb3.ips')
```

### API Reference

#### `run_randomization(original_rom, spec, seed=None)`

Apply randomization spec to ROM bytes.

**Parameters:**
- `original_rom` (bytes): The original ROM bytes
- `spec` (dict): Dictionary containing region specifications
- `seed` (int, optional): Seed for reproducible randomization

**Returns:**
- bytes: Modified ROM bytes

**Raises:**
- `ValueError`: If an unknown operation type is specified or bounds check fails

#### `make_ips(original, modified, out_path)`

Create an IPS patch file from original and modified ROM bytes.

**Parameters:**
- `original` (bytes): Original ROM bytes
- `modified` (bytes): Modified ROM bytes
- `out_path` (str): Path where IPS patch will be written

**Raises:**
- `ValueError`: If original and modified have different lengths

#### `apply_ips(rom, ips_path)`

Apply an IPS patch to ROM bytes.

**Parameters:**
- `rom` (bytes): Original ROM bytes
- `ips_path` (str): Path to IPS patch file

**Returns:**
- bytes: Patched ROM bytes

**Raises:**
- `ValueError`: If the file is not a valid IPS file

## Testing

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_randomizer.py -v
```

### Test Coverage

The project includes 22 comprehensive test cases:

- **test_randomizer.py** (14 tests): Tests for shuffle, randomize_bytes, replace_values, and run_randomization
- **test_ips.py** (8 tests): Tests for IPS patch creation and application

## Development

### Setting Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=. --cov-report=html
```

### Project Structure

```
smb3-randomizer/
├── __init__.py              # Package initialization
├── randomizer.py            # Core randomization routines
├── ips.py                   # IPS patch utilities
├── cli.py                   # Command-line interface
├── setup.py                 # Package configuration
├── requirements.txt         # Development dependencies
├── README.md                # This file
├── .gitignore               # Git ignore patterns
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI workflow
├── mappings/
│   └── smb3_example.json    # Example mapping file
└── tests/
    ├── __init__.py
    ├── test_randomizer.py   # Tests for randomizer module
    └── test_ips.py          # Tests for IPS module
```

## Limitations

- IPS patch support does not include Run-Length Encoding (RLE) records
- ROM offset range is limited to 24-bit addressing (max 16MB)
- Chunk size in shuffle operations must evenly divide the region length

## Locating ROM Offsets

To use this tool effectively, you need to find the correct ROM offsets for SMB3 data. Resources:

- **Disassembly Projects**: ROM disassemblers and community projects document data locations
- **ROM Hacking Communities**: SMB3 Hacking community sites often have documented offset lists
- **Hex Editors**: Tools like HxD or Ghidra can help locate data patterns

## Disclaimer

This tool is provided for educational purposes. You are responsible for ensuring you have the legal right to modify any ROM files. This project does not distribute or modify any copyrighted material.

## License

MIT License

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass: `pytest tests/ -v`
5. Submit a pull request

## Support

For issues, questions, or contributions, please visit:
https://github.com/cheetahella16-crypto/smb3-randomizer
