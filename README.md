# Kindle Book Processing Toolkit

A comprehensive Python toolkit for downloading, processing, and converting Kindle books from Kindle Cloud Reader. This project extracts raw encrypted book data, decodes custom glyphs using advanced image processing, and converts books to standard EPUB format.

## Features

- **Complete Book Download**: Download entire Kindle books from Cloud Reader in batches
- **Advanced Glyph Decoding**: Two-phase glyph processing using perceptual hashing and TTF matching
- **EPUB Generation**: Create properly formatted EPUB files with TOC and styling
- **Font Support**: Includes complete Bookerly font family for accurate rendering
- **Parallel Processing**: Multi-threaded glyph matching for improved performance

## Prerequisites

- Python 3.7+
- Valid Kindle Cloud Reader session (active browser session required)
- Books must be available in your Kindle Cloud Reader library
- Sufficient disk space for book downloads and processing

## Installation

### Recommended: Using uv (Isolated Environment)

1. Clone the repository:
```bash
git clone <repository-url>
cd kindle-book-toolkit
```

2. Install uv if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Create and activate a virtual environment with dependencies:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install pillow cairosvg imagehash svgpathtools fonttools scikit-image tqdm ebooklib requests
```

4. Set up authentication by copying the example headers file:
```bash
cp headers.example.json headers.json
```

5. Edit `headers.json` with your Kindle Cloud Reader session data (see Configuration section).

### Alternative: Using pip

1. Clone the repository:
```bash
git clone <repository-url>
cd kindle-book-toolkit
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required dependencies:
```bash
pip install pillow cairosvg imagehash svgpathtools fonttools scikit-image tqdm ebooklib requests
```

4. Set up authentication by copying the example headers file:
```bash
cp headers.example.json headers.json
```

5. Edit `headers.json` with your Kindle Cloud Reader session data (see Configuration section).

## Quick Start

### Option 1: Using the Wrapper Script (Recommended)

The easiest way to process Kindle books is using the all-in-one wrapper script:

```bash
# Process a single book with default settings
python3 kindle_conversion_wrapper.py B0FLBTR2FS

# Fast mode with auto-confirmation
python3 kindle_conversion_wrapper.py B0FLBTR2FS --fast --yes

# Process multiple books from a list
python3 kindle_conversion_wrapper.py --batch book_list_example.txt

# Custom configuration
python3 kindle_conversion_wrapper.py B0FLBTR2FS --config config.txt
```

### Option 2: Manual Step-by-Step Process

For more control or troubleshooting, you can run each step manually:

#### 1. Download a Complete Book

```bash
# Download entire book (interactive)
python3 download_full_book.py B0FLBTR2FS

# Download with auto-confirmation
python3 download_full_book.py B0FLBTR2FS --yes
```

#### 2. Process and Decode Glyphs

```bash
# Complete glyph processing pipeline
python3 decode_glyphs_complete.py downloads/B0FLBTR2FS

# With optimization flags
python3 decode_glyphs_complete.py downloads/B0FLBTR2FS --fast --progressive
```

#### 3. Create EPUB

```bash
# Convert to EPUB format
python3 create_epub.py downloads/B0FLBTR2FS
```

## Wrapper Script Usage

### `kindle_conversion_wrapper.py` (Recommended)

The wrapper script orchestrates the entire pipeline and provides the easiest way to convert Kindle books.

```bash
python3 kindle_conversion_wrapper.py <ASIN> [options]
python3 kindle_conversion_wrapper.py --batch <book_list_file> [options]
```

**Basic Options:**
- `ASIN`: Amazon book identifier (required for single book processing)
- `--batch FILE`: Process multiple books from a text file
- `--config FILE`: Use custom configuration file
- `--yes`: Auto-confirm all prompts
- `--output-name NAME`: Custom EPUB filename (use `{asin}` as placeholder)

