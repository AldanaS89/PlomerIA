"""
Configuración de pytest para la suite de PlomerIA.

Inserta la carpeta Backend/ en el path para que los tests puedan importar
`services`, `models`, etc. sin importar desde dónde se ejecute pytest.
"""
import os
import sys

# Backend/ (carpeta padre de tests/)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
