#!/usr/bin/env python3
"""
Test script to verify that all dependencies are properly installed
"""

import sys
import importlib

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        if package_name:
            importlib.import_module(package_name)
        else:
            importlib.import_module(module_name)
        print(f"✓ {module_name} - OK")
        return True
    except ImportError as e:
        print(f"✗ {module_name} - FAILED: {e}")
        return False

def main():
    print("Testing Posture Detection App Dependencies")
    print("=" * 40)
    
    # Test Python dependencies
    print("\nPython Dependencies:")
    python_modules = [
        ("Flask", "flask"),
        ("Flask-CORS", "flask_cors"),
        ("OpenCV", "cv2"),
        ("MediaPipe", "mediapipe"),
        ("NumPy", "numpy"),
        ("PIL", "PIL"),
        ("Werkzeug", "werkzeug"),
        ("python-dotenv", "dotenv"),
    ]
    
    all_passed = True
    for name, module in python_modules:
        if not test_import(name, module):
            all_passed = False
    
    # Test if we can import our custom modules
    print("\nCustom Modules:")
    try:
        sys.path.append('backend')
        import app
        print("✓ Backend app - OK")
    except ImportError as e:
        print(f"✗ Backend app - FAILED: {e}")
        all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("✓ All dependencies are properly installed!")
        print("\nYou can now run the application:")
        print("1. Start backend: cd backend && python app.py")
        print("2. Start frontend: npm start")
        print("\nOr use the startup scripts:")
        print("- Windows: start.bat")
        print("- Unix/Linux: ./start.sh")
    else:
        print("✗ Some dependencies failed to import.")
        print("\nPlease install missing dependencies:")
        print("pip install -r requirements.txt")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 