**Processing Modes:**
- `--fast`: Fast decoding mode (early exit on good matches)
- `--full`: Full character set mode (check all font characters)
- `--progressive`: Progressive mode with multi-stage filtering (default)

**Step Control:**
- `--skip-download`: Skip download step (use existing data)
- `--skip-decode`: Skip glyph decoding step
- `--skip-epub`: Skip EPUB creation step

**Examples:**

```bash
# Basic single book processing
python3 kindle_conversion_wrapper.py B0FLBTR2FS

# Fast mode with auto-confirm
python3 kindle_conversion_wrapper.py B0FLBTR2FS --fast --yes

# Custom output filename
python3 kindle_conversion_wrapper.py B0FLBTR2FS --output-name "My Book - {asin}.epub"

# Process multiple books
python3 kindle_conversion_wrapper.py --batch my_books.txt

# Use custom configuration
python3 kindle_conversion_wrapper.py B0FLBTR2FS --config fast_config.txt

# Skip download (if already downloaded)
python3 kindle_conversion_wrapper.py B0FLBTR2FS --skip-download --progressive

# Process with specific steps only
python3 kindle_conversion_wrapper.py B0FLBTR2FS --skip-download --skip-decode
```

### Configuration Files

The wrapper script supports simple key-value configuration files for easy customization:

**Default config.txt:**
```
# Pipeline settings - Download
pipeline.download.enabled = true
pipeline.download.auto_confirm = false

# Pipeline settings - Decode
pipeline.decode.enabled = true
pipeline.decode.mode = progressive

# Pipeline settings - EPUB
pipeline.epub.enabled = true
pipeline.epub.output_name = auto

# Path settings
paths.downloads = downloads
paths.fonts = fonts
paths.output = output

# Batch processing
batch.continue_on_error = true
```

**Custom configurations:**
```bash
# Create custom config for fast processing
cp config.txt fast_config.txt
# Edit fast_config.txt to set:
# pipeline.decode.mode = fast
# pipeline.download.auto_confirm = true

# Use custom config
python3 kindle_conversion_wrapper.py B0FLBTR2FS --config fast_config.txt
```

### Batch Processing

Create a text file with one ASIN per line:

**book_list.txt:**
```
B0FLBTR2FS
B0ABCDEF12
B0GHIJKL34
# Lines starting with # are ignored
```

**Process the batch:**
```bash
python3 kindle_conversion_wrapper.py --batch book_list.txt
```

The wrapper will:
- Process each book sequentially
- Continue with remaining books if one fails (configurable)
- Generate a detailed batch report
- Save individual EPUBs for each successful book

## Detailed Usage

### Individual Command Line Tools

For advanced users or troubleshooting, you can run each component separately:

#### `download_full_book.py`
Downloads complete books in 5-page batches to ensure consistent font encoding.

```bash
python3 download_full_book.py <ASIN> [--yes]
```

**Options:**
- `ASIN`: Amazon book identifier (required)
- `--yes`: Skip confirmation prompt

**Example:**
```bash
python3 download_full_book.py B0FLBTR2FS --yes
```

#### `downloader.py`
Downloads specific page ranges (useful for testing or partial downloads).

```bash
python3 downloader.py <ASIN> [--pages N] [--output DIR] [--start-position POS]
```

**Options:**
- `--pages N`: Number of pages to download (default: 2)
- `--output DIR`: Output directory (default: downloads/<asin>/)
- `--start-position POS`: Override start position

**Examples:**
```bash
python3 downloader.py B0FLBTR2FS --pages 10
python3 downloader.py B0FLBTR2FS --output my_books/ --start-position 1000
```

#### `decode_glyphs_complete.py`
Two-phase glyph decoding: hash-based normalization + TTF character matching.

```bash
python3 decode_glyphs_complete.py <book_dir> [--fast] [--full] [--progressive]
```

