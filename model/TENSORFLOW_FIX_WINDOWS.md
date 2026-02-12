# Sentinel-AI - TensorFlow Windows DLL Fix Guide

## Problem
TensorFlow DLL load failed on Windows:
```
ImportError: DLL load failed while importing _pywrap_tensorflow_internal: 
A dynamic link library (DLL) initialization routine failed.
```

## Solution

### Option 1: Use tensorflow-cpu (Recommended)

```bash
# Uninstall old TensorFlow
pip uninstall -y tensorflow tensorflow-intel

# Install CPU-only TensorFlow (stable for Windows + Python 3.11)
pip install tensorflow-cpu==2.13.0

# If that fails, try:
pip install tensorflow-cpu==2.12.0

# Install other dependencies
pip install -r requirements.txt
```

### Option 2: Use the Setup Script

```bash
# Run the automated setup script
setup_windows.bat
```

### Option 3: Create Virtual Environment (Best Practice)

```bash
# Create virtual environment with Python 3.10
python -m venv sentinel-env
sentinel-env\Scripts\activate

# Install TensorFlow CPU version
pip install tensorflow-cpu==2.13.0

# Install dependencies
pip install -r requirements.txt

# Run the application
python app/app.py
```

## Why This Happens

1. **DLL Conflicts**: Windows has strict DLL loading rules that can conflict with TensorFlow's internal DLLs
2. **Python 3.11**: Some TensorFlow versions have compatibility issues with Python 3.11 on Windows
3. **Visual C++ Redistributable**: Missing VC++ runtime can cause DLL initialization failures

## Alternative: Install Visual C++ Redistributable

If tensorflow-cpu doesn't work, install the Visual C++ Redistributable:
1. Download "Visual C++ Redistributable Packages for Visual Studio 2015-2022" from Microsoft
2. Run the installer
3. Reboot your system

## Running the Application

After fixing TensorFlow:
```bash
cd model/app
python app.py
```

## Requirements Updated

The `requirements.txt` has been updated to use `tensorflow-cpu` instead of `tensorflow`:
```
tensorflow-cpu>=2.13.0
```

This version is specifically compiled for Windows and avoids the DLL issues.

