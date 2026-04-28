#!/usr/bin/env python3
"""
Test script specifically for the matrix functionality used in web interface
"""

import sys
import os

# Añadir el directorio raíz al path para importar los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.materia import Materia
from models.paralelo import Paralelo
from models.calificacion import Calificacion

def test_matrix_functionality():
    """Test the matrix functionality specifically used by web interface"""

    print("=== Prueba de funcionalidad de matriz para interfaz web ===")

    try:
        # Verificar si hay materias, paralelos, etc. en la base de datos
        materias = Materia.select()
        if not materias.exists():
            print("No hay materias registradas en la base de datos")
            return

        for materia in materias[:1]:  # Solo la primera materia para simplificar
            print(f"\nMateria: {materia.materia} ({materia.sigla})")

            paralelos = Paralelo.select().where(Paralelo.id_materia == materia)
            if not paralelos.exists():
                print(f"No hay paralelos para la materia {materia.sigla}")
                continue

            for paralelo in paralelos[:1]:  # Solo el primer paralelo
                print(f"\nParalelo: {paralelo.paralelo}")
                
                # Obtener matriz de calificaciones (this is the method used in web interface)
                matriz = Calificacion.matriz_calificaciones_paralelo(paralelo)
                
                if matriz:
                    print(f"Total estudiantes en matriz: {len(matriz)}")
                    
                    # Show first few students as example
                    for i, fila in enumerate(matriz[:3]):
                        print(f"  Estudiante {i+1}: {fila['estudiante']}")
                        print(f"    CI: {fila['ci']}")
                        print(f"    Promedio: {fila['promedio']}")
                        print(f"    Grupo: {fila['grupo']}")
                        
                        # Count how many labs have grades
                        lab_count = 0
                        for key, value in fila['calificaciones'].items():
                            if value is not None and value != 0:  # If there's a grade
                                lab_count += 1
                        
                        print(f"    Laboratorios con calificaciones: {lab_count}")
                        print()
                else:
                    print("  No hay matriz generada para este paralelo")

    except Exception as e:
        print(f"Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_matrix_functionality()