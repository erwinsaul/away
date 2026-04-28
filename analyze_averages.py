#!/usr/bin/env python3
"""
Detailed analysis of different average calculation methods
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

def analyze_average_methods():
    """Analyze different possible methods for calculating student averages"""
    
    print("=== Análisis de métodos de cálculo de promedios ===\n")

    try:
        materias = Materia.select()
        if not materias.exists():
            print("No hay materias registradas en la base de datos")
            return

        for materia in materias:
            print(f"Materia: {materia.materia} ({materia.sigla})")
            total_labs = Laboratorio.select().where(Laboratorio.id_materia == materia).count()
            print(f"Total de laboratorios: {total_labs}")

            paralelos = Paralelo.select().where(Paralelo.id_materia == materia)
            for paralelo in paralelos:
                print(f"\n  Paralelo: {paralelo.paralelo}")
                
                estudiantes = Estudiante.select().where(Estudiante.id_paralelo == paralelo)
                
                for estudiante in estudiantes[:2]:  # Limit to first 2 for brevity
                    print(f"\n    Estudiante: {estudiante.nombre}")
                    
                    # Get all grades for this student
                    calificaciones = (estudiante.calificaciones
                                    .join(Laboratorio)
                                    .where(Laboratorio.id_materia == materia))
                    
                    total_grades = 0
                    labs_with_grades = 0
                    grades_list = []
                    
                    for cal in calificaciones:
                        if cal.calificacion is not None:
                            total_grades += cal.calificacion
                            labs_with_grades += 1
                            grades_list.append(cal.calificacion)
                            print(f"      Lab {cal.id_laboratorio.numero}: {cal.calificacion}")
                    
                    print(f"    Total grades sum: {total_grades}")
                    print(f"    Labs with grades: {labs_with_grades}")
                    print(f"    Grades list: {grades_list}")
                    
                    # Current method (as implemented): sum / total_labs_in_subject
                    current_method = total_grades / total_labs if total_labs > 0 else 0
                    print(f"    Current method (sum/total_labs): {current_method:.2f}")
                    
                    # Model method
                    model_method = estudiante.promedio_calificaciones()
                    print(f"    Model method result: {model_method:.2f}")
                    
                    # Method if we only consider labs student took: sum / labs_with_grades
                    if labs_with_grades > 0:
                        alternative_method = total_grades / labs_with_grades
                        print(f"    Alternative method (sum/labs_with_grades): {alternative_method:.2f}")
                    else:
                        print(f"    Alternative method (sum/labs_with_grades): 0.00")
                    
                    # Check for discrepancies
                    if abs(current_method - model_method) > 0.01:
                        print(f"    ! DISCREPANCY: Current vs Model methods differ!")
                    elif labs_with_grades > 0 and abs(alternative_method - model_method) < 0.01:
                        print(f"    ! NOTE: Model matches alternative method, not current method")
                    
                    print()

    except Exception as e:
        print(f"Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_average_methods()