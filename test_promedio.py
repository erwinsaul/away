#!/usr/bin/env python3
"""
Script de prueba para verificar el cálculo correcto de promedios
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

def test_promedio_calculations():
    """Prueba de cálculo de promedios"""
    
    print("=== Prueba de cálculo de promedios ===")
    
    try:
        # Verificar si hay materias, paralelos, etc. en la base de datos
        materias = Materia.select()
        if not materias.exists():
            print("No hay materias registradas en la base de datos")
            return
            
        materia = materias[0]  # Tomamos la primera materia
        print(f"Materia: {materia.materia} ({materia.sigla})")
        
        # Contar laboratorios en esta materia
        laboratorios = Laboratorio.select().where(Laboratorio.id_materia == materia)
        total_labs = laboratorios.count()
        print(f"Total de laboratorios en la materia: {total_labs}")
        
        # Buscar estudiantes en esta materia
        paralelos = Paralelo.select().where(Paralelo.id_materia == materia)
        if not paralelos.exists():
            print(f"No hay paralelos para la materia {materia.sigla}")
            return
            
        paralelo = paralelos[0]  # Tomamos el primer paralelo
        print(f"Paralelo: {paralelo.paralelo}")
        
        estudiantes = Estudiante.select().where(Estudiante.id_paralelo == paralelo)
        if not estudiantes.exists():
            print(f"No hay estudiantes en el paralelo {paralelo.paralelo}")
            return
            
        estudiante = estudiantes[0]  # Tomamos el primer estudiante
        print(f"Estudiante: {estudiante.nombre} (CI: {estudiante.ci})")
        
        # Calcular promedio usando el método del modelo
        promedio = estudiante.promedio_calificaciones()
        print(f"Promedio calculado del estudiante: {promedio}")
        
        # Verificar cuántas calificaciones tiene
        calificaciones = Calificacion.select().where(
            Calificacion.id_estudiante == estudiante
        ).join(Laboratorio).where(
            Laboratorio.id_materia == materia
        )
        
        total_calificaciones = 0
        count_calificaciones = 0
        
        print("Calificaciones del estudiante:")
        for cal in calificaciones:
            if cal.calificacion is not None:
                print(f"  Lab {cal.id_laboratorio.numero}: {cal.calificacion}")
                total_calificaciones += cal.calificacion
                count_calificaciones += 1
            else:
                print(f"  Lab {cal.id_laboratorio.numero}: Sin nota")
        
        print(f"Suma de calificaciones con nota: {total_calificaciones}")
        print(f"Cantidad de laboratorios con nota: {count_calificaciones}")
        print(f"Total de laboratorios en la materia: {total_labs}")
        print(f"Promedio calculado manualmente (suma/total_labs): {total_calificaciones/total_labs if total_labs > 0 else 0}")
        
    except Exception as e:
        print(f"Error en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_promedio_calculations()