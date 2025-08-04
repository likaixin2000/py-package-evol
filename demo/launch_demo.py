#!/usr/bin/env python3
"""
PyMevol Plus Demo Launcher

This script helps you get started with the PyMevol Plus demo notebooks.
It checks dependencies, sets up the environment, and launches Jupyter.
"""

import sys
import subprocess
import importlib
from pathlib import Path

def check_dependency(package_name, import_name=None):
    """Check if a package is installed."""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🚀 PyMevol Plus Demo Launcher")
    print("=" * 40)
    
    # Check if we're in the right directory
    demo_dir = Path(__file__).parent
    notebooks = list(demo_dir.glob("*.ipynb"))
    
    if not notebooks:
        print("❌ No demo notebooks found in current directory!")
        print(f"   Expected location: {demo_dir}")
        return 1
    
    print(f"📁 Demo directory: {demo_dir}")
    print(f"📚 Found {len(notebooks)} demo notebooks")
    
    # Core dependencies
    core_deps = [
        ("pymevol", "pymevol"),
        ("jupyter", "jupyter"),
        ("pandas", "pandas"),
        ("plotly", "plotly"),
    ]
    
    # Optional dependencies  
    optional_deps = [
        ("matplotlib", "matplotlib"),
        ("seaborn", "seaborn"),
        ("tqdm", "tqdm"),
    ]
    
    print("\\n🔍 Checking dependencies...")
    
    missing_core = []
    missing_optional = []
    
    for package, import_name in core_deps:
        if check_dependency(package, import_name):
            print(f"✅ {package}")
        else:
            print(f"❌ {package} (required)")
            missing_core.append(package)
    
    for package, import_name in optional_deps:
        if check_dependency(package, import_name):
            print(f"✅ {package}")
        else:
            print(f"⚠️  {package} (optional)")
            missing_optional.append(package)
    
    # Install missing dependencies
    if missing_core:
        print(f"\\n📦 Installing required dependencies: {', '.join(missing_core)}")
        for package in missing_core:
            print(f"   Installing {package}...")
            if not install_package(package):
                print(f"   ❌ Failed to install {package}")
                return 1
            print(f"   ✅ {package} installed")
    
    if missing_optional:
        print(f"\\n💡 Optional dependencies available: {', '.join(missing_optional)}")
        install_optional = input("   Install optional dependencies? (y/N): ").strip().lower()
        
        if install_optional in ['y', 'yes']:
            for package in missing_optional:
                print(f"   Installing {package}...")
                if install_package(package):
                    print(f"   ✅ {package} installed")
                else:
                    print(f"   ⚠️  Failed to install {package} (skipping)")
    
    # Test PyMevol Plus import
    print("\\n🧪 Testing PyMevol Plus...")
    try:
        import pymevol
        from pymevol import PackageAnalyzer
        analyzer = PackageAnalyzer()
        print("✅ PyMevol Plus is working correctly!")
        
        # Show version if available
        if hasattr(pymevol, '__version__'):
            print(f"   Version: {pymevol.__version__}")
        
    except Exception as e:
        print(f"❌ PyMevol Plus test failed: {e}")
        print("   Make sure PyMevol Plus is installed:")
        print("   pip install -e /path/to/pymevol-plus")
        return 1
    
    # List available notebooks
    print("\\n📚 Available demo notebooks:")
    for i, notebook in enumerate(sorted(notebooks), 1):
        print(f"   {i}. {notebook.name}")
    
    # Launch options
    print("\\n🚀 Launch options:")
    print("   1. Start Jupyter Notebook (classic interface)")
    print("   2. Start Jupyter Lab (modern interface)")  
    print("   3. Open specific notebook")
    print("   4. Just verify setup (don't launch)")
    
    choice = input("\\nSelect option (1-4): ").strip()
    
    if choice == "1":
        print("🚀 Launching Jupyter Notebook...")
        subprocess.run([sys.executable, "-m", "jupyter", "notebook"], cwd=demo_dir)
        
    elif choice == "2":
        print("🚀 Launching Jupyter Lab...")
        subprocess.run([sys.executable, "-m", "jupyter", "lab"], cwd=demo_dir)
        
    elif choice == "3":
        print("\\nSelect notebook to open:")
        for i, notebook in enumerate(sorted(notebooks), 1):
            print(f"   {i}. {notebook.stem}")
        
        try:
            nb_choice = int(input("Notebook number: ").strip())
            if 1 <= nb_choice <= len(notebooks):
                selected_notebook = sorted(notebooks)[nb_choice - 1]
                print(f"🚀 Opening {selected_notebook.name}...")
                subprocess.run([
                    sys.executable, "-m", "jupyter", "notebook", 
                    str(selected_notebook)
                ], cwd=demo_dir)
            else:
                print("❌ Invalid notebook number")
        except ValueError:
            print("❌ Invalid input")
            
    elif choice == "4":
        print("✅ Setup verification complete!")
        print("\\n💡 Next steps:")
        print("   - Run 'jupyter notebook' to start exploring")
        print("   - Begin with '01_basic_api_usage.ipynb'")
        print("   - Check the README.md for detailed guidance")
        
    else:
        print("❌ Invalid choice")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
