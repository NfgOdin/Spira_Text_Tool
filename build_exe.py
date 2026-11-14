"""
Automated Build Script for Spira Text Tool (FFX & FFX-2 Text & Localization Studio).
Executes test verification, cleans build artifacts, runs PyInstaller, and validates output.
"""

import os
import sys
import shutil
import subprocess
import hashlib
import unittest


def run_tests():
    print("=" * 60)
    print("Step 1: Running Automated Test Discovery & Verification...")
    print("=" * 60)
    loader = unittest.TestLoader()
    suite = loader.discover("tests")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        print("\n❌ BUILD ABORTED: Tests failed!")
        sys.exit(1)
    print("\n✅ All tests passed successfully!")


def clean_build_artifacts():
    print("\n" + "=" * 60)
    print("Step 2: Cleaning Previous Build Artifacts...")
    print("=" * 60)
    for folder in ("build", "dist"):
        if os.path.exists(folder):
            print(f"Removing '{folder}' directory...")
            try:
                shutil.rmtree(folder)
            except Exception as e:
                print(f"Warning: Could not fully clean '{folder}': {e}")


def run_pyinstaller():
    print("\n" + "=" * 60)
    print("Step 3: Building Standalone Executable with PyInstaller...")
    print("=" * 60)
    spec_file = "Spira_Text_Tool.spec"
    if not os.path.exists(spec_file):
        print(f"❌ Error: Spec file '{spec_file}' not found.")
        sys.exit(1)

    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", spec_file]
    print(f"Running: {' '.join(cmd)}")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"\n❌ PyInstaller compilation failed with code {res.returncode}.")
        sys.exit(res.returncode)


def verify_executable():
    print("\n" + "=" * 60)
    print("Step 4: Validating Output Executable...")
    print("=" * 60)
    exe_path = os.path.join("dist", "Spira_Text_Tool.exe")
    if not os.path.exists(exe_path):
        print(f"❌ Error: Expected output '{exe_path}' does not exist.")
        sys.exit(1)

    size_bytes = os.path.getsize(exe_path)
    size_mb = size_bytes / (1024 * 1024)

    hasher = hashlib.sha256()
    with open(exe_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    sha256 = hasher.hexdigest()

    print(f"✅ Build Successful!")
    print(f"• Executable: {exe_path}")
    print(f"• Size:       {size_mb:.2f} MB ({size_bytes:,} bytes)")
    print(f"• SHA-256:    {sha256}")
    print("=" * 60)


def main():
    print("=" * 60)
    print("Spira Text Tool v2.0.0 Build Pipeline")
    print("=" * 60)
    run_tests()
    clean_build_artifacts()
    run_pyinstaller()
    verify_executable()


if __name__ == "__main__":
    main()
