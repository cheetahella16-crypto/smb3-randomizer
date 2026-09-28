"""Command-line interface for the SMB3 randomizer.

Usage examples:
  python cli.py --rom path/to/smb3.nes --mapping mappings/smb3_example.json --out patch.ips --seed 42

This tool does not distribute or modify any ROMs itself; the user must
provide a legal dump of their SMB3 ROM to generate a patch.
"""
import argparse
import json
import sys
from pathlib import Path
from randomizer import run_randomization
from ips import make_ips


def validate_mapping(spec):
    """Validate that the mapping specification is well-formed.
    
    Args:
        spec (dict): The mapping specification.
        
    Raises:
        ValueError: If the spec is invalid.
    """
    if not isinstance(spec, dict):
        raise ValueError("Mapping must be a JSON object")
    
    if "regions" not in spec:
        raise ValueError("Mapping must contain a 'regions' key")
    
    if not isinstance(spec["regions"], list):
        raise ValueError("'regions' must be a list")
    
    if not spec["regions"]:
        raise ValueError("'regions' cannot be empty")
    
    for i, region in enumerate(spec["regions"]):
        if not isinstance(region, dict):
            raise ValueError(f"Region {i} must be a dictionary")
        
        required_fields = {"offset", "length", "op"}
        missing = required_fields - set(region.keys())
        if missing:
            raise ValueError(f"Region {i} missing required fields: {missing}")
        
        valid_ops = {"shuffle", "randomize_bytes", "replace_values"}
        if region["op"] not in valid_ops:
            raise ValueError(f"Region {i} has invalid op '{region['op']}'. Must be one of: {valid_ops}")


def main():
    p = argparse.ArgumentParser(
        description="SMB3 randomizer - generates an IPS patch from a ROM and a mapping spec",
        epilog="Example: python cli.py --rom smb3.nes --mapping mappings/smb3_example.json --out patch.ips --seed 42"
    )
    p.add_argument("--rom", required=True, help="Path to source SMB3 .nes ROM (legal user-owned dump)")
    p.add_argument("--mapping", required=True, help="JSON mapping/spec file describing regions to randomize")
    p.add_argument("--out", required=True, help="Output IPS patch path")
    p.add_argument("--seed", type=int, default=None, help="Optional seed for deterministic randomization")
    p.add_argument("--write-rom", help="Optional path to write the full modified ROM (for testing)")
    args = p.parse_args()

    try:
        # Load ROM
        rom_path = Path(args.rom)
        if not rom_path.exists():
            print(f"Error: ROM file not found: {args.rom}", file=sys.stderr)
            sys.exit(1)
        
        with open(rom_path, "rb") as f:
            original = f.read()
        
        if not original:
            print(f"Error: ROM file is empty: {args.rom}", file=sys.stderr)
            sys.exit(1)
        
        # Load mapping
        mapping_path = Path(args.mapping)
        if not mapping_path.exists():
            print(f"Error: Mapping file not found: {args.mapping}", file=sys.stderr)
            sys.exit(1)
        
        try:
            with open(mapping_path, "r", encoding="utf-8") as f:
                spec = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in mapping file: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Validate mapping
        try:
            validate_mapping(spec)
        except ValueError as e:
            print(f"Error: Invalid mapping specification: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Run randomization
        try:
            print(f"Randomizing ROM with seed {args.seed}...")
            modified = run_randomization(original, spec, seed=args.seed)
        except ValueError as e:
            print(f"Error: Randomization failed: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: Unexpected error during randomization: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Create IPS patch
        try:
            print(f"Creating IPS patch...")
            make_ips(original, modified, args.out)
            print(f"✓ Wrote IPS patch to: {args.out}")
        except ValueError as e:
            print(f"Error: Failed to create IPS patch: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: Unexpected error creating IPS patch: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Optionally write modified ROM
        if args.write_rom:
            try:
                with open(args.write_rom, "wb") as f:
                    f.write(modified)
                print(f"✓ Wrote modified ROM to: {args.write_rom}")
            except Exception as e:
                print(f"Error: Failed to write modified ROM: {e}", file=sys.stderr)
                sys.exit(1)
        
        print("Done!")
    
    except KeyboardInterrupt:
        print("\nAborted by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
