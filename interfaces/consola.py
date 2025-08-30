"""
Interfaz de consola para el Sistema de gestión de laboratorios.
"""

import os
import sys
from models.database import inicializar_bd, cerrar_bd
from managers.materia_manager import MateriaManager
from managers.paralelo_manager import ParaleloManager
from managers.estudiante_manager import EstudianteManager
from managers.laboratorio_manager import LaboratorioManager
from managers.calificacion_manager import CalificacionManager

class InterfazConsola:
    """
    Interfaz principal de consola del sistema.
    """
    def __init__(self):
        self.running = True

    def ejecutar(self):
        """
        Ejecuta el menu principal del sistema.
        """
        try:
            print("="*60)
            print("     SISTEMA DE GESTIÓN DE LABORATORIOS")
            print("="*60)

            # Inicializar base de datos
            inicializar_bd()

            while self.running:
                self.mostrar_menu_principal()
                opcion = self.obtener_opcion()
                self.procesar_opcion_principal(opcion)

        except KeyboardInterrupt:
            print("")
            print("Sistema cerrado por el usuario")
        except Exception as e:
            print("")
            print("Error:", e)
        finally:
            cerrar_bd()
    
    def mostrar_menu_principal(self):
        """Muestra el menú principal del sistema. """
        print("")
        print("="*40)
        print("                MENÚ PRINCIPAL")
        print("="*40)
        print("1. Gestión de Materias")
        print("2. Gestión de Paralelos")
        print("3. Gestión de Estudiantes")
        print("4. Gestión de Laboratorios")
        print("5. Gestión de Calificaciones")
        print("6. Reportes y Exportación")
        print("7. Estadísticas")
        print("8. Salir")
        print("-"*40)
    
    def obtener_opcion(self):
        """ Obtiene y valida la opción del Usuario"""
        while True:
            try:
                opcion = input("Seleccione una opción:").strip()
                return opcion
            except EOFError:
                return "0"
    
    def procesar_opcion_principal(self, opcion):
        """ Procesa la opción seleccionada del menú principal."""
        if opcion == "1":
            self.menu_materias()
        elif opcion == "2":
            self.menu_paralelos()
        elif opcion == "3":
            self.menu_estudiantes()
        elif opcion == "4":
            self.menu_laboratorios()
        elif opcion == "5":
            self.menu_calificaciones()
        elif opcion == "6":
            self.menu_reportes()
        elif opcion == "7":
            self.menu_estadisticas_generales()
        elif opcion == "0":
            self.salir()
        else:
            print("[ERROR] Opción no válida. Intente nuevamente.")
    
    # ==========================================================================
    # MENÚ DE GESTIÓN DE MATERIAS
    # ==========================================================================
    def menu_materias(self):
        """Muestra el menú de gestión de materias."""
        print("")
        print("="*40)
        print("                GESTIÓN DE MATERIAS")
        print("="*40)
        print("1. Crear materia")
        print("2. Listar materias")
        print("3. Buscar materia")
        print("4. Actualizar materia")
        print("5. Eliminar materia")
        print("6. Estadísticas de materias")
        print("0. Volver al menú principal")
        print("-"*40)

        opcion = self.obtener_opcion()

        if opcion == "1":
            self.crear_materia()
        elif opcion == "2":
            self.listar_materias()
        elif opcion == "3":
            self.buscar_materia()
        elif opcion == "4":
            self.actualizar_materia()
        elif opcion == "5":
            self.eliminar_materia()
        elif opcion == "6":
            self.estadisticas_materias()
        elif opcion == "0":
            break
        else:
            print("[ERROR] Opción no válida.")
    
    def crear_materia(self):
        """ Crea una nueva materia."""
        print("")
        print("--- Crear Nueva Materia ---")
        materia = input("Nombre de la materia:").strip()
        if not materia:
            print("[ERROR] El nombre de la materia es obligatorio.")
            return

        sigla = input("Sigla (ej: SIS-1110): ").strip()
        if not sigla:
            print("[ERROR] La sigla de la materia es obligatorio.")
            return
        
        resultado = MateriaManager.crear_materia(materia, sigla)
        if resultado:
            print("[OK] Materia {sigla} creada exitosamente.")
        else:
            print("[ERROR] No se pudo crear la materia.")
    
    def listar_materias(self):
        """ Lista todas las materias """
        print()
        print("--- Lista de Materias ---")
        materias = MateriaManager.listar_materias()
        if not materias:
            print("No hay materias registradas.")
            return
        
        print()
        print("ID | Nombre                          | Sigla")
        print("-"*80)

        for materia in materias:
            print(f"{materia.id:2d} | {materia.materia:20s} | {materia.sigla:10s}")
    
    def buscar_materia(self):
        """ Busca materías por términos """
        print()
        print("--- Buscar Materia ---")

        termino = input("Ingrese un término de búsqueda:").strip()
        if not termino:
            print("[ERROR] El término de búsqueda es obligatorio.")
            return
        
        materias = MateriaManager.buscar_materia(termino)

        if not materias:
            print("No hay materias que coincidan con el término de búsqueda.")
            return

        print()
        print("--- Resultad para {termino} ---")
        print("ID | Nombre                          | Sigla")
        print("-"*80)
        for materia in materias:
            print(f"{materia.id:2d} | {materia.materia:20s} | {materia.sigla:10s}")

    def actualizar_materia(self):
        """ Actualiza una materia existente """
        print()
        print("--- Actualizar Materia ---")

        self.listar_materias()

        try:
            materia_id = int(input("\nID de la materia a actualizar:"))
            materia = MateriaManager.obtener_materia(materia_id)
            if not materia:
                print("[ERROR] La materia no existe con ese ID.")
                return
            
            print()
            print(f"Actualizando la materia: {materia.sigla} -- {materia.materia}")
            print("Deje en blanco para mantener el valor actual.")

            nombre = input("Nombre ({materia.materia}) : ").strip()
            sigla = input("Sigla ({materia.sigla}): ").strip()

            campos = {}
            if nombre:
                campos["materia"] = nombre
            if sigla:
                campos["sigla"] = sigla
            
            if not campos:
                print("[ERROR] No se realizaron cambios.")
                return
            
            if MateriaManager.actualizar_materia(materia_id, **campos):
                print("[OK] Materia actualizada exitosamente.")
            else:
                print("[ERROR] No se pudo actualizar la materia.")
        except ValueError:
            print("[ERROR] El ID ingresado no es válido.")
    
    def eliminar_materia(self):
        """ Elimina una materia existente """
        print()
        print("--- Eliminar Materia ---")
        self.listar_materias()

        try:
            materia_id = int(input("\nID de la materia a eliminar:"))
            materia = MateriaManager.obtener_materia(materia_id)
            if not materia:
                print("[ERROR] La materia no existe con ese ID.")
                return
            
            print()
            print(f"Eliminando la materia: {materia.sigla} -- {materia.materia}")
            
            stats = materia.estadisticas_completas()
            print(f"Paralelos: {stats['paralelos']}")
            print(f"Estudiantes: {stats['estudiantes']}")
            print(f"Laboratorios: {stats['laboratorios']}")

            confirmacion = input("\n¿Está seguro de eliminar la materia? (s/N): ").strip().lower()
            if confirmacion != "s":
                print("Operacion Cancelada")
                return
            
            forzar = False
            if stats['paralelos'] > 0 or stats['laboratorios'] > 0:
                forzar_input = input("Eliminar con todas sus dependencias? (s/N)").strip().lower()
                forzar = forzar_input == 's'
                resultado = MateriaManager.eliminar_materia(materia_id, forzar)

                if resultado['success']:
                    print(f"[OK] {resultado['mensaje']}")
                else:
                    print(f"[ERROR] {resultado['mensaje']}")
        
        except ValueError:
            print("[ERROR] ID no válido")

    def estadisticas_materias(self):
        """ Muestra las estadísticas de materias """
        print()
        print("--- Estadísticas de Materias ---")
        materias = MateriaManager.listar_materias()
        if not materias:
            print("No hay materias registradas.")
            return
        
        print()
        print("Detalle de materia:")
        print("Sigla     | Paralelos          | Estudiantes        | Laboratorios")
        print("-"*50)

        for materia in materias:
            stats = materia.estadisticas_completas()
            print(f"{materia.sigla:10s} | {stats['paralelos']:5d} | {stats['estudiantes']:5d} | {stats['laboratorios']:5d}")


    # ===========================================================
    # GESTIÓN DE PARALELOS
    # ===========================================================
    def menu_paralelos(self):
        """ Menu para la gestión de paralelos """
        print()
        print("-"*40)
        print("                GESTIÓN DE PARALELOS")
        print("-"*40)
        print("1. Crear paralelo")
        print("2. Listar paralelos por Materia")
        print("3. Actualizar paralelo")
        print("4. Eliminar paralelo")
        print("5. Estadísticas de paralelos")
        print("0. Volver al menú principal")

        opcion = self.obtener_opcion()

        if opcion == "1":
            self.crear_paralelo()
        elif opcion == "2":
            self.listar_paralelos_por_materia()
        elif opcion == "3":
            self.actualizar_paralelo()
        elif opcion == "4":
            self.eliminar_paralelo()
        elif opcion == "5":
            self.estadisticas_paralelos()
        elif opcion == "0":
            break
        else:
            print("[ERROR] Opción no válida.")

    def crear_paralelo(self):
        """ Crea un nuevo paralelo """
        print()
        print("--- Crea un Nuevo Paralelo ---")

        materias = MateriaManager.listar_materias()

        if not materias:
            print("[ERROR] No hay materias registradas.")
            return
        
        print()
        print("Materias Disponibles")
        for materia in materias:
            print(f"{materia.id:2d} | {materia.sigla:10s} | {materia.materia:20s}")

        try:
            materia_id = int(input("\nID de la materia:"))

            paralelo_nombre = input("Nombre del Paralelo (A, B, C, etc.):").strip()
            if not paralelo_nombre:
                print("[ERROR] El nombre del paralelo es obligatorio.")
                return

            nombre_docente = input("Nombre del Docente:").strip().upper()
            if not nombre_docente:
                print("[ERROR] El nombre del docente es obligatorio.")
                return
            
            resultado = ParaleloManager.crear_paralelo(materia_id, paralelo_nombre, nombre_docente)
            if resultado:
                print("[OK] Paralelo {paralelo_nombre}-{nombre_docente} creado exitosamente.")
            else:
                print("[ERROR] No se pudo crear el paralelo.")
        except ValueError:
            print("[ERROR] El ID de materia no es válido.")