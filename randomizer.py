"""Core randomization routines for a ROM-based randomizer.

This module implements a small, generic framework driven by a mapping JSON.
For Super Mario Bros 3 you can supply a mapping that lists ROM regions and an
operation for each region (shuffle, randomize_bytes, replace_values). The
randomizer will produce modified ROM bytes which can then be written or
exported as an IPS patch.
"""
from typing import Dict, Any, List
import random


def shuffle_region(rom: bytearray, offset: int, length: int, chunk_size: int, rng: random.Random):
    """Shuffle chunks of a ROM region.
    
    Args:
        rom: The ROM buffer to modify.
        offset: Starting offset in the ROM.
        length: Number of bytes to shuffle.
        chunk_size: Size of each chunk to shuffle.
        rng: Random number generator instance.
        
    Raises:
        ValueError: If chunk_size is invalid or region extends beyond ROM.
    """
    if chunk_size <= 0 or length % chunk_size != 0:
        raise ValueError(f"length ({length}) must be divisible by chunk_size ({chunk_size})")
    
    if offset + length > len(rom):
        raise ValueError(f"Region extends beyond ROM: offset={offset}, length={length}, rom_size={len(rom)}")
    
    end = offset + length
    chunks = [rom[offset + i: offset + i + chunk_size] for i in range(0, length, chunk_size)]
    rng.shuffle(chunks)
    i = offset
    for c in chunks:
        rom[i:i+chunk_size] = c
        i += chunk_size


def randomize_bytes(rom: bytearray, offset: int, length: int, allowed: List[int], rng: random.Random):
    """Randomize bytes in a ROM region with allowed values.
    
    Args:
        rom: The ROM buffer to modify.
        offset: Starting offset in the ROM.
        length: Number of bytes to randomize.
        allowed: List of allowed byte values.
        rng: Random number generator instance.
    """
    for i in range(offset, offset + length):
        rom[i] = rng.choice(allowed)


def replace_values(rom: bytearray, offset: int, length: int, mapping: Dict[int, int]):
    """Replace byte values in a ROM region according to a mapping.
    
    Args:
        rom: The ROM buffer to modify.
        offset: Starting offset in the ROM.
        length: Number of bytes to process.
        mapping: Dictionary mapping old byte values to new byte values.
    """
    for i in range(offset, offset + length):
        b = rom[i]
        if b in mapping:
            rom[i] = mapping[b]


def run_randomization(original_rom: bytes, spec: Dict[str, Any], seed: int = None) -> bytes:
    """Apply the given spec to original_rom and return modified bytes.

    Spec format:
    {
      "regions": [
         {"name":"LevelPointers","offset":12345,"length":48,"op":"shuffle","chunk_size":2},
         {"name":"Enemies","offset":23456,"length":128,"op":"replace_values","mapping":{1:5,2:7}},
         {"name":"Items","offset":34567,"length":64,"op":"randomize_bytes","allowed":[0,1,2,3]}
      ]
    }

    The offsets/lengths are raw ROM offsets (0-based). This function is ROM-format
    agnostic and works with any bytes buffer.
    
    Args:
        original_rom: The original ROM bytes.
        spec: Dictionary containing region specifications.
        seed: Optional seed for reproducible randomization.
        
    Returns:
        Modified ROM bytes.
        
    Raises:
        ValueError: If an unknown operation type is specified.
    """
    rom = bytearray(original_rom)
    rng = random.Random(seed)

    for region in spec.get("regions", []):
        op = region.get("op")
        offset = int(region["offset"])
        length = int(region["length"])
        if op == "shuffle":
            chunk_size = int(region.get("chunk_size", 1))
            shuffle_region(rom, offset, length, chunk_size, rng)
        elif op == "randomize_bytes":
            allowed = region.get("allowed")
            if allowed is None:
                # allow any byte
                allowed = list(range(256))
            else:
                allowed = [int(x) for x in allowed]
            randomize_bytes(rom, offset, length, allowed, rng)
        elif op == "replace_values":
            mapping = {int(k): int(v) for k, v in region.get("mapping", {}).items()}
            replace_values(rom, offset, length, mapping)
        else:
            raise ValueError(f"Unknown op type: {op}")

    return bytes(rom)
