#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Punto de entrada principal para el agregador de feeds ICS.

Este script permite ejecutar el agregador desde la raíz del proyecto.
"""

import sys
from pathlib import Path

# Agregar src al path para importar el módulo
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from cronquiles.main import main

if __name__ == "__main__":
    main()
