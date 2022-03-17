import sys
import os
from cx_Freeze import setup, Executable

# Build Optionen
build_exe_options = dict(packages = ["pathlib", "PySide6", "sys", "os", "tokenize", "tempfile", "json", "shutil", "requests", "threading", "psutil"], excludes = [], include_files = ["data/", "platforms/", "C42_Toollist_Converter_CheckforUpdate.json"])

# Ziel
target = Executable(
    script="C42 Toollist Converter.py",
    base="Win32GUI",
    icon="data/favicon.ico"
)

# Setup CX Freez
setup( 
    name = "C42 Toollist Converter",
    version = "0.25",
    description = "Umwandeln der Spannlisten",
    author= "Manuel Bücherl",
    options = {'build_exe' : build_exe_options},
    executables = [target]
    )