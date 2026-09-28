# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-28

### Added
- Initial release of SMB3 Randomizer framework
- Three core randomization operations:
  - **Shuffle**: Randomize order of fixed-size chunks within a region
  - **Randomize Bytes**: Replace bytes with random values from an allowed set
  - **Replace Values**: Map specific byte values to new values
- IPS patch creation and application support
- Full command-line interface with robust error handling
- Comprehensive input validation for mapping specifications
- 22 test cases covering all functionality (14 for randomizer, 8 for IPS)
- Complete documentation with API reference and examples
- Example mapping file for reference

### Fixed
- Critical EOF detection bug in IPS patch application
- Bounds checking in randomization operations to prevent out-of-range access
- Proper error messages for invalid mapping specifications

### Security
- Input validation to reject invalid mappings
- Error handling to prevent uncontrolled exceptions
- Safe temporary file handling in file operations

## [Unreleased]

### Planned
- Support for Run-Length Encoding (RLE) in IPS patches
- GUI for mapping file creation
- More example mappings for common SMB3 modifications
- Performance optimizations for large ROMs
