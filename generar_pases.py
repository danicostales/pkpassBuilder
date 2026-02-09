#!/usr/bin/env python3
"""Script simple para generar pases."""
import sys
from pathlib import Path

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pkpass_builder.generate import main

if __name__ == "__main__":
    main()
