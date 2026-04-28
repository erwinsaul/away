#!/usr/bin/env python3
"""
Test script to verify multiple enrollment functionality
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import inicializar_bd
from managers.estudiante_manager import EstudianteManager
from managers.materia_manager import MateriaManager
from managers.paralelo_manager import ParaleloManager

def test_multi_enrollment():
    """Test that a student can be enrolled in multiple paralelos"""

    print("=== Testing Multiple Enrollment ===\n")

    # Initialize database
    inicializar_bd()

    # Get existing paralelos from all materias
    materias = MateriaManager.listar_materias()
    paralelos = []
    for materia in materias:
        paralelos.extend(ParaleloManager.listar_paralelos_por_materia(materia.id))

    if len(paralelos) < 2:
        print("ERROR: Need at least 2 paralelos to test")
        return

    print(f"Found {len(paralelos)} paralelos:")
    for p in paralelos:
        print(f"  - {p.id_materia.sigla} Paralelo {p.paralelo} (ID: {p.id})")

    print("\n--- Test 1: Register new student in first paralelo ---")
    ci = "99999999"
    nombre = "TEST STUDENT"

    # Clean up any existing test data
    existing = EstudianteManager.buscar_todos_por_ci(ci)
    if existing:
        print(f"Cleaning up {len(existing)} existing test records...")
        for est in existing:
            EstudianteManager.eliminar_estudiante(est.id, forzar=True)

    # Register in first paralelo
    est1 = EstudianteManager.registrar_estudiante(nombre, ci, paralelos[0].id, "Grupo 1")
    if est1:
        print(f"✓ Successfully enrolled in {est1.id_paralelo.id_materia.sigla} - Paralelo {est1.id_paralelo.paralelo}")
    else:
        print("✗ Failed to enroll in first paralelo")
        return

    print("\n--- Test 2: Register SAME student in second paralelo ---")
    est2 = EstudianteManager.registrar_estudiante(nombre, ci, paralelos[1].id, "Grupo 2")
    if est2:
        print(f"✓ Successfully enrolled in {est2.id_paralelo.id_materia.sigla} - Paralelo {est2.id_paralelo.paralelo}")
    else:
        print("✗ Failed to enroll in second paralelo")
        return

    print("\n--- Test 3: Verify multiple enrollments ---")
    all_enrollments = EstudianteManager.buscar_todos_por_ci(ci)
    print(f"Found {len(all_enrollments)} enrollment(s) for CI {ci}:")
    for est in all_enrollments:
        print(f"  - {est.nombre} in {est.id_paralelo.id_materia.sigla} - Paralelo {est.id_paralelo.paralelo}")

    if len(all_enrollments) >= 2:
        print("\n✓✓✓ SUCCESS: Multiple enrollment is working! ✓✓✓")
    else:
        print("\n✗✗✗ FAILED: Multiple enrollment not working ✗✗✗")

    # Cleanup
    print("\n--- Cleaning up test data ---")
    for est in all_enrollments:
        EstudianteManager.eliminar_estudiante(est.id, forzar=True)
    print("Test data cleaned up")

if __name__ == "__main__":
    test_multi_enrollment()
