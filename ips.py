"""Simple IPS patch writer/reader utilities.

IPS (International Patching System) is a standard format for ROM patches.
This module provides basic support for creating and applying IPS patches.
Note: RLE (Run-Length Encoding) records are not supported in this implementation.
"""
from typing import List


def make_ips(original: bytes, modified: bytes, out_path: str) -> None:
    """Create a simple IPS patch file from original and modified ROM bytes.

    Only supports straightforward non-RLE records (size > 0). For most small
    hacks this is sufficient. If a generated record would require RLE this
    function will still emit it as a normal record.
    
    Args:
        original: The original ROM bytes.
        modified: The modified ROM bytes.
        out_path: Path where the IPS patch file will be written.
        
    Raises:
        ValueError: If original and modified have different lengths.
    """
    if len(original) != len(modified):
        raise ValueError("original and modified must be same length")

    records = []
    i = 0
    n = len(original)
    while i < n:
        if original[i] == modified[i]:
            i += 1
            continue
        # start of diff
        start = i
        chunk = bytearray()
        while i < n and original[i] != modified[i] and len(chunk) < 0xFFFF:
            chunk.append(modified[i])
            i += 1
        records.append((start, bytes(chunk)))

    with open(out_path, "wb") as f:
        f.write(b"PATCH")
        for offset, data in records:
            # 3-byte offset (big-endian)
            f.write(offset.to_bytes(3, "big"))
            # 2-byte size
            f.write(len(data).to_bytes(2, "big"))
            f.write(data)
        f.write(b"EOF")


def apply_ips(rom: bytes, ips_path: str) -> bytes:
    """Apply an IPS patch to rom bytes and return patched bytes.

    Minimal IPS parser supporting basic records produced by make_ips.
    Note: RLE (Run-Length Encoding) records are not supported.
    
    Args:
        rom: The original ROM bytes.
        ips_path: Path to the IPS patch file.
        
    Returns:
        Patched ROM bytes.
        
    Raises:
        ValueError: If the file is not a valid IPS patch.
    """
    data = bytearray(rom)
    with open(ips_path, "rb") as f:
        header = f.read(5)
        if header != b"PATCH":
            raise ValueError("Not an IPS file")
        while True:
            pos = f.read(3)
            if not pos or pos == b"EOF":
                break
            offset = int.from_bytes(pos, "big")
            size = int.from_bytes(f.read(2), "big")
            chunk = f.read(size)
            # ensure length
            if offset + size > len(data):
                data.extend(b"\x00" * (offset + size - len(data)))
            data[offset:offset+size] = chunk
    return bytes(data)
