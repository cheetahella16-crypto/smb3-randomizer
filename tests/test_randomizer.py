"""Tests for the randomizer module."""
import pytest
from randomizer import run_randomization, shuffle_region, randomize_bytes, replace_values


class TestShuffleRegion:
    """Tests for shuffle_region function."""
    
    def test_shuffle_region_basic(self):
        """Test basic shuffling functionality."""
        rom = bytearray(b'\x01\x02\x03\x04\x05\x06')
        import random
        rng = random.Random(42)
        shuffle_region(rom, 0, 6, 2, rng)
        # With seed 42, we should get a deterministic result
        assert len(rom) == 6
        assert rom != bytearray(b'\x01\x02\x03\x04\x05\x06')  # Should be shuffled
    
    def test_shuffle_region_invalid_chunk_size(self):
        """Test that invalid chunk size raises ValueError."""
        rom = bytearray(b'\x01\x02\x03\x04')
        import random
        rng = random.Random()
        with pytest.raises(ValueError, match="divisible by chunk_size"):
            shuffle_region(rom, 0, 4, 3, rng)
    
    def test_shuffle_region_out_of_bounds(self):
        """Test that out of bounds access raises ValueError."""
        rom = bytearray(b'\x01\x02\x03\x04')
        import random
        rng = random.Random()
        with pytest.raises(ValueError, match="Region extends beyond ROM"):
            shuffle_region(rom, 0, 10, 2, rng)


class TestRandomizeBytes:
    """Tests for randomize_bytes function."""
    
    def test_randomize_bytes_basic(self):
        """Test basic randomization functionality."""
        rom = bytearray(b'\x00\x00\x00\x00')
        import random
        rng = random.Random(42)
        randomize_bytes(rom, 0, 4, [1, 2, 3], rng)
        # All bytes should be replaced with values from allowed list
        assert all(b in [1, 2, 3] for b in rom)
    
    def test_randomize_bytes_single_value(self):
        """Test randomization with single allowed value."""
        rom = bytearray(b'\x00\x00\x00\x00')
        import random
        rng = random.Random()
        randomize_bytes(rom, 0, 4, [5], rng)
        assert rom == bytearray(b'\x05\x05\x05\x05')


class TestReplaceValues:
    """Tests for replace_values function."""
    
    def test_replace_values_basic(self):
        """Test basic value replacement."""
        rom = bytearray(b'\x01\x02\x03\x02\x01')
        mapping = {1: 10, 2: 20}
        replace_values(rom, 0, 5, mapping)
        assert rom == bytearray(b'\x0a\x14\x03\x14\x0a')
    
    def test_replace_values_no_matches(self):
        """Test replacement when no values match."""
        rom = bytearray(b'\x01\x02\x03')
        mapping = {5: 10, 6: 20}
        replace_values(rom, 0, 3, mapping)
        assert rom == bytearray(b'\x01\x02\x03')  # Unchanged
    
    def test_replace_values_partial_region(self):
        """Test replacement in partial region."""
        rom = bytearray(b'\x01\x02\x03\x04\x05')
        mapping = {2: 20, 3: 30}
        replace_values(rom, 1, 2, mapping)
        assert rom == bytearray(b'\x01\x14\x1e\x04\x05')


class TestRunRandomization:
    """Tests for run_randomization function."""
    
    def test_run_randomization_shuffle(self):
        """Test randomization with shuffle operation."""
        rom = b'\x01\x02\x03\x04\x05\x06'
        spec = {
            "regions": [
                {"name": "test", "offset": 0, "length": 6, "op": "shuffle", "chunk_size": 2}
            ]
        }
        result = run_randomization(rom, spec, seed=42)
        assert len(result) == len(rom)
        assert result != rom
    
    def test_run_randomization_randomize_bytes(self):
        """Test randomization with randomize_bytes operation."""
        rom = b'\x00\x00\x00\x00'
        spec = {
            "regions": [
                {"name": "test", "offset": 0, "length": 4, "op": "randomize_bytes", "allowed": [1, 2]}
            ]
        }
        result = run_randomization(rom, spec, seed=42)
        assert all(b in [1, 2] for b in result)
    
    def test_run_randomization_replace_values(self):
        """Test randomization with replace_values operation."""
        rom = b'\x01\x02\x03'
        spec = {
            "regions": [
                {"name": "test", "offset": 0, "length": 3, "op": "replace_values", "mapping": {1: 10, 2: 20}}
            ]
        }
        result = run_randomization(rom, spec)
        assert result == b'\x0a\x14\x03'
    
    def test_run_randomization_unknown_op(self):
        """Test that unknown operation raises ValueError."""
        rom = b'\x01\x02'
        spec = {
            "regions": [
                {"name": "test", "offset": 0, "length": 2, "op": "unknown_op"}
            ]
        }
        with pytest.raises(ValueError, match="Unknown op type"):
            run_randomization(rom, spec)
    
    def test_run_randomization_multiple_regions(self):
        """Test randomization with multiple regions."""
        rom = b'\x01\x02\x03\x04\x05\x06'
        spec = {
            "regions": [
                {"name": "r1", "offset": 0, "length": 2, "op": "replace_values", "mapping": {1: 10}},
                {"name": "r2", "offset": 2, "length": 2, "op": "replace_values", "mapping": {3: 30}}
            ]
        }
        result = run_randomization(rom, spec)
        assert result == b'\x0a\x02\x1e\x04\x05\x06'
    
    def test_run_randomization_deterministic_seed(self):
        """Test that same seed produces same results."""
        rom = b'\x00\x00\x00\x00\x00\x00'
        spec = {
            "regions": [
                {"name": "test", "offset": 0, "length": 6, "op": "shuffle", "chunk_size": 2}
            ]
        }
        result1 = run_randomization(rom, spec, seed=123)
        result2 = run_randomization(rom, spec, seed=123)
        assert result1 == result2
