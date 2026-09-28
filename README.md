# SMB3 Randomizer

A generic ROM-based randomizer framework for Super Mario Bros 3.

## Overview

This project implements a flexible framework for randomizing ROM content. It's driven by a mapping JSON specification that defines regions of the ROM and operations to perform on each region.

## Features

- **Shuffle**: Randomize the order of fixed-size chunks within a region
- **Randomize Bytes**: Replace bytes with random values from an allowed set
- **Replace Values**: Map specific byte values to new values
- **IPS Patch Support**: Create and apply standard IPS patches for distributing modifications

## Installation

```bash
pip install -e .
```

## Usage

### Basic Randomization

```python
from randomizer import run_randomization

# Define your randomization spec
spec = {
    "regions": [
        {
            "name": "LevelPointers",
            "offset": 12345,
            "length": 48,
            "op": "shuffle",
            "chunk_size": 2
        },
        {
            "name": "Enemies",
            "offset": 23456,
            "length": 128,
            "op": "replace_values",
            "mapping": {1: 5, 2: 7}
        },
        {
            "name": "Items",
            "offset": 34567,
            "length": 64,
            "op": "randomize_bytes",
            "allowed": [0, 1, 2, 3]
        }
    ]
}

# Load your ROM
with open('smb3.nes', 'rb') as f:
    original_rom = f.read()

# Apply randomization with optional seed for reproducibility
randomized_rom = run_randomization(original_rom, spec, seed=42)

# Save the result
with open('smb3_randomized.nes', 'wb') as f:
    f.write(randomized_rom)
```

### Creating IPS Patches

```python
from ips import make_ips, apply_ips

# Create a patch file from original and modified ROM
make_ips(original_rom, randomized_rom, 'smb3.ips')

# Apply the patch to get modified ROM
patched_rom = apply_ips(original_rom, 'smb3.ips')
```

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

- `offset`: Starting offset in ROM
- `length`: Number of bytes to process
- `mapping`: Dictionary mapping old byte values to new values

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run tests with coverage:

```bash
pytest tests/ --cov=. --cov-report=html
```

## Project Structure

```
smb3-randomizer/
├── __init__.py              # Package initialization
├── randomizer.py            # Core randomization routines
├── ips.py                   # IPS patch utilities
├── setup.py                 # Package configuration
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI workflow
└── tests/
    ├── __init__.py
    ├── test_randomizer.py   # Tests for randomizer module
    └── test_ips.py          # Tests for IPS module
```

## API Reference

### `run_randomization(original_rom, spec, seed=None)`

Apply randomization spec to ROM bytes.

**Parameters:**
- `original_rom` (bytes): The original ROM bytes
- `spec` (dict): Dictionary containing region specifications
- `seed` (int, optional): Seed for reproducible randomization

**Returns:**
- bytes: Modified ROM bytes

**Raises:**
- `ValueError`: If an unknown operation type is specified

### `make_ips(original, modified, out_path)`

Create an IPS patch file from original and modified ROM bytes.

**Parameters:**
- `original` (bytes): Original ROM bytes
- `modified` (bytes): Modified ROM bytes
- `out_path` (str): Path where IPS patch will be written

**Raises:**
- `ValueError`: If original and modified have different lengths

### `apply_ips(rom, ips_path)`

Apply an IPS patch to ROM bytes.

**Parameters:**
- `rom` (bytes): Original ROM bytes
- `ips_path` (str): Path to IPS patch file

**Returns:**
- bytes: Patched ROM bytes

**Raises:**
- `ValueError`: If the file is not a valid IPS file

## Limitations

- IPS patch support does not include Run-Length Encoding (RLE) records
- ROM offset range is limited to 24-bit addressing (max 16MB)
- Chunk size in shuffle operations must evenly divide the region length

## License

MIT License

## Contributing

Contributions are welcome! Please ensure all tests pass and add new tests for any new functionality.
