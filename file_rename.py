#!/usr/bin/env python3
"""
Enhanced File Renamer - Troubleshooting all limitations
Features: Interactive, configurable, safe, comprehensive character handling
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('file_rename.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class EnhancedFileRenamer:
    def __init__(self, directory=None, recursive=False, preview_only=False, 
                 replace_spaces=True, replace_special_chars=True, 
                 custom_replacements=None):
        self.directory = directory
        self.recursive = recursive
        self.preview_only = preview_only
        self.replace_spaces = replace_spaces
        self.replace_special_chars = replace_special_chars
        self.custom_replacements = custom_replacements or {}
        
        # Common special characters to replace (excluding dots for file extensions)
        self.special_chars = {
            ' ': '_',           # Spaces
            '-': '_',           # Hyphens
            '(': '_',           # Parentheses
            ')': '_',
            '[': '_',
            ']': '_',
            '{': '_',
            '}': '_',
            '<': '_',
            '>': '_',
            '&': 'and',
            '@': 'at',
            '#': 'hash',
            '%': 'percent',
            '$': 'dollar',
            '!': '_',
            '?': '_',
            ';': '_',
            ':': '_',
            ',': '_',
            '"': '_',
            "'": '_',
            '\\': '_',
            '/': '_',
            '|': '_',
            '*': '_',
            '^': '_',
            '~': '_',
            '`': '_'
        }
        
        # Update with custom replacements
        self.special_chars.update(self.custom_replacements)
    
    def get_directory_interactively(self):
        """Interactive directory path input with validation"""
        print("📁 Enhanced File Renamer")
        print("=" * 40)
        
        while True:
            if self.directory:
                folder_path = self.directory
            else:
                folder_path = input("📁 Enter the directory path to rename files: ").strip()
            
            if not folder_path:
                print("❌ Please enter a valid directory path")
                continue
            
            # Expand user home directory if needed
            folder_path = os.path.expanduser(folder_path)
            
            if not os.path.exists(folder_path):
                print(f"❌ Directory not found: {folder_path}")
                retry = input("Try again? (y/n): ").lower()
                if retry != 'y':
                    return None
                continue
            elif not os.path.isdir(folder_path):
                print(f"❌ Path is not a directory: {folder_path}")
                retry = input("Try again? (y/n): ").lower()
                if retry != 'y':
                    return None
                continue
            else:
                return folder_path
    
    def should_process_file(self, filepath):
        """Determine if file should be processed based on user preferences"""
        filename = os.path.basename(filepath)
        
        # Check if file has characters that need replacement
        if self.replace_spaces and ' ' in filename:
            return True
        
        if self.replace_special_chars:
            for char in self.special_chars:
                if char in filename:
                    return True
        
        return False
    
    def generate_new_name(self, filename):
        """Generate new filename with all replacements"""
        new_name = filename
        
        # Apply all character replacements
        for old_char, new_char in self.special_chars.items():
            new_name = new_name.replace(old_char, new_char)
        
        # Remove multiple consecutive underscores
        while '__' in new_name:
            new_name = new_name.replace('__', '_')
        
        # Remove leading/trailing underscores
        new_name = new_name.strip('_')
        
        return new_name
    
    def process_file(self, filepath, base_path):
        """Process a single file with error handling"""
        try:
            filename = os.path.basename(filepath)
            
            if not self.should_process_file(filepath):
                return False, None, None
            
            new_name = self.generate_new_name(filename)
            
            if new_name == filename:
                return False, None, None
            
            # Create new path
            relative_path = os.path.relpath(filepath, base_path)
            new_relative_path = os.path.dirname(relative_path)
            new_filepath = os.path.join(base_path, new_relative_path, new_name)
            
            # Handle file extension properly
            if '.' in filename and filename.rfind('.') > filename.rfind('_'):
                original_ext = filename[filename.rfind('.'):]
                if new_name.endswith(original_ext):
                    pass  # Extension already preserved
                else:
                    # Remove extension from new_name and add original
                    if '_' in new_name:
                        name_part = new_name[:new_name.rfind('_')]
                        new_name = name_part + original_ext
                        new_filepath = os.path.join(base_path, new_relative_path, new_name)
            
            # Check if target file already exists
            if os.path.exists(new_filepath) and new_filepath != filepath:
                counter = 1
                base_new_name = new_name
                while os.path.exists(new_filepath):
                    name_part, ext = os.path.splitext(base_new_name)
                    new_name = f"{name_part}_{counter}{ext}"
                    new_filepath = os.path.join(base_path, new_relative_path, new_name)
                    counter += 1
            
            return True, new_filepath, new_name
            
        except Exception as e:
            logging.error(f"Error processing {filepath}: {e}")
            return False, None, None
    
    def scan_files(self, directory):
        """Scan files to rename with error handling"""
        files_to_rename = []
        
        try:
            if self.recursive:
                # Recursive scanning
                for root, dirs, files in os.walk(directory):
                    for filename in files:
                        filepath = os.path.join(root, filename)
                        should_rename, new_filepath, new_name = self.process_file(filepath, directory)
                        if should_rename:
                            files_to_rename.append({
                                'old_path': filepath,
                                'new_path': new_filepath,
                                'old_name': filename,
                                'new_name': new_name
                            })
            else:
                # Top-level scanning only
                for filename in os.listdir(directory):
                    filepath = os.path.join(directory, filename)
                    if os.path.isfile(filepath):
                        should_rename, new_filepath, new_name = self.process_file(filepath, directory)
                        if should_rename:
                            files_to_rename.append({
                                'old_path': filepath,
                                'new_path': new_filepath,
                                'old_name': filename,
                                'new_name': new_name
                            })
        
        except PermissionError as e:
            logging.error(f"Permission denied accessing {directory}: {e}")
            print(f"❌ Permission denied: {directory}")
            return []
        except Exception as e:
            logging.error(f"Error scanning directory {directory}: {e}")
            print(f"❌ Error scanning directory: {e}")
            return []
        
        return files_to_rename
    
    def preview_changes(self, files_to_rename):
        """Display preview of changes"""
        if not files_to_rename:
            print("✅ No files need renaming!")
            return
        
        print(f"\n📋 Preview of changes ({len(files_to_rename)} files):")
        print("=" * 80)
        
        for i, file_info in enumerate(files_to_rename, 1):
            old_rel = os.path.relpath(file_info['old_path'], self.directory)
            new_rel = os.path.relpath(file_info['new_path'], self.directory)
            
            print(f"{i:3d}. {old_rel}")
            print(f"     → {new_rel}")
            
            # Show character changes
            changes = []
            old_name = file_info['old_name']
            new_name = file_info['new_name']
            
            for old_char, new_char in self.special_chars.items():
                if old_char in old_name:
                    changes.append(f"'{old_char}'→'{new_char}'")
            
            if changes:
                print(f"     Changes: {', '.join(changes)}")
            print()
    
    def execute_renames(self, files_to_rename):
        """Execute the file renaming with error handling"""
        if not files_to_rename:
            print("✅ No files to rename!")
            return 0
        
        renamed_count = 0
        failed_count = 0
        
        print(f"\n🔄 Executing renames ({len(files_to_rename)} files)...")
        print("=" * 50)
        
        for file_info in files_to_rename:
            try:
                old_path = file_info['old_path']
                new_path = file_info['new_path']
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(new_path), exist_ok=True)
                
                # Perform rename
                os.rename(old_path, new_path)
                
                # Log success
                old_rel = os.path.relpath(old_path, self.directory)
                new_rel = os.path.relpath(new_path, self.directory)
                print(f"✅ {old_rel} → {new_rel}")
                renamed_count += 1
                
            except PermissionError as e:
                print(f"❌ Permission denied: {file_info['old_path']} - {e}")
                failed_count += 1
            except OSError as e:
                print(f"❌ OS Error renaming {file_info['old_path']}: {e}")
                failed_count += 1
            except Exception as e:
                print(f"❌ Unexpected error renaming {file_info['old_path']}: {e}")
                failed_count += 1
        
        print(f"\n📊 Summary:")
        print(f"   ✅ Successfully renamed: {renamed_count}")
        print(f"   ❌ Failed to rename: {failed_count}")
        
        return renamed_count
    
    def run(self):
        """Main execution method"""
        # Get directory interactively
        directory = self.get_directory_interactively()
        if not directory:
            print("❌ No valid directory provided. Exiting.")
            return
        
        self.directory = directory
        
        print(f"\n🔍 Scanning directory: {directory}")
        print(f"   Recursive: {'Yes' if self.recursive else 'No'}")
        print(f"   Preview mode: {'Yes' if self.preview_only else 'No'}")
        
        # Scan for files to rename
        files_to_rename = self.scan_files(directory)
        
        if not files_to_rename:
            print("✅ No files found that need renaming!")
            return
        
        # Show preview
        self.preview_changes(files_to_rename)
        
        # Ask for confirmation if not in preview mode
        if not self.preview_only:
            response = input(f"\n🚀 Proceed with renaming {len(files_to_rename)} files? (y/n): ").lower()
            if response != 'y':
                print("❌ Operation cancelled by user.")
                return
        
        # Execute renames
        if self.preview_only:
            print("📋 Preview mode - no files were actually renamed.")
        else:
            renamed_count = self.execute_renames(files_to_rename)
            print(f"\n🎉 Completed! Renamed {renamed_count} files successfully.")
            print(f"📄 Detailed log saved to: file_rename.log")

def main():
    parser = argparse.ArgumentParser(
        description="Enhanced File Renamer - Fix all limitations of basic file renaming",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python file_rename_to_enhanced.py                                    # Interactive mode
  python file_rename_to_enhanced.py --dir /path/to/files              # Specify directory
  python file_rename_to_enhanced.py --recursive                       # Include subdirectories
  python file_rename_to_enhanced.py --preview                         # Preview only
  python file_rename_to_enhanced.py --no-spaces --no-special          # Disable specific replacements
        """
    )
    
    parser.add_argument('--dir', '--directory', 
                       help='Target directory path')
    parser.add_argument('--recursive', '-r', action='store_true',
                       help='Process subdirectories recursively')
    parser.add_argument('--preview', '-p', action='store_true',
                       help='Preview changes without executing')
    parser.add_argument('--no-spaces', action='store_true',
                       help='Skip space replacement')
    parser.add_argument('--no-special', action='store_true',
                       help='Skip special character replacement')
    parser.add_argument('--custom-replace', nargs='+',
                       help='Custom replacements in format old:new (e.g., @-at %-percent)')
    
    args = parser.parse_args()
    
    # Parse custom replacements
    custom_replacements = {}
    if args.custom_replace:
        for replacement in args.custom_replace:
            if ':' in replacement:
                old_char, new_char = replacement.split(':', 1)
                custom_replacements[old_char] = new_char
    
    # Create renamer instance
    renamer = EnhancedFileRenamer(
        directory=args.dir,
        recursive=args.recursive,
        preview_only=args.preview,
        replace_spaces=not args.no_spaces,
        replace_special_chars=not args.no_special,
        custom_replacements=custom_replacements
    )
    
    # Run the renamer
    renamer.run()

if __name__ == "__main__":
    main()