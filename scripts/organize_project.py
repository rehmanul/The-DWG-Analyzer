#!/usr/bin/env python3
"""
Project Directory Organizer
Clean and structure the entire project
"""

import os
import shutil
from pathlib import Path
import subprocess

def organize_project():
    """Organize project into clean structure"""
    
    # Define clean directory structure
    structure = {
        'src/': ['*.py files (core modules)'],
        'apps/': ['Desktop applications'],
        'installers/': ['NSIS scripts and installers'],
        'dist/': ['Built executables'],
        'build/': ['Build artifacts'],
        'docs/': ['Documentation'],
        'assets/': ['Icons, images, samples'],
        'config/': ['Configuration files'],
        'tests/': ['Test files'],
        'scripts/': ['Utility scripts']
    }
    
    print("🧹 ORGANIZING PROJECT DIRECTORY")
    print("=" * 50)
    
    # Create directories
    for dir_name in structure.keys():
        os.makedirs(dir_name, exist_ok=True)
        print(f"📁 Created: {dir_name}")
    
    # Move files to appropriate locations
    move_files()
    
    # Clean up
    cleanup_files()
    
    print("\n✅ PROJECT ORGANIZED!")

def move_files():
    """Move files to appropriate directories"""
    
    # Core source files to src/
    src_files = [
        'ai_analyzer.py', 'ai_integration.py', 'advanced_visualization.py',
        'construction_planner.py', 'database.py', 'dwg_parser.py',
        'enhanced_dwg_parser.py', 'enhanced_zone_detector.py', 'export_utils.py',
        'navigation_manager.py', 'optimization.py', 'pdf_parser.py',
        'placement_optimizer.py', 'robust_error_handler.py', 'visualization.py'
    ]
    
    for file in src_files:
        if os.path.exists(file):
            shutil.move(file, f'src/{file}')
            print(f"📄 Moved {file} → src/")
    
    # Desktop apps to apps/
    app_files = [
        'functional_desktop_app.py', 'desktop_app_web_features.py',
        'streamlit_app.py'
    ]
    
    for file in app_files:
        if os.path.exists(file):
            shutil.move(file, f'apps/{file}')
            print(f"🖥️ Moved {file} → apps/")
    
    # Installer files to installers/
    installer_files = [
        'installer.nsi', 'installer_fixed.nsi', 'installer_inno.iss',
        'build_installer.bat', 'create_installer.py'
    ]
    
    for file in installer_files:
        if os.path.exists(file):
            shutil.move(file, f'installers/{file}')
            print(f"📦 Moved {file} → installers/")
    
    # Executables to dist/
    if os.path.exists('dist/'):
        for file in os.listdir('dist/'):
            if file.endswith('.exe'):
                print(f"💾 Keeping dist/{file}")
    
    # Documentation to docs/
    doc_files = [
        'README.md', 'README_TUNNEL.md', 'LICENSE.txt'
    ]
    
    for file in doc_files:
        if os.path.exists(file):
            shutil.move(file, f'docs/{file}')
            print(f"📚 Moved {file} → docs/")
    
    # Assets
    asset_files = [
        'app_icon.ico', 'installer_banner.bmp'
    ]
    
    for file in asset_files:
        if os.path.exists(file):
            shutil.move(file, f'assets/{file}')
            print(f"🎨 Moved {file} → assets/")
    
    # Sample files
    if os.path.exists('attached_assets/'):
        shutil.move('attached_assets/', 'assets/samples/')
        print(f"📁 Moved attached_assets/ → assets/samples/")
    
    # Scripts
    script_files = [
        'organize_project.py', 'create_icon.py'
    ]
    
    for file in script_files:
        if os.path.exists(file):
            shutil.move(file, f'scripts/{file}')
            print(f"🔧 Moved {file} → scripts/")

def cleanup_files():
    """Clean up temporary and build files"""
    
    cleanup_patterns = [
        '*.pyc', '__pycache__/', '*.log', '*.tmp',
        'build/', '*.spec', 'warn-*.txt', 'xref-*.html'
    ]
    
    print("\n🧹 CLEANING UP:")
    
    # Remove PyInstaller build artifacts
    if os.path.exists('build/'):
        shutil.rmtree('build/')
        print("🗑️ Removed build artifacts")
    
    # Remove spec files
    for file in Path('.').glob('*.spec'):
        file.unlink()
        print(f"🗑️ Removed {file}")
    
    # Remove log files
    for file in Path('.').glob('*.log'):
        file.unlink()
        print(f"🗑️ Removed {file}")

def create_main_readme():
    """Create main project README"""
    
    readme_content = """# 🏗️ AI Architectural Space Analyzer PRO

Professional architectural drawing analysis with AI-powered insights.

## 📁 Project Structure

```
├── src/                    # Core source modules
├── apps/                   # Desktop & web applications  
├── installers/            # Installation packages
├── dist/                  # Built executables
├── docs/                  # Documentation
├── assets/                # Icons, images, samples
├── config/               # Configuration files
├── tests/                # Test files
└── scripts/              # Utility scripts
```

## 🚀 Quick Start

### Desktop Application
```bash
# Run from dist/
./AI_Architectural_Analyzer_WebFeatures.exe
```

### Web Application  
```bash
# Run from apps/
streamlit run streamlit_app.py
```

### Installation
```bash
# Run installer from installers/
./AI_Architectural_Analyzer_Setup.exe
```

## 🌟 Features

- ✅ AI-powered room detection
- ✅ Advanced furniture placement
- ✅ Interactive visualizations
- ✅ Professional export options
- ✅ BIM integration
- ✅ Multi-format support (DWG/DXF)

## 📊 Database

- **PostgreSQL**: `postgresql://de_de:PUPB8V0s2b3bvNZUblolz7d6UM9bcBzb@dpg-d1h53rffte5s739b1i40-a.oregon-postgres.render.com/dwg_analyzer_pro`
- **Gemini AI**: Configured and ready

## 🛠️ Development

See individual directories for specific documentation and setup instructions.

---
**Professional CAD Analysis Solution** 🎯
"""
    
    with open('README.md', 'w') as f:
        f.write(readme_content)
    
    print("📝 Created main README.md")

def git_operations():
    """Perform git operations"""
    
    print("\n🔄 GIT OPERATIONS:")
    
    try:
        # Add all files
        subprocess.run(['git', 'add', '.'], check=True)
        print("✅ Added all files to git")
        
        # Commit changes
        subprocess.run(['git', 'commit', '-m', '🧹 Organize project structure - Clean directory layout'], check=True)
        print("✅ Committed changes")
        
        # Push to remote
        subprocess.run(['git', 'push'], check=True)
        print("✅ Pushed to remote repository")
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Git operation failed: {e}")
        print("💡 Manual git commands:")
        print("   git add .")
        print("   git commit -m '🧹 Organize project structure'")
        print("   git push")

def main():
    """Main execution"""
    
    # Change to project directory
    os.chdir(r'C:\Users\HP\Desktop\DWG Analyzee')
    
    # Organize project
    organize_project()
    
    # Create main README
    create_main_readme()
    
    # Git operations
    git_operations()
    
    print("\n🎉 PROJECT ORGANIZATION COMPLETE!")
    print("\n📁 CLEAN STRUCTURE:")
    print("   ├── src/           # Core modules")
    print("   ├── apps/          # Applications") 
    print("   ├── installers/    # Installation")
    print("   ├── dist/          # Executables")
    print("   ├── docs/          # Documentation")
    print("   ├── assets/        # Resources")
    print("   └── scripts/       # Utilities")

if __name__ == "__main__":
    main()