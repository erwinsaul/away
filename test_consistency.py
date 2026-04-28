#!/usr/bin/env python3
"""
Test script to compare average calculations between different methods
"""

import sys
import os

# Añadir el directorio raíz al path para importar los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.laboratorio import Laboratorio
from models.materia import Materia
from models.paralelo import Paralelo
from models.estudiante import Estudiante
from models.calificacion import Calificacion

def test_consistency():
    """Test consistency between different average calculation methods"""

    print("=== Prueba de consistencia entre métodos de cálculo de promedios ===")

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
                
                # Obtener matriz de calificaciones
                matriz = Calificacion.matriz_calificaciones_paralelo(paralelo)
                
                if matriz:
                    print(f"Total estudiantes en matriz: {len(matriz)}")
                    
                    for fila in matriz[:3]:  # Solo los primeros 3 estudiantes en la matriz
                        estudiante = Estudiante.get(Estudiante.ci == fila['ci'])
                        promedio_modelo = estudiante.promedio_calificaciones()
                        promedio_matriz = fila['promedio']
                        
                        print(f"\n  Estudiante: {fila['estudiante']}")
                        print(f"    Promedio (modelo): {promedio_modelo}")
                        print(f"    Promedio (matriz): {promedio_matriz}")
                        
                        if abs(promedio_modelo - promedio_matriz) > 0.01:
                            print(f"    ¡DISCREPANCIA DETECTADA! Diferencia: {abs(promedio_modelo - promedio_matriz)}")

                            # Mostrar detalles de diagnóstico
                            calificaciones = estudiante.calificaciones.where(Calificacion.calificacion.is_null(False))
                            total_calificaciones = sum(cal.calificacion for cal in calificaciones)
                            laboratorios_materia = Laboratorio.select().where(Laboratorio.id_materia == materia).count()
                            
                            print(f"    Detalles: suma={total_calificaciones}, total_labs={laboratorios_materia}, calculo={total_calificaciones/laboratorios_materia}")

    except Exception as e:
        print(f"Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_consistency()