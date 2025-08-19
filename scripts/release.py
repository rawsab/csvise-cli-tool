#!/usr/bin/env python3
"""
Release script for CSVise
"""
import re
import sys
from pathlib import Path


def update_version(version, files):
    """Update version in specified files"""
    for file_path in files:
        if not Path(file_path).exists():
            print(f"Warning: {file_path} does not exist")
            continue
            
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Update version in different file types
        if file_path.endswith('.py'):
            # Python files
            content = re.sub(r'version\s*=\s*["\']([^"\']+)["\']', f'version = "{version}"', content)
            content = re.sub(r"@click\.version_option\('([^']+)'", f"@click.version_option('{version}'", content)
        elif file_path.endswith('.toml'):
            # TOML files
            content = re.sub(r'version\s*=\s*["\']([^"\']+)["\']', f'version = "{version}"', content)
        elif file_path.endswith('.md'):
            # Markdown files
            content = re.sub(r'Version:\s*([^\n]+)', f'Version: {version}', content)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"Updated version in {file_path}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/release.py <version>")
        print("Example: python scripts/release.py 1.2.1")
        sys.exit(1)
    
    version = sys.argv[1]
    
    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        print("Error: Version must be in format X.Y.Z (e.g., 1.2.1)")
        sys.exit(1)
    
    # Files to update
    files_to_update = [
        'pyproject.toml',
        'setup.py',
        'csvtools/cli.py',
        'README.md'
    ]
    
    print(f"Updating version to {version}...")
    update_version(version, files_to_update)
    print("Version update complete!")
    print("\nNext steps:")
    print("1. Test the package: pip install -e .")
    print("2. Build the package: python -m build")
    print("3. Test the build: twine check dist/*")
    print("4. Commit changes: git add . && git commit -m 'Bump version to {version}'")
    print("5. Create a tag: git tag v{version}")
    print("6. Push changes: git push && git push --tags")
    print("7. Create a GitHub release")
    print("8. Publish to PyPI: twine upload dist/*")


if __name__ == "__main__":
    main()
