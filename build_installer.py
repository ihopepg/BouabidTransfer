"""
Build Script for BouabidTransfer Installer
Creates Windows executable and installer package
"""

import os
import sys
import shutil
from pathlib import Path
import subprocess

def build_executable():
    """Build executable using PyInstaller"""
    print("Building BouabidTransfer executable...")
    
    # PyInstaller spec file
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
    ],
    hiddenimports=[
        'PyQt5',
        'pymobiledevice3',
        'libimobiledevice',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BouabidTransfer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)
"""
    
    # Write spec file
    spec_path = Path("BouabidTransfer.spec")
    with open(spec_path, 'w') as f:
        f.write(spec_content)
    
    # Run PyInstaller
    try:
        subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "BouabidTransfer.spec"
        ], check=True)
        print("✓ Executable built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to build executable: {e}")
        return False


def create_installer():
    """Create Windows installer using Inno Setup (if available)"""
    print("\nCreating installer...")
    
    # Inno Setup script
    iss_content = """
[Setup]
AppName=BouabidTransfer
AppVersion=1.0.0
AppPublisher=BouabidTransfer Team
AppPublisherURL=https://bouabidtransfer.com
AppSupportURL=https://bouabidtransfer.com/support
DefaultDirName={pf}\\BouabidTransfer
DefaultGroupName=BouabidTransfer
OutputDir=dist
OutputBaseFilename=BouabidTransfer-Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=assets\\icon.ico
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Files]
Source: "dist\\BouabidTransfer\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\\BouabidTransfer"; Filename: "{app}\\BouabidTransfer.exe"
Name: "{group}\\Uninstall BouabidTransfer"; Filename: "{uninstallexe}"
Name: "{autodesktop}\\BouabidTransfer"; Filename: "{app}\\BouabidTransfer.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\\BouabidTransfer.exe"; Description: "Launch BouabidTransfer"; Flags: nowait postinstall skipifsilent
"""
    
    iss_path = Path("installer.iss")
    with open(iss_path, 'w') as f:
        f.write(iss_content)
    
    # Check if Inno Setup is available
    inno_compiler = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    if os.path.exists(inno_compiler):
        try:
            subprocess.run([inno_compiler, str(iss_path)], check=True)
            print("✓ Installer created successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to create installer: {e}")
            return False
    else:
        print("⚠ Inno Setup not found. Installer script created at installer.iss")
        print("  Please compile it manually using Inno Setup Compiler")
        return False


def main():
    """Main build process"""
    print("=" * 60)
    print("BouabidTransfer - Build Process")
    print("=" * 60)
    
    # Clean previous builds
    if Path("build").exists():
        shutil.rmtree("build")
    if Path("dist").exists():
        shutil.rmtree("dist")
    
    # Build executable
    if not build_executable():
        print("\n✗ Build failed")
        return 1
    
    # Create installer
    create_installer()
    
    print("\n" + "=" * 60)
    print("Build process completed!")
    print("=" * 60)
    print("\nOutput files:")
    print("  - Executable: dist/BouabidTransfer/BouabidTransfer.exe")
    print("  - Installer: dist/BouabidTransfer-Setup.exe (if Inno Setup is available)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


