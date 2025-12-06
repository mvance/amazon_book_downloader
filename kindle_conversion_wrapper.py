#!/usr/bin/env python3
"""
Kindle Conversion Wrapper
Complete pipeline for downloading, decoding, and converting Kindle books to EPUB

Combines:
1. Simple Sequential Wrapper - orchestrates all steps
2. Configuration-Driven Approach - YAML config with CLI overrides
3. Batch Processing - handle multiple books
4. Error Recovery and Cleanup - basic error handling

Usage:
    python3 kindle_conversion_wrapper.py B0FLBTR2FS
    python3 kindle_conversion_wrapper.py --batch book_list.txt
    python3 kindle_conversion_wrapper.py B0FLBTR2FS --config custom_config.yaml --fast
"""

import sys
import json
import subprocess
import shutil
import time
from pathlib import Path
import argparse
from datetime import datetime


class KindleProcessor:
    """Main processor class that orchestrates the entire pipeline"""
    
    def __init__(self, asin, config):
        self.asin = asin
        self.config = config
        self.book_dir = Path(config['paths']['downloads']) / asin
        self.start_time = time.time()
        
    def run_pipeline(self):
        """Execute complete pipeline with error handling"""
        print(f"\n{'='*80}")
        print(f"PROCESSING KINDLE BOOK: {self.asin}")
        print(f"{'='*80}")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        steps = []
        
        # Build step list based on config
        if self.config['pipeline']['download']['enabled']:
            steps.append(("Download Book", self.download_book))
            
        if self.config['pipeline']['decode']['enabled']:
            steps.append(("Decode Glyphs", self.decode_glyphs))
            
        if self.config['pipeline']['epub']['enabled']:
            steps.append(("Create EPUB", self.create_epub))
        
        # Execute each step
        for i, (step_name, step_func) in enumerate(steps, 1):
            print(f"\n{'='*60}")
            print(f"STEP {i}/{len(steps)}: {step_name}")
            print(f"{'='*60}")
            
            step_start = time.time()
            
            try:
                step_func()
                step_duration = time.time() - step_start
                print(f"✅ {step_name} completed successfully in {step_duration:.1f}s")
                
            except subprocess.CalledProcessError as e:
                print(f"❌ {step_name} failed with exit code {e.returncode}")
                print(f"Command: {' '.join(e.cmd)}")
                if e.stdout:
                    print(f"Output: {e.stdout}")
                if e.stderr:
                    print(f"Error: {e.stderr}")
                self.cleanup_on_failure()
                raise
                
            except Exception as e:
                print(f"❌ {step_name} failed: {e}")
                self.cleanup_on_failure()
                raise
        
        # Success summary
        total_duration = time.time() - self.start_time
        print(f"\n{'='*80}")
        print(f"✅ PIPELINE COMPLETED SUCCESSFULLY!")
        print(f"{'='*80}")
        print(f"Book: {self.asin}")
        print(f"Total time: {total_duration:.1f}s")
        print(f"Output directory: {self.book_dir}")
        
        # Show final EPUB location
        epub_file = Path("decoded_book.epub")
        if epub_file.exists():
            print(f"EPUB file: {epub_file.absolute()}")
        
    def download_book(self):
        """Download complete book using download_full_book.py"""
        cmd = ["python3", "download_full_book.py", self.asin]
        
        # Add auto-confirm if configured
        if self.config['pipeline']['download']['auto_confirm']:
            cmd.append("--yes")
            
        print(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("Download output:")
        print(result.stdout)
        
        # Verify download succeeded
        if not self.book_dir.exists():
            raise Exception(f"Download failed - book directory not created: {self.book_dir}")
            
        batch_dirs = list(self.book_dir.glob("batch_*"))
        if not batch_dirs:
            raise Exception("Download failed - no batch directories found")
            
        print(f"✓ Downloaded {len(batch_dirs)} batches to {self.book_dir}")
        
    def decode_glyphs(self):
        """Decode glyphs using decode_glyphs_complete.py"""
        cmd = ["python3", "decode_glyphs_complete.py", str(self.book_dir)]
        
        # Add decode options from config
        decode_config = self.config['pipeline']['decode']
        
        if decode_config['mode'] == 'fast':
            cmd.append("--fast")
        elif decode_config['mode'] == 'full':
            cmd.append("--full")
        elif decode_config['mode'] == 'progressive':
            cmd.append("--progressive")
            
        print(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("Decode output:")
        print(result.stdout)
        
        # Verify decode succeeded
        mapping_file = Path("ttf_character_mapping.json")
        if not mapping_file.exists():
            raise Exception("Decode failed - character mapping file not created")
            
        print(f"✓ Character mapping created: {mapping_file}")
        
    def create_epub(self):
        """Create EPUB using create_epub.py"""
        cmd = ["python3", "create_epub.py", str(self.book_dir)]
        
        print(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print("EPUB creation output:")
        print(result.stdout)
        
        # Verify EPUB was created
        epub_file = Path("decoded_book.epub")
        if not epub_file.exists():
            raise Exception("EPUB creation failed - output file not found")
            
        # Get book title from metadata for naming
        metadata_file = self.book_dir / 'batch_0' / 'metadata.json'
        if metadata_file.exists():
            with open(metadata_file) as f:
                metadata = json.load(f)
            book_title = metadata.get('bookTitle', self.asin)
            # Clean title for filename (remove invalid characters)
            import re
            clean_title = re.sub(r'[<>:"/\\|?*]', '', book_title)
            clean_title = clean_title.strip()
        else:
            clean_title = self.asin
        
        # Rename EPUB based on config
        output_name = self.config['pipeline']['epub']['output_name']
        if output_name == "auto":
            # Use title automatically
            custom_name = f"{clean_title}.epub"
        else:
            # Use configured name with placeholders
            custom_name = output_name.replace("{asin}", self.asin).replace("{title}", clean_title)
            if not custom_name.endswith('.epub'):
                custom_name += '.epub'
        
        custom_path = Path(custom_name)
        epub_file.rename(custom_path)
        print(f"✓ EPUB created: {custom_path}")
            
    def cleanup_on_failure(self):
        """Clean up partial files on failure"""
        print("\n🧹 Cleaning up partial files...")
        
        # Remove incomplete batch directories
        if self.book_dir.exists():
            batch_dirs = list(self.book_dir.glob("batch_*"))
            for batch_dir in batch_dirs:
                if not self.is_complete_batch(batch_dir):
                    print(f"  Removing incomplete batch: {batch_dir}")
                    shutil.rmtree(batch_dir, ignore_errors=True)
        
        # Remove partial mapping files
        partial_files = [
            "ttf_character_mapping.json",
            "decoded_book.epub"
        ]
        
        for file_path in partial_files:
            path = Path(file_path)
            if path.exists():
                print(f"  Removing partial file: {path}")
                path.unlink(missing_ok=True)
                
    def is_complete_batch(self, batch_dir):
        """Check if a batch directory is complete"""
        required_files = ["page_data_*.json"]
        
        for pattern in required_files:
            if not list(batch_dir.glob(pattern)):
                return False
        return True


class BatchProcessor:
    """Handles processing multiple books from a list"""
    
    def __init__(self, book_list_file, config):
        self.book_list_file = Path(book_list_file)
        self.config = config
        
    def process_batch(self):
        """Process all books in the list"""
        # Load book list
        if not self.book_list_file.exists():
            raise FileNotFoundError(f"Book list file not found: {self.book_list_file}")
            
        with open(self.book_list_file) as f:
            asins = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
        if not asins:
            raise ValueError(f"No ASINs found in {self.book_list_file}")
            
        print(f"\n{'='*80}")
        print(f"BATCH PROCESSING: {len(asins)} BOOKS")
        print(f"{'='*80}")
        print(f"Book list: {self.book_list_file}")
        print(f"Books to process: {', '.join(asins)}")
        
        results = []
        
        for i, asin in enumerate(asins, 1):
            print(f"\n{'#'*80}")
            print(f"BOOK {i}/{len(asins)}: {asin}")
            print(f"{'#'*80}")
            
            try:
                processor = KindleProcessor(asin, self.config)
                processor.run_pipeline()
                results.append({"asin": asin, "status": "success"})
                
            except Exception as e:
                print(f"❌ Failed to process {asin}: {e}")
                results.append({"asin": asin, "status": "failed", "error": str(e)})
                
                # Continue with next book unless configured to stop
                if not self.config.get('batch', {}).get('continue_on_error', True):
                    print("❌ Stopping batch processing due to error")
                    break
                    
        # Generate batch summary
        self.generate_batch_report(results)
        
    def generate_batch_report(self, results):
        """Generate summary report for batch processing"""
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] == 'failed']
        
        print(f"\n{'='*80}")
        print(f"BATCH PROCESSING SUMMARY")
        print(f"{'='*80}")
        print(f"Total books: {len(results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")
        
        if successful:
            print(f"\n✅ Successful books:")
            for result in successful:
                print(f"  - {result['asin']}")
                
        if failed:
            print(f"\n❌ Failed books:")
            for result in failed:
                print(f"  - {result['asin']}: {result['error']}")
                
        # Save detailed report
        report_file = Path(f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nDetailed report saved to: {report_file}")


def parse_simple_config(file_path):
    """Parse simple key-value configuration file"""
    config = {}
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Convert types
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value.isdigit():
                    value = int(value)
                
                # Build nested dict
                keys = key.split('.')
                current = config
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                current[keys[-1]] = value
    return config


def load_config(config_file=None):
    """Load configuration from simple key-value file with defaults"""
    default_config = {
        'pipeline': {
            'download': {
                'enabled': True,
                'pages_per_batch': 5,
                'auto_confirm': False
            },
            'decode': {
                'enabled': True,
                'mode': 'progressive',  # fast, full, progressive
                'early_exit': True,
                'save_images': True
            },
            'epub': {
                'enabled': True,
                'output_name': 'auto',  # auto, or custom name with {asin} and {title} placeholders
                'include_metadata': True
            }
        },
        'paths': {
            'downloads': 'downloads',
            'fonts': 'fonts',
            'output': 'output'
        },
        'batch': {
            'continue_on_error': True
        },
        'logging': {
            'level': 'INFO',
            'save_logs': True,
            'log_file': 'kindle_processor.log'
        }
    }
    
    # Load custom config if provided
    if config_file and Path(config_file).exists():
        print(f"Loading configuration from: {config_file}")
        custom_config = parse_simple_config(config_file)
            
        # Merge custom config with defaults
        def merge_dicts(default, custom):
            for key, value in custom.items():
                if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                    merge_dicts(default[key], value)
                else:
                    default[key] = value
                    
        merge_dicts(default_config, custom_config)
        
    return default_config


def check_prerequisites():
    """Check that required files and dependencies exist"""
    print("🔍 Checking prerequisites...")
    
    # Check required scripts
    required_scripts = [
        "download_full_book.py",
        "decode_glyphs_complete.py", 
        "create_epub.py"
    ]
    
    for script in required_scripts:
        if not Path(script).exists():
            raise FileNotFoundError(f"Required script not found: {script}")
    print("✅ Required scripts found")
    
    # Check headers.json
    if not Path("headers.json").exists():
        raise FileNotFoundError("headers.json not found - please create from headers.example.json")
    print("✅ headers.json found")
    
    # Check fonts directory
    fonts_dir = Path("fonts")
    if not fonts_dir.exists():
        raise FileNotFoundError("fonts/ directory not found")
        
    font_files = list(fonts_dir.glob("*.ttf"))
    if not font_files:
        raise FileNotFoundError("No TTF font files found in fonts/ directory")
    print(f"✅ Found {len(font_files)} font files")
    
    print("✅ All prerequisites satisfied")


def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Complete Kindle Book Processing Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single book
  python3 kindle_conversion_wrapper.py B0FLBTR2FS
  
  # Process with custom config
  python3 kindle_conversion_wrapper.py B0FLBTR2FS --config my_config.txt
  
  # Fast mode with auto-confirm
  python3 kindle_conversion_wrapper.py B0FLBTR2FS --fast --yes
  
  # Process multiple books
  python3 kindle_conversion_wrapper.py --batch book_list.txt
  
  # Custom output name
  python3 kindle_conversion_wrapper.py B0FLBTR2FS --output-name "My Book - {asin}.epub"
        """
    )
    
    # Main argument - either ASIN or batch mode
    parser.add_argument('asin', nargs='?', help='Book ASIN to process')
    
    # Configuration
    parser.add_argument('--config', help='Configuration file (simple key-value format)')
    
    # Processing modes (override config)
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--fast', action='store_true', help='Fast decoding mode')
    mode_group.add_argument('--full', action='store_true', help='Full character set mode')
    mode_group.add_argument('--progressive', action='store_true', help='Progressive mode (default)')
    
    # Workflow control
    parser.add_argument('--yes', action='store_true', help='Auto-confirm download prompts')
    parser.add_argument('--output-name', help='Custom EPUB output name (use {asin} for placeholder)')
    
    # Step control
    parser.add_argument('--skip-download', action='store_true', help='Skip download step')
    parser.add_argument('--skip-decode', action='store_true', help='Skip decode step')
    parser.add_argument('--skip-epub', action='store_true', help='Skip EPUB creation')
    
    # Batch processing
    parser.add_argument('--batch', help='Process multiple books from file')
    
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    
    # Validate arguments
    if not args.asin and not args.batch:
        parser.error("Must provide either ASIN or --batch option")
        
    if args.asin and args.batch:
        parser.error("Cannot use both ASIN and --batch options")
    
    try:
        # Check prerequisites
        check_prerequisites()
        
        # Load configuration
        config = load_config(args.config)
        
        # Apply CLI overrides to config
        if args.fast:
            config['pipeline']['decode']['mode'] = 'fast'
        elif args.full:
            config['pipeline']['decode']['mode'] = 'full'
        elif args.progressive:
            config['pipeline']['decode']['mode'] = 'progressive'
            
        if args.yes:
            config['pipeline']['download']['auto_confirm'] = True
            
        if args.output_name:
            config['pipeline']['epub']['output_name'] = args.output_name
            
        if args.skip_download:
            config['pipeline']['download']['enabled'] = False
        if args.skip_decode:
            config['pipeline']['decode']['enabled'] = False
        if args.skip_epub:
            config['pipeline']['epub']['enabled'] = False
            
        # Process single book or batch
        if args.batch:
            processor = BatchProcessor(args.batch, config)
            processor.process_batch()
        else:
            processor = KindleProcessor(args.asin, config)
            processor.run_pipeline()
            
    except KeyboardInterrupt:
        print("\n❌ Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
