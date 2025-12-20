#!/usr/bin/env python3
"""
Character Encoding Checker - UTF-8 to CP1252 Compatibility Verifier

This script scans all files in project to identify files that are UTF-8
but NOT CP1252 compatible, and reports problematic lines and characters.

Author: LousyBook01
Version: 1.0.0
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Dict
from datetime import datetime

class EncodingChecker:
    """Main class for checking character encoding compatibility"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        
        # File extensions to scan (text files)
        self.text_extensions = {
            '.py', '.js', '.html', '.htm', '.css', '.scss', '.less',
            '.json', '.xml', '.yml', '.yaml', '.toml', '.ini', '.cfg',
            '.txt', '.rst', '.csv', '.log', '.sql', '.sh',
            '.bat', '.cmd', '.ps1', '.gitignore', '.dockerfile'
        }
        
        # Files to skip (including markdown)
        self.skip_extensions = {
            '.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.msi',
            '.zip', '.tar', '.gz', '.rar', '.7z', '.jpg', '.jpeg',
            '.png', '.gif', '.bmp', '.ico', '.svg', '.pdf', '.doc',
            '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.mp3', '.mp4',
            '.avi', '.mov', '.wav', '.flac', '.ttf', '.otf', '.woff',
            '.woff2', '.eot', '.class', '.jar', '.war', '.ear',
            '.md'  # Skip markdown files
        }
        
        # Files to always skip (binary or generated)
        self.skip_files = {
            '.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.msi',
            '.zip', '.tar', '.gz', '.rar', '.7z', '.jpg', '.jpeg',
            '.png', '.gif', '.bmp', '.ico', '.svg', '.pdf', '.doc',
            '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.mp3', '.mp4',
            '.avi', '.mov', '.wav', '.flac', '.ttf', '.otf', '.woff',
            '.woff2', '.eot', '.class', '.jar', '.war', '.ear',
            '.md'  # Skip Markdown files as requested
        }

    def is_text_file(self, file_path: Path) -> bool:
        """Determine if a file is likely a text file"""
        if file_path.is_dir():
            return False
            
        # Check extension
        ext = file_path.suffix.lower()
        if ext in self.skip_files:
            return False
        if ext in self.text_extensions:
            return True
            
        # Try to read a small portion to detect binary files
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                # Check for null bytes (common in binary files)
                if b'\x00' in chunk:
                    return False
                # Check for high ratio of non-printable characters
                printable = sum(32 <= byte <= 126 or byte in (9, 10, 13) for byte in chunk)
                if len(chunk) > 0 and printable / len(chunk) < 0.7:
                    return False
        except Exception:
            return False
            
        return True

    def test_encoding_compatibility(self, file_path: Path) -> Tuple[bool, bool, List[Tuple[int, str, List[str]]]]:
        """
        Test if a file is compatible with UTF-8 and CP1252 encodings.
        Returns: (utf8_ok, cp1252_ok, problematic_lines)
        """
        problematic_lines = []
        utf8_ok = False
        cp1252_ok = False
        content_lines = []
        
        # First try UTF-8
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content_lines = f.readlines()
            utf8_ok = True
        except UnicodeDecodeError:
            return False, False, []
        
        # Test UTF-8 content for CP1252 compatibility
        try:
            content_text = ''.join(content_lines)
            content_text.encode('cp1252')
            cp1252_ok = True
        except UnicodeEncodeError:
            # Find problematic lines and characters
            for line_num, line in enumerate(content_lines, 1):
                try:
                    line.encode('cp1252')
                except UnicodeEncodeError:
                    # Find specific problematic characters
                    problematic_chars = []
                    for char in line:
                        try:
                            char.encode('cp1252')
                        except UnicodeEncodeError:
                            problematic_chars.append(char)
                    
                    if problematic_chars:
                        problematic_lines.append((line_num, line.rstrip(), problematic_chars))
        
        return utf8_ok, cp1252_ok, problematic_lines

    def scan_directory(self) -> Dict:
        """Scan all files in project directory"""
        results = {
            'total_files': 0,
            'text_files': 0,
            'utf8_only': 0,
            'cp1252_compatible': 0,
            'problematic_files': 0,
            'issues': []
        }
        
        print(f"Scanning directory: {self.project_root.absolute()}")
        
        # Walk through all files
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file():
                results['total_files'] += 1
                
                # Skip hidden files and directories
                if any(part.startswith('.') for part in file_path.parts):
                    continue
                
                if self.is_text_file(file_path):
                    results['text_files'] += 1
                    
                    utf8_ok, cp1252_ok, problematic_lines = self.test_encoding_compatibility(file_path)
                    
                    if utf8_ok and cp1252_ok:
                        results['cp1252_compatible'] += 1
                    elif utf8_ok and not cp1252_ok:
                        results['utf8_only'] += 1
                        results['problematic_files'] += 1
                        
                        issue_info = {
                            'file': str(file_path.relative_to(self.project_root)),
                            'problematic_lines': problematic_lines
                        }
                        results['issues'].append(issue_info)
        
        return results

    def print_report(self, results: Dict):
        """Print a detailed report of the scan results"""
        print("\n" + "="*80)
        print("CHARACTER ENCODING COMPATIBILITY REPORT")
        print("="*80)
        
        print(f"\nSUMMARY:")
        print(f"  Total files scanned: {results['total_files']}")
        print(f"  Text files found: {results['text_files']}")
        print(f"  CP1252 compatible: {results['cp1252_compatible']} [OK]")
        print(f"  UTF-8 only (NOT CP1252 compatible): {results['utf8_only']} [WARNING]")
        print(f"  Problematic files: {results['problematic_files']}")
        
        if results['issues']:
            print(f"\nFILES WITH ENCODING ISSUES (UTF-8 but NOT CP1252 compatible):")
            for issue in results['issues']:
                file_path = issue['file']
                print(f"\n  File: {file_path}")
                
                for line_num, line_content, problematic_chars in issue['problematic_lines']:
                    # Safe display of line content
                    try:
                        line_preview = line_content[:100] + ('...' if len(line_content) > 100 else '')
                        print(f"    Line {line_num}: {line_preview}")
                    except Exception:
                        print(f"    Line {line_num}: [Line contains problematic Unicode characters]")
                    
                    # Safe display of problematic characters
                    try:
                        print(f"      Problematic characters: {problematic_chars}")
                    except Exception:
                        safe_chars = []
                        for char in problematic_chars:
                            try:
                                char.encode('ascii')
                                safe_chars.append(char)
                            except:
                                safe_chars.append(f"U+{ord(char):04X}")
                        print(f"      Problematic characters (safe): {safe_chars}")
        else:
            print("\n[OK] All text files are CP1252 compatible!")
        
        print("\n" + "="*80)

def main():
    """Main function to run the character encoding checker"""
    parser = argparse.ArgumentParser(
        description="Check for UTF-8 to CP1252 encoding compatibility issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python char_fixer.py                    # Scan all files (default behavior)
  python char_fixer.py --path ./src       # Scan specific directory
  python char_fixer.py --verbose           # Enable verbose logging
        """
    )
    
    parser.add_argument(
        '--path', '-p',
        default='.',
        help='Project root directory (default: current directory)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging (currently disabled)'
    )
    
    args = parser.parse_args()
    
    # Initialize the encoding checker
    checker = EncodingChecker(args.path)
    
    try:
        # Scan the directory
        results = checker.scan_directory()
        
        # Print the report
        checker.print_report(results)
        
        # Exit with appropriate code
        sys.exit(0 if results['problematic_files'] == 0 else 1)
        
    except KeyboardInterrupt:
        print("\n\n[WARNING] Scan interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
