#!/usr/bin/env python3
"""
Test script to verify that students can now be registered in multiple subjects
"""

import sys
import os

# Añadir el directorio raíz al path para importar los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import inicializar_bd
from models.materia import Materia
from models.paralelo import Paralelo
from managers.estudiante_manager import EstudianteManager
from managers.materia_manager import MateriaManager
from managers.paralelo_manager import ParaleloManager

def test_multiple_enrollments():
    """Test that a student can be enrolled in multiple subjects"""

    print("=== Testing Multiple Subject Enrollment ===")

    try:
        # Initialize database
        from models.database import inicializar_bd
        inicializar_bd()

        # Create some test data
        # Create first subject
        materia1 = MateriaManager.crear_materia("INTRODUCCION A LA PROGRAMACION", "SIS-1100")
        if materia1:
            print(f"Created materia: {materia1.materia}")
        else:
            print("Failed to create first materia")
            return

        # Create second subject
        materia2 = MateriaManager.crear_materia("PROGRAMACION AVANZADA", "SIS-2200")
        if materia2:
            print(f"Created materia: {materia2.materia}")
        else:
            print("Failed to create second materia")
            return

        # Create paralelos for each subject
        paralelo1 = ParaleloManager.crear_paralelo(materia1.id, "A", "Profesor Uno")
        print(f"Created paralelo: {paralelo1.paralelo} for {paralelo1.id_materia.sigla}")

        paralelo2 = ParaleloManager.crear_paralelo(materia2.id, "A", "Profesor Dos")
        print(f"Created paralelo: {paralelo2.paralelo} for {paralelo2.id_materia.sigla}")
        
        # Try to register the same student in both subjects
        ci_estudiante = "12345678"
        nombre_estudiante = "Juan Pérez"
        
        # Register in first paralelo
        estudiante1 = EstudianteManager.registrar_estudiante(
            nombre_estudiante, 
            ci_estudiante, 
            paralelo1.id, 
            "Grupo 1"
        )
        
        if estudiante1:
            print(f"✓ Successfully registered {nombre_estudiante} in {paralelo1.id_materia.sigla}")
        else:
            print(f"✗ Failed to register {nombre_estudiante} in {paralelo1.id_materia.sigla}")
            return
        
        # Try to register the same student in second paralelo (this should work now)
        estudiante2 = EstudianteManager.registrar_estudiante(
            nombre_estudiante, 
            ci_estudiante, 
            paralelo2.id, 
            "Grupo 2"
        )
        
        if estudiante2:
            print(f"✓ Successfully registered {nombre_estudiante} in {paralelo2.id_materia.sigla}")
            print("✓ Student successfully enrolled in multiple subjects!")
        else:
            print(f"✗ Failed to register {nombre_estudiante} in {paralelo2.id_materia.sigla}")
            print("✗ This indicates the multiple enrollment is still not working")
        
        # Verify both records exist
        estudiantes_con_mismo_ci = EstudianteManager.buscar_todos_por_ci(ci_estudiante)
        print(f"Number of records found for CI {ci_estudiante}: {len(estudiantes_con_mismo_ci)}")
        
        for est in estudiantes_con_mismo_ci:
            print(f"  - {est.nombre} in paralelo {est.id_paralelo.id_materia.sigla}-{est.id_paralelo.paralelo}")
        
    except Exception as e:
        print(f"Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_multiple_enrollments()