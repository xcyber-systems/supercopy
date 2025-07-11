#!/usr/bin/env python3
"""
Setup script for SuperCopy macOS app.
To build: python3 setup.py py2app
"""
from setuptools import setup

APP = ['app.py']

# Include splash screen in the app's Resources folder
DATA_FILES = [('resources', ['splash.png'])]

OPTIONS = {
    'argv_emulation': False,
    'includes': ['llm_service', 'jaraco'],
    'excludes': ['tkinter', 'wheel'], # <-- ADD 'wheel' HERE
    'iconfile': 'icon.icns',
    'plist': {
        'CFBundleName': 'SuperCopy',
        'CFBundleDisplayName': 'SuperCopy',
        'CFBundleIdentifier': 'com.supercopy.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2024 Your Name',
        'LSUIElement': True,
        'NSAppleEventsUsageDescription': 'SuperCopy needs access to the clipboard for text analysis.',
    },
    'strip': False,
}


setup(
    name='SuperCopy',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'rumps>=0.4.0',
        'pyperclip>=1.8.2',
        'requests>=2.31.0',
        'python-dotenv>=1.0.0',
    ],
)