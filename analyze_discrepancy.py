#!/usr/bin/env python3
"""
Detailed analysis of one specific student to understand the discrepancy
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

def analyze_discrepancy():
    """Analyze the specific discrepancy found"""
    
    print("=== Análisis del estudiante con discrepancia ===\n")

    try:
        # Find the specific student
        estudiante = Estudiante.get(Estudiante.nombre == "CALIZAYA CHOQUE ANTONIO GERARDO")
        print(f"Estudiante: {estudiante.nombre}")
        print(f"CI: {estudiante.ci}")
        print(f"Paralelo: {estudiante.id_paralelo.paralelo}")
        print(f"Materia: {estudiante.id_paralelo.id_materia.materia} ({estudiante.id_paralelo.id_materia.sigla})")
        
        # Count total labs for this student's materia
        total_labs = Laboratorio.select().where(Laboratorio.id_materia == estudiante.id_paralelo.id_materia).count()
        print(f"Total de laboratorios en la materia: {total_labs}")
        
        # Get all grades for this student
        calificaciones = (estudiante.calificaciones
                        .join(Laboratorio)
                        .order_by(Laboratorio.numero))
        
        total_grades = 0
        labs_with_grades = 0
        print("Calificaciones:")
        for cal in calificaciones:
            print(f"  Lab {cal.id_laboratorio.numero}: {cal.calificacion}")
            if cal.calificacion is not None:
                total_grades += cal.calificacion
                labs_with_grades += 1
        
        print(f"Suma de calificaciones: {total_grades}")
        print(f"Labs con calificaciones: {labs_with_grades}")
        
        if total_labs > 0:
            manual_calc = total_grades / total_labs
            print(f"Calculo manual (suma/total_labs): {manual_calc}")
        
        model_result = estudiante.promedio_calificaciones()
        print(f"Resultado del modelo: {model_result}")
        
        # Run exactly the same code as in the model
        materia = estudiante.id_paralelo.id_materia
        total_laboratorios = Laboratorio.select().where(Laboratorio.id_materia == materia).count()
        print(f"total_laboratorios en el modelo: {total_laboratorios}")
        
        # Obtener solo las calificaciones que tienen valor
        calificaciones_model = estudiante.calificaciones.where(Calificacion.calificacion.is_null(False))
        total_calificaciones = sum(cal.calificacion for cal in calificaciones_model)
        print(f"total_calificaciones en el modelo: {total_calificaciones}")
        
        result = round(total_calificaciones / total_laboratorios, 2) if total_laboratorios > 0 else 0.0
        print(f"Resultado del cálculo modelo: {result}")

    except Exception as e:
        print(f"Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_discrepancy()