**Options:**
- `--fast`: Early exit on good SSIM matches (faster but potentially less accurate)
- `--full`: Check all characters in font files (not just alphanumeric)
- `--progressive`: Multi-stage filtering (128→256→512px) for better accuracy

**Example:**
```bash
python3 decode_glyphs_complete.py downloads/B0FLBTR2FS --progressive --fast
```

#### `create_epub.py`
Converts processed book data to EPUB format with proper formatting and TOC.

```bash
python3 create_epub.py <book_dir>
```

**Example:**
```bash
python3 create_epub.py downloads/B0FLBTR2FS
```

## API Documentation

### KindleDownloader Class

Main class for downloading Kindle books from Cloud Reader.

```python
from downloader import KindleDownloader

downloader = KindleDownloader(cookies_string, adp_session_token=None)
```

#### Methods

**`start_reading(asin)`**
Initialize reading session and get rendering token.
- **Parameters:** `asin` (str) - Book ASIN
- **Returns:** dict - Book metadata including token, revision, srl

**`render_pages(asin, revision, start_position=0, num_pages=2)`**
Download raw page data from Kindle renderer.
- **Parameters:**
  - `asin` (str) - Book ASIN
  - `revision` (str) - Content revision ID
  - `start_position` (int) - Starting position ID
  - `num_pages` (int) - Number of pages to fetch
- **Returns:** bytes - Raw TAR archive containing page data

**`extract_tar(tar_bytes, output_dir)`**
Extract TAR archive to directory.
- **Parameters:**
  - `tar_bytes` (bytes) - Raw TAR data
  - `output_dir` (str) - Directory to extract to
- **Returns:** list - Names of extracted files

**`download(asin, num_pages=2, output_dir=None)`**
Complete download workflow.
- **Parameters:**
  - `asin` (str) - Book ASIN
  - `num_pages` (int) - Number of pages to download
  - `output_dir` (str, optional) - Output directory
- **Returns:** dict - Download metadata

### GlyphHasher Class

Handles SVG glyph rendering and perceptual hashing.

```python
from decode_glyphs_complete import GlyphHasher

hasher = GlyphHasher(size=128)
```

#### Methods

**`render_glyph(glyph_data)`**
Render SVG path as filled shape.
- **Parameters:** `glyph_data` (dict) - Glyph data with path, metrics
- **Returns:** PIL.Image or None

**`compute_hash(img)`**
Compute perceptual hash using average + directional hash.
- **Parameters:** `img` (PIL.Image) - Input image
- **Returns:** str - Combined hash string

### Utility Functions

**`render_glyph_by_name(tt, glyph_name, size=128)`**
Render a glyph by name from TTF font.

**`render_char_from_ttf(tt, char, size=128)`**
Render a character from TTF font.

**`compare_images_ssim(img1, img2)`**
Compare images using Structural Similarity Index.
- **Returns:** float - Distance (0=identical, higher=more different)

## Configuration

### Authentication Setup

1. Open Kindle Cloud Reader in your browser and log in
2. Open browser developer tools (F12)
3. Go to Network tab and refresh the page
4. Find a request to `read.amazon.com` and copy:
   - All cookies from the Cookie header
   - The `x-adp-session-token` header value (if present)

5. Edit `headers.json`:

```json
{
  "headers": {
    "x-adp-session-token": "your_token_here"
  },
  "cookies": "session-id=123-456; session-id-time=789; ubid-main=456; at-main=token; sess-at-main=token; x-main=value"
}
```

### Font Configuration

The toolkit expects Bookerly fonts in the `fonts/` directory:
- Bookerly.ttf (regular)
- Bookerly Bold.ttf
- Bookerly Italic.ttf
- Bookerly Bold Italic.ttf
- Additional Bookerly variants

These fonts are used for accurate glyph matching during the decoding process.

### Processing Options

**Glyph Matching Modes:**
- **Standard Mode**: Checks predefined character set (ASCII + common symbols)
- **Full Mode** (`--full`): Checks all characters available in font files
- **Fast Mode** (`--fast`): Early exit on confident matches
- **Progressive Mode** (`--progressive`): Multi-resolution filtering for accuracy

