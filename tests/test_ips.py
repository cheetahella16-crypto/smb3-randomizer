"""Tests for the IPS module."""
import pytest
import tempfile
import os
from ips import make_ips, apply_ips


class TestMakeIPS:
    """Tests for make_ips function."""
    
    def test_make_ips_no_differences(self):
        """Test IPS creation when files are identical."""
        original = b'\x01\x02\x03\x04'
        modified = b'\x01\x02\x03\x04'
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
        try:
            make_ips(original, modified, temp_path)
            with open(temp_path, 'rb') as f:
                content = f.read()
            # Should contain just PATCH and EOF
            assert content == b'PATCHEOF'
        finally:
            os.unlink(temp_path)
    
    def test_make_ips_single_byte_difference(self):
        """Test IPS creation with single byte difference."""
        original = b'\x01\x02\x03\x04'
        modified = b'\x01\xFF\x03\x04'
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
        try:
            make_ips(original, modified, temp_path)
            with open(temp_path, 'rb') as f:
                content = f.read()
            # Should have PATCH + record + EOF
            assert content.startswith(b'PATCH')
            assert content.endswith(b'EOF')
            assert b'\xFF' in content
        finally:
            os.unlink(temp_path)
    
    def test_make_ips_multiple_differences(self):
        """Test IPS creation with multiple byte differences."""
        original = b'\x01\x02\x03\x04\x05\x06'
        modified = b'\x01\xFF\x03\xFF\x05\x06'
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
        try:
            make_ips(original, modified, temp_path)
            with open(temp_path, 'rb') as f:
                content = f.read()
            assert content.startswith(b'PATCH')
            assert content.endswith(b'EOF')
        finally:
            os.unlink(temp_path)
    
    def test_make_ips_length_mismatch(self):
        """Test that length mismatch raises ValueError."""
        original = b'\x01\x02'
        modified = b'\x01\x02\x03'
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
        try:
            with pytest.raises(ValueError, match="same length"):
                make_ips(original, modified, temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestApplyIPS:
    """Tests for apply_ips function."""
    
    def test_apply_ips_empty_patch(self):
        """Test applying an empty patch."""
        rom = b'\x01\x02\x03\x04'
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
            f.write(b'PATCHEOF')
        try:
            result = apply_ips(rom, temp_path)
            assert result == rom
        finally:
            os.unlink(temp_path)
    
    def test_apply_ips_single_record(self):
        """Test applying a patch with single record."""
        rom = b'\x01\x02\x03\x04'
        # Create patch: offset=1, size=1, data=\xFF
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
            f.write(b'PATCH')
            f.write((1).to_bytes(3, 'big'))  # offset
            f.write((1).to_bytes(2, 'big'))  # size
            f.write(b'\xFF')  # data
            f.write(b'EOF')
        try:
            result = apply_ips(rom, temp_path)
            assert result == b'\x01\xFF\x03\x04'
        finally:
            os.unlink(temp_path)
    
    def test_apply_ips_invalid_header(self):
        """Test that invalid header raises ValueError."""
        rom = b'\x01\x02\x03'
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
            f.write(b'NOIPS')  # Invalid header
        try:
            with pytest.raises(ValueError, match="Not an IPS file"):
                apply_ips(rom, temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_apply_ips_extends_rom(self):
        """Test that patch can extend ROM size."""
        rom = b'\x01\x02'
        # Create patch: offset=5, size=2, data=\xFF\xFF
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
            f.write(b'PATCH')
            f.write((5).to_bytes(3, 'big'))  # offset
            f.write((2).to_bytes(2, 'big'))  # size
            f.write(b'\xFF\xFF')  # data
            f.write(b'EOF')
        try:
            result = apply_ips(rom, temp_path)
            # Should be padded with zeros
            assert len(result) == 7
            assert result == b'\x01\x02\x00\x00\x00\xFF\xFF'
        finally:
            os.unlink(temp_path)
    
    def test_make_and_apply_ips_roundtrip(self):
        """Test roundtrip: create patch from diff, apply to original."""
        original = b'\x01\x02\x03\x04\x05\x06'
        modified = b'\x01\xFF\x03\xFF\x05\x06'
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
        try:
            make_ips(original, modified, temp_path)
            result = apply_ips(original, temp_path)
            assert result == modified
        finally:
            os.unlink(temp_path)
