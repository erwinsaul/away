#!/usr/bin/env python3
"""
Debug script to check various scenarios for average calculation
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

def test_different_scenarios():
    """Test different scenarios for average calculation"""

    print("=== Prueba de diferentes escenarios de cálculo de promedios ===")

    try:
        # Verificar si hay materias, paralelos, etc. en la base de datos
        materias = Materia.select()
        if not materias.exists():
            print("No hay materias registradas en la base de datos")
            return

        for materia in materias:
            print(f"\nMateria: {materia.materia} ({materia.sigla})")

            # Contar laboratorios en esta materia
            laboratorios = Laboratorio.select().where(Laboratorio.id_materia == materia)
            total_labs = laboratorios.count()
            print(f"Total de laboratorios en la materia: {total_labs}")

            # Buscar paralelos en esta materia
            paralelos = Paralelo.select().where(Paralelo.id_materia == materia)
            if not paralelos.exists():
                print(f"No hay paralelos para la materia {materia.sigla}")
                continue

            for paralelo in paralelos:
                print(f"\nParalelo: {paralelo.paralelo}")
                print(f"Promedio general del paralelo: {paralelo.promedio_general()}")

                estudiantes = Estudiante.select().where(Estudiante.id_paralelo == paralelo)

                for estudiante in estudiantes[:3]:  # Solo los primeros 3 estudiantes
                    print(f"\n  Estudiante: {estudiante.nombre}")
                    
                    # Calcular promedio usando el método del modelo
                    promedio = estudiante.promedio_calificaciones()
                    print(f"  Promedio calculado del estudiante: {promedio}")

                    # Verificar cuántas calificaciones tiene
                    calificaciones = Calificacion.select().where(
                        Calificacion.id_estudiante == estudiante
                    ).join(Laboratorio).where(
                        Laboratorio.id_materia == materia
                    )

                    total_calificaciones = 0
                    count_calificaciones = 0

                    for cal in calificaciones:
                        if cal.calificacion is not None:
                            print(f"    Lab {cal.id_laboratorio.numero}: {cal.calificacion}")
                            total_calificaciones += cal.calificacion
                            count_calificaciones += 1
                        else:
                            print(f"    Lab {cal.id_laboratorio.numero}: Sin nota")

                    print(f"  Suma de calificaciones con nota: {total_calificaciones}")
                    print(f"  Cantidad de laboratorios con nota: {count_calificaciones}")
                    print(f"  Total de laboratorios en la materia: {total_labs}")
                    
                    if total_labs > 0:
                        manual_promedio = total_calificaciones / total_labs
                        print(f"  Promedio calculado manualmente (suma/total_labs): {manual_promedio}")
                        
                        # Verificar si hay discrepancia
                        if abs(promedio - manual_promedio) > 0.01:
                            print(f"  ¡DISCREPANCIA ENCONTRADA! Método: {promedio}, Manual: {manual_promedio}")

    except Exception as e:
        print(f"Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_different_scenarios()