## File Structure

After processing, your directory structure will look like:

```
downloads/
└── B0FLBTR2FS/
    ├── batch_0/                 # Front matter (TOC, cover)
    │   ├── page_data_*.json
    │   ├── glyphs.json
    │   ├── metadata.json
    │   └── toc.json
    ├── batch_1/                 # Main content batches
    ├── batch_2/
    ├── hash_mapping/            # Glyph processing results
    │   ├── hash_info.json
    │   ├── all_glyphs.json
    │   └── glyph_images/
    ├── karamel_token.json       # For image decryption
    └── download_info.json       # Download metadata

ttf_character_mapping.json       # Final character mapping
decoded_book.epub               # Generated EPUB file
```

## Troubleshooting

### Authentication Issues

**"headers.json not found"**
- Copy `headers.example.json` to `headers.json`
- Add your session cookies and tokens

**"Invalid or expired credentials"**
- Refresh your Kindle Cloud Reader session
- Update cookies in `headers.json`
- Ensure the book is in your library

**"No 'x-adp-session-token' found"**
- This token may not be required for all books
- Try without it first; add only if downloads fail

### Download Problems

**"Network request failed"**
- Check internet connection
- Verify ASIN format (should be like "B0FLBTR2FS")
- Ensure book is available in your region

**"No page data found"**
- Book may have DRM protection preventing download
- Try a different book to test your setup
- Check if book is available for download vs. streaming only

### Glyph Processing Issues

**"Missing dependencies"**
```bash
# With uv:
uv pip install pillow cairosvg imagehash svgpathtools fonttools scikit-image tqdm

# With pip:
pip install pillow cairosvg imagehash svgpathtools fonttools scikit-image tqdm
```

**"Font files not found"**
- Ensure Bookerly fonts are in `fonts/` directory
- Check font file permissions
- Verify font files are not corrupted

**"Low matching accuracy"**
- Try `--progressive` mode for better accuracy
- Use `--full` mode to check more characters
- Verify font files match the book's font family

### EPUB Creation Issues

**"No character mapping found"**
- Run `decode_glyphs_complete.py` first
- Ensure `ttf_character_mapping.json` exists

**"Missing ebooklib"**
```bash
# With uv:
uv pip install ebooklib

# With pip:
pip install ebooklib
```

## Wrapper Script Features

### Pipeline Orchestration
- **Sequential Processing**: Automatically runs download → decode → EPUB creation
- **Error Handling**: Stops on failures with detailed error messages
- **Progress Tracking**: Shows step-by-step progress with timing information
- **Cleanup**: Automatically removes partial files on failure

### Configuration Management
- **Simple Config Support**: Flexible configuration files with sensible defaults
- **CLI Overrides**: Command line options override configuration settings
- **Multiple Configs**: Support for different configuration profiles

### Batch Processing
- **Multiple Books**: Process entire libraries from text file lists
- **Error Recovery**: Continue processing remaining books if one fails
- **Batch Reports**: Detailed success/failure reports with timestamps
- **Progress Tracking**: Shows current book progress in batch

### Advanced Features
- **Step Control**: Skip individual pipeline steps as needed
- **Custom Naming**: Flexible EPUB output naming with ASIN placeholders
- **Prerequisites Check**: Validates environment before processing
- **Comprehensive Logging**: Detailed output for troubleshooting

### Workflow Examples

**Development/Testing Workflow:**
```bash
# Test with a single book first
python3 kindle_conversion_wrapper.py B0FLBTR2FS --fast --yes

# If successful, process your library
python3 kindle_conversion_wrapper.py --batch my_library.txt --config production.txt
```

**Incremental Processing:**
```bash
# Download only (for later processing)
python3 kindle_conversion_wrapper.py B0FLBTR2FS --skip-decode --skip-epub

# Process existing download
python3 kindle_conversion_wrapper.py B0FLBTR2FS --skip-download
```

**Custom Output Organization:**
```bash
# Organized naming scheme
python3 kindle_conversion_wrapper.py B0FLBTR2FS --output-name "Converted/{title}-{author}.epub"
```

## Performance Tips

1. **Use Progressive Mode**: `--progressive` provides better accuracy with reasonable speed
2. **Parallel Processing**: The toolkit automatically uses all CPU cores
3. **Disk Space**: Ensure sufficient space (books can be 100MB+ when processed)
4. **Memory Usage**: Large books may require 4GB+ RAM during processing
5. **Batch Processing**: Use wrapper script for multiple books to avoid repeated setup overhead
6. **Configuration Files**: Create optimized configs for different use cases (fast vs. accurate)

## Dependencies

### Required Python Packages

**With uv (recommended):**
```bash
uv pip install pillow cairosvg imagehash svgpathtools fonttools scikit-image tqdm ebooklib requests
```

**With pip:**
```bash
pip install pillow cairosvg imagehash svgpathtools fonttools scikit-image tqdm ebooklib requests
```

**Note:** The wrapper script uses a simple key-value configuration format with no additional dependencies.

### System Requirements

- **Python**: 3.7 or higher
- **Memory**: 4GB+ recommended for large books
- **Storage**: 500MB+ free space per book
- **CPU**: Multi-core recommended for faster processing

## Legal Notice

**Important**: This toolkit is for educational and personal use only.

### Requirements:
- You must own legitimate copies of all books processed
- Comply with Amazon's Terms of Service
- Respect copyright laws and DRM policies
- Use only for personal backup and format conversion
- Do not distribute processed content

### Limitations:
- Some books may have additional DRM protection
- Not all Kindle features (annotations, X-Ray) are preserved
- Image quality may vary depending on source resolution

## Contributing

We welcome contributions! Please follow these guidelines:

### Development Setup

1. Fork the repository
2. Create a virtual environment:
```bash
# With uv (recommended):
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# With pip:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
3. Install development dependencies
4. Create a feature branch

### Code Standards

- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Include type hints where appropriate
- Write unit tests for new functionality
- Update documentation for API changes

### Pull Request Process

1. Ensure all tests pass
2. Update README.md if needed
3. Add entry to CHANGELOG.md
4. Submit pull request with clear description

## License

This project is provided for educational and research purposes. Users are responsible for ensuring compliance with all applicable laws, terms of service, and copyright regulations.

## Support

### Getting Help

1. **Check Documentation**: Review this README and inline code comments
2. **Search Issues**: Look for similar problems in the issue tracker
3. **Create Issue**: Provide detailed information including:
   - Python version and OS
   - Complete error messages
   - Steps to reproduce the problem
   - Sample ASIN (if not sensitive)
   - Whether using wrapper script or individual tools

### Common Solutions

- **Authentication**: Most issues stem from expired or incorrect session data
- **Dependencies**: Ensure all required packages are installed with correct versions
- **Permissions**: Check file/directory permissions if seeing access errors
- **Wrapper Issues**: Try running individual scripts manually to isolate problems

### Wrapper Script Troubleshooting

**"Required script not found"**
- Ensure all Python scripts are in the same directory
- Check that script names match exactly

**"Configuration file error"**
- Check config file syntax (key = value format)
- Ensure no spaces around the = sign
- Verify boolean values are lowercase (true/false)

**"Batch processing fails"**
- Check book list file format (one ASIN per line)
- Verify ASINs are valid
- Use `--config` with `continue_on_error: true` to process remaining books

**"Pipeline step fails"**
- Use individual scripts to isolate the problem
- Check prerequisites for each step
- Review error messages for specific issues

---

**Disclaimer**: This software is not affiliated with Amazon or Kindle. Use responsibly and in accordance with applicable laws and terms of service.
