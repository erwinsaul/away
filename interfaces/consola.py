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

    def listar_paralelos_por_materia(self):
        """ Lista de paralelos de una materia específica """
        print("\n--- Listar Paralelos por Materia ---")

        # Mostrar materias disponibles
        materias = MateriaManager.listar_materias()
        if not materias:
            print("No hay materias registradas.")
            return
        
        print()
        print("Materias Disponibles")

        for materia in materias:
            print(f"{materia.id:2d} | {materia.sigla:10s} | {materia.materia:20s}")
        
        try:
            materia_id = int(input("\nID de la materia: "))
            paralelos = ParaleloManager.listar_paralelos_por_materia(materia_id)

            if not paralelos:
                print("No hay paralelos registrados en esta materia.")
                return

            print()
            print(f"--- Paralelos ---")
            print("ID | Nombre  | Docente | Estudiantes | Grupos")
            print("-"*80)

            for paralelo in paralelos:
                print(f"{paralelo.id:2d} | {paralelo.nombre:20s} | {paralelo.docente_teoria:10s} | {paralelo.contar_estudiantes():5d} | {paralelo.contar_grupos():5d}")
        
        except ValueError:
            print("[ERROR] ID de materia no válido")
        
    def actualizar_paralelo(self):
        """ Actualiza un paralelo existente """
        print()
        print("--- Actualizar Paralelo ---")

        self.listar_paralelos_por_materia()

        try:
            paralelo_id = int(input("\nID del paralelo a actualizar:"))
            paralelo  = ParaleloManager.obtener_paralelo(paralelo_id)
            if not paralelo:
                print("[ERROR] No existe paralelo con ese ID.")
                return
            
            print()
            print(f"Actualizando el paralelo: {paralelo.nombre}")
            print("Deje en blanco para mantener el valor actual.")

            nuevo_nombre = input("Nuevo nombre ({paralelo.nombre}): ").strip()
            nuevo_docente = input("Nuevo docente ({paralelo.docente_teoria}): ").strip().upper()

            campos = {} 
            if nuevo_nombre:
                campos["nombre"] = nuevo_nombre
            
            if nuevo_docente:
                campos["docente_teoria"] = nuevo_docente
            
            if not campos:
                print("No se realizaron cambios.")
                return
            
            if ParaleloManager.actualizar_paralelo(paralelo_id, **campos):
                print("[OK] Paralelo actualizado exitosamente.")
            else:
                print("[ERROR] No se pudo actualizar el paralelo.")
        
        except ValueError:
            print("[ERROR] ID de paralelo no válido")
    
    def eliminar_paralelo(self):
        """ Elimina un paralelo existente """
        
        print()
        print("--- Eliminar Paralelo ---")

        # Listar paralelos por materia
        self.listar_paralelos_por_materia()

        try:
            paralelo_id = int(input("\nID del paralelo a eliminar:"))
            paralelo = ParaleloManager.obtener_paralelo(paralelo_id)
            if not paralelo:
                print("[ERROR] No existe el paralelo con este ID")
                return
            
            print(f"\nParalelo a eliminar: {paralelo.nombre} - {paralelo.docente_teoria}")
            print(f"Estudiantes inscritos: {paralelo.contar_estudiantes()}")

            confirmacion = input("\n¿Está seguro de eliminar el paralelo? (s/N): ").strip().lower()

            if confirmacion != "s":
                print("Operacion Cancelada")
                return
            
            # Preguntas si forzar eliminación
            forzar = False
            if paralelo.contar_estudiantes() > 0:
                forzar_input = input("Eliminar con todos los estudiantes inscritos? (s/N)").strip().lower()
                forzar = forzar_input == 's'
            
            resultado = ParaleloManager.eliminar_paralelo(paralelo_id, forzar)

            if resultado['success']:
                print(f"[OK] {resultado['mensaje']}")
            else:
                print(f"[ERROR] {resultado['mensaje']}")
        
        except ValueError:
            print("[ERROR] ID de paralelo no válido")
        
    def estadisticas_paralelo(self):
        """ Muestra estadísticas de un paralelo específico """
        print("")
        print("--- Estadísticas de Paralelo ---")

        # Listar paralelos por materia
        self.listar_paralelos_por_materia()

        try:
            paralelo_id = int(input("\nID del paralelo: "))
            stats = EstudianteManager.obtener_estadisticas_paralelo(paralelo_id)

            if 'error' in stats:
                print(f"[ERROR] {stats['error']}")
                return
            
            print("")
            print(f"\n--- Estadísticas: {stats['paralelo_info']} ---")
            print(f"Total Estudiantes: {stats['total_estudiantes']}")
            print(f"Total Grupos: {stats['total_grupos']}")
            print(f"Estudiantes sin Grupo: {stats['estudiantes_sin_grupo']}")
            print(f"Promedio General: {stats['promedio_general']}")
            if stats['grupos_lista']:
                print(f"Grupos: {stats['grupos_lista']}")

        except ValueError:
            print("[ERROR] ID de paralelo no válido")
    
    # ==========================================================================
    # GESTIÓN DE ESTUDIANTES
    # ==========================================================================
    def menu_estudiantes(self):
        """ Menú completo de gestión de estudiantes """
        while True:
            print("")
            print("-"*40)
            print("     GESTIÓN DE ESTUDIANTES")
            print("-"*40)
            print("1. Registrar Estudiante")
            print("2. Listar Estudiantes por Paralelo")
            print("3. Buscar estudiante por CI")
            print("4. Actualizar Estudiante")
            print("5. Eliminar Estudiante")            
            print("6. Estadísticas de paralelo")
            print("0. Volver al menú principal")

            opcion = self.obtener_opcion()

            if opcion == "1":
                self.registrar_estudiante()
            elif opcion == "2":
                self.listar_estudiantes_por_paralelo()
            elif opcion == "3":
                self.buscar_estudiante()
            elif opcion == "4":
                self.actualizar_estudiante()
            elif opcion == "5":
                self.eliminar_estudiante()
            elif opcion == "6":                
                self.estadisticas_estudiantes_paralelo()
            elif opcion == "0":
                break
            else:
                print("[ERROR] Opción no válida.")
    
    def registrar_estudiante(self):
        """ Registra un nuevo estudiante """

        print("")
        print("--- Registrar Estudiante ---")

        # Mostrar materias y paralelos disponibles
        materias = MateriaManager.listar_materias()

        if not materias:
            print("[ERROR] No hay materias registradas. Debe registrar una materia primero.")
            return
        
        # Mostrar estructura de materias y paralelos
        print("\nEstrucutara de Materias:")
        for materia in materias:
            paralelos = ParaleloManager.listar_paralelos_por_materia(materia.id)
            print(f"{materia.sigla} | {materia.materia}")
            for paralelo in paralelos:
                print(f"ID: {paralelo.id} - Paralelo: {paralelo.paralelo} - Docente: {paralelo.docente_teoria} - Estudiantes: {paralelo.contar_estudiantes()}")
        
        try:
            paralelo_id = int(input("\nID del paralelo:"))
            nombre = input("Nombre del estudiante:").strip().upper()

            if not nombre:
                print("[ERROR] El nombre del estudiante es obligatorio.")
                return
            
            ci = input("Cedula de identidad: "),strip()
            if not ci:
                print("[ERROR] El CI es obligatorio.")
                return
            
            grupo = input("Grupo (Opcional): ").strip().upper()

            estudiante = EstudianteManager.registrar_estudiante(nombre, ci, paralelo_id, grupo)
        
            if estudiante: 
                print("\n[OK] Estudiante {nombre} registrado exitosamente.")
            else:
                print("\n[ERROR] No se registro al estudiante.")
        
        except ValueError:
            print("[ERROR] ID de paralelo no válido")
    
    def listar_estudiantes_por_paralelo(self):
        """ Lista estudiantes de un paralelo específico """
        print("\n--- Listar Estudiantes por Paralelo ---")

        materias = MateriaManager.listar_materias()

        if not materias:
            print("[ERROR] No hay materias registradas.")
            return
        
        print("\nParalelo Disponibles:")
        for materia in materias:
            paralelos = ParaleloManager.listar_paralelos_por_materia(materia.id)
            for paralelo in paralelos:
                print(f"{paralelo.id} - {materia.sigla} Paralelo {paralelo.paralelo} - Docente: {paralelo.docente_teoria} ({paralelo.contar_estudiantes()})")
            
        try:
            paralelo_id = int(input("\nID del paralelo:"))

            print("\nOrdenar por:")
            print("1. Nombre (default)")
            print("2. Grupo")
            print("3. CI")

            orden_opcion = input("Opcion (1-3): ").strip() or "1"
            orden_map = {"1": "nombre", "2": "grupo", "3": "ci"}
            orden = orden_map[orden_opcion]

            estudiantes = EstudianteManager.listar_por_paralelo(paralelo_id, orden)

            if not estudiantes:
                print("No hay estudiantes registrados en este paralelo.")
                return
            
            print(f"\n---Estudiantes del Paralelo {paralelo_id}---")
            print("ID | CI                | Nombre                 | Grupo              | Promedio")
            print("-"*80)

            for estudiante in estudiantes:
                grupo_str = estudiante.grupo if estudiante.grupo else "Sin Grupo"
                promedio = estudiante.promedio_calificaciones()
                print(f"{estudiante.id:2d} | {estudiante.ci:10s} | {estudiante.nombre:20s} | {grupo_str:10s} | {promedio:5.2f}")

        except ValueError:
            print("[ERROR] ID de paralelo no válido")
    
    def buscar_estudiante_por_ci(self):
        """ Busca un estudiatne por CI """
        print("\n--- Buscar Estudiante por CI ---")

        ci = input("Ingrese CI del estudiante:").strip()

        if not ci:
            print("[ERROR] El CI es obligatorio.")
            return
        
        estudiante = EstudianteManager.buscar_estudiante_por_ci(ci)

        if not estudiante:
            print(f"No se encontró estudiante con CI {ci}.")
            return
        
        print(f"\n--- Información del Estudiante ---")
        print(f"ID: {estudiante.id}")
        print(f"CI: {estudiante.ci}")
        print(f"Nombre: {estudiante.nombre}")
        print(f"Paralelo: {estudiante.id_paralelo}")
        print(f"Grupo: {estudiante.grupo if estudiante.grupo else 'Sin Grupo'}")
        print(f"Promedio: {estudiante.promedio_calificaciones():.2f}")
        print(f"Calificaciones registradas: {estudiante.contar_calificaciones()}")

        # Mostrar calificaciones por laboratorio
        calificaciones = estudiante.calificaciones_por_laboratorio()
        if calificaciones:
            print("\n--- Calificaciones por Laboratorio ---")
            for lab, datos in calificaciones.items():
                print(f"{lab}: {datos['calificacion']:.1f} -  {datos['titulo']}")
    
    def actualizar_estudiante(self):
        """ Actualiza información de un estudiante """
        print("\n--- Actualizar Estudiante ---")

        ci = input("Ingrese CI del estudiante:").strip()

        if not ci:
            print("[ERROR] El CI es obligatorio.")
            return
        
        estudiante = EstudianteManager.obtener_por_ci(ci)

        if not estudiante:
            print(f"No se encontró estudiante con CI {ci}.")
            return 

        print(f"\nActualizando información del estudiante: {estudiante.nombre}")
        print("Deje en blanco para mantener el valor actual.")

        # Obtener nuevos valores
        nombre = input("Nuevo nombre ({estudiante.nombre}): ").strip().upper()
        ci = input(f"CI ({estudiante.ci}): ").strip()
        grupo = input(f"Grupo ({estudiante.grupo or 'Sin Grupo'}): ").strip().upper()

        campos = {}
        if nombre:
            campos["nombre"] = nuevo_nombre
            
        if ci:
            campos["ci"] = ci

        if grupo:
            campos["grupo"] = grupo
        
        if not campos:
            print("No se realizaron cambios.")
            return
        
        if EstudianteManager.actualizar_estudiante(estudiante.id, **campos):
            print("[OK] Estudiante actualizado exitosamente.")
        else:
            print("[ERROR] No se pudo actualizar el estudiante.")
    
    def eliminar_estudiante(self):
        """ Elimina un estudiante del sistema """
        print("\n--- Eliminar Estudiante ---")

        ci = input("CI del estudiante:").strip()

        if not ci:
            print("[ERROR] El CI es obligatorio.")
            return
        
        estudiante = EstudianteManager.obtener_por_ci(ci)

        if not estudiante:
            print(f"No se encontró estudiante con CI {ci}.")
            return

        print(f"\nEstudiante a eliminar: {estudiante.nombre} ({estudiante.ci})")
        print(f"Paralelo: {estudiante.id_paralelo}")
        print(f"Calificaciones registradas: {estudiante.contar_calificaciones()}")

        confirmacion = input("\n Está seguro que desea eliminar el estudiante? (s/N): ").strip().lower()

        if confirmacion != "s":
            print("Operacion Cancelada")
            return
        
        # Preguntas si forzar eliminación
        forzar = False
        if estudiante.contar_calificaciones() > 0:
            forzar_input = input("Eliminar con todas sus calificaciones? (s/N)").strip().lower()
            forzar = forzar_input == 's'

        resultado = EstudianteManager.eliminar_estudiante(estudiante.id, forzar)

        if resultado['success']:
            print(f"[OK] {resultado['mensaje']}")
        else:
            print(f"[ERROR] {resultado['mensaje']}")
        
    def estadisticas_estudiantes_paralelo(self):
        """ Muestra estadísticas de un paralelo específico """
        print("\n--- Estadísticas de Estudiantes del Paralelo ---")

        # Mostrar paralelos disponibles
        materias = MateriaManager.listar_materias()

        if not materias:
            print("No hay materias registradas")
            return
        
        print("\nParalelo Disponibles:")
        for materia in materias:
            paralelos = ParaleloManager.listar_paralelos_por_materia(materia.id)
            for paralelo in paralelos:
                print(f"ID: {paralelo.id} - {materia.sigla} Paralelo {paralelo.paralelo}")
        
        try:
            paralelo_id = int(input("\nID del paralelo: "))

            stats = EstudianteManager.obtener_estadisticas_paralelo(paralelo_id)
            
            if 'error' in stats:
                print(f"[ERROR] {stats['error']}")
                return
            
            print("\n--- Estadísticas: {stat['paralelo_info']} ---")
            print(f"Total Estudiantes: {stats['total_estudiantes']}")
            print(f"Total Grupos: {stats['total_grupos']}")
            print(f"Estudiantes sin Grupo: {stats['estudiantes_sin_grupo']}")
            print(f"Promedio General: {stats['promedio_general']:.2f}")

            if stats['grupos_lista']:
                print(f"Grupos: {', '.join(stats['grupos_lista'])}")
            else:
                print("No hay grupos registrados.")
        
        except ValueError:
            print("[ERROR] ID de paralelo no válido")

    
    # ==========================================================================
    # GESTIÓN DE LABORATORIOS
    # ==========================================================================

    def menu_laboratorios(self):
        """ Menú completo de gestión de laboratorios """

        while True:
            print("")
            print("-"*40)
            print("     GESTIÓN DE LABORATORIOS")
            print("-"*40)
            print("1. Crear Laboratorio")
            print("2. Listar Laboratorios por materia")
            print("3. Actualizar Laboratorio")
            print("4. Eliminar Laboratorio")
            print("5. Estadísticas de Laboratorios")
            print("0. Volver al menú principal")

            opcion = self.obtener_opcion()

            if opcion == "1":
                self.crear_laboratorio()
            elif opcion == "2":
                self.listar_laboratorios_por_materia()
            elif opcion == "3":
                self.actualizar_laboratorio()
            elif opcion == "4":
                self.eliminar_laboratorio()
            elif opcion == "5":
                self.estadisticas_laboratorios()
            elif opcion == "0":
                break
            else:
                print("[ERROR] Opción no válida.")
        
    def crear_laboratorio(self):
        """ Crea un nuevo laboratorio """
        print("")
        print("--- Crear Nuevo Laboratorio ---")

        materias = MateriaManager.listar_materias()

        if not materias:
            print("[ERROR] No hay materias registradas.")
            return
        
        print("\nMaterias Disponibles:")
        for materia in materias:
            print(f"{materia.id:2d} | {materia.sigla:10s} | {materia.materia:20s}")

        try:
            materia_id = int(input("\ID de la materia:"))
            titulo = input("Titulo del laboratorio:").strip().upper()

            if not titulo:
                print("[ERROR] El titulo del laboratorio es obligatorio.")
                return
            
            descripcion = input("Descripción (Opcional): ").strip() or None

            try:
                puntaje_maximo = float(input("puntaje maximo (default: 100.0): ").strip() or "100")
            except ValueError:
                puntaje_maximo = 100.0
            
            resultado = LaboratorioManager.crear_laboratorio(materia_id, titulo, descripcion, puntaje_maximo)

            if resultado:
                print(f"[OK] Laboratorio creado xitosamente: {resultado}")
            else:
                print("[ERROR] No se pudo crear el laboratorio")
        
        except ValueError:
            print("[ERROR] ID de la materia no válido")
    
    def listar_laboratorios_por_materia(self):
        """ Lista Laboratorios de una materia específica """

        print("\n--- Listar Laboatorios por Materia ---")

        #Mostrar materias disponibles
        materias = MateriaManager.listar_materia()

        if not materias:
            print("[ERROR] No hay materias registradas")
            return
        
        print("\nMaterias Disponibles")
        for materia in materias:
            print(f"{materia.id:2d} | {materia.sigla:10s} | {materia.materia:20s}")

        try:
            materia_id = int(input("\nID de la materia:"))
            laboratorios = LaboratorioManager.listar_laboratorios_por_materia(materia_id)

            if not laboratorios:
                print("No hay laboratorios registrados en esta materia.")
                return
            
            print("\n--- Laboratorios ---")
            print("ID | Num | Titulo                         | Puntaje     | Calificaciones")
            print("-"*80)
            for laboratorio in laboratorios:
                print(f"{laboratorio.id:2d} | {laboratorio.numero:2d} | {laboratorio.titulo:20s} | {laboratorio.puntaje_maximo:5.2f} | {laboratorio.contar_calificaciones():13d}")
        
        except ValueError:
            print("[ERROR] ID de materia no válido")
    
    def actualizar_laboratorio(self):
        """ Actualiza un laboratorio existente """
        print("\n--- Actualizar Laboratorio ---")

        # Primero listar por materia
        self.listar_laboratorios_por_materia()

        try:
            laboratorio_id = int(input("\nID del laboratorio a actualizar:"))

            laboratorio = LaboratorioManager.obtener_laboratorio(laboratorio_id)

            if not laboratorio:
                print("[ERROR] No existe laboratorio con ese ID.")
                return
            
            print(f"\nActualizando laboratorio: {laboratorio}")
            print("Deje en blanco para mantener el valor actual.")

            # Obtener nuevos valores

            titulo = input(f"Título ({laboratorio.titulo}): ").strip().upper()
            descripcion = input(f"Descripción ({laboratorio.descripcion or 'Sin descripción'}): ").strip()

            try:
                puntaje = input(f"Puntaje máximo ({laboratorio.puntaje_maximo}): ").strip()
                nuevo_puntaje = float(nuevo_puntaje) if nuevo_puntaje else None
            except ValueError:
                nuevo_puntaje = None
            
            # Preparar campos a actualizar
            campos = {}
            if titulo:
                campos["titulo"] = titulo
            
            if descripcion:
                campos["descripcion"] = descripcion

            if nuevo_puntaje:
                campos["puntaje_maximo"] = nuevo_puntaje
            
            if not campos:
                print("No se realizaron cambios.")
                return

            if LaboratorioManager.actualizar_laboratorio(laboratorio_id, **campos):
                print("[OK] Laboratorio actualizado exitosamente.")
            else:
                print("[ERROR] No se pudo actualizar el laboratorio.")
        
        except ValueError:
            print("[ERROR] ID de laboratorio no válido")
    

    def eliminar_laboratorio(self):
        """ Elimina un laboratorio del sistema """
        print("\n--- Eliminar Laboratorio ---")

        # Primero listar por materia
        self.listar_laboratorios_por_materia()

        try:
            laboratorio_id = int(input("\nID del laboratorio a eliminar:"))

            laboratorio = LaboratorioManager.obtener_laboratorio(laboratorio_id)

            if not laboratorio:
                print("[ERROR] No existe laboratorio con ese ID.")
                return
            
            print(f"\nLaboratorio a eliminar: {laboratorio}")
            print(f"Calificaciones registradas: {laboratorio.contar_calificaciones()}")

            confiracion = input("\n¿Está seguro de eliminar el laboratorio? (s/N): ").strip().lower()

            if confirminacion != "s":
                print("Operacion Cancelada")
                return
            
            # Preguntar si forzar eliminación
            forzar = False
            if laboratorio.contar_calificaciones() > 0:
                forzar_input = input("Eliminar con todas las calificaciones? (s/N)").strip().lower()
                forzar = forzar_input == 's'
            
            resultado = LaboratorioManager.eliminar_laboratorio(laboratorio_id, forzar)

            if resultado['success']:
                print(f"[OK] {resultado['mensaje']}")
            else:
                print(f"[ERROR] {resultado['mensaje']}")
        
        except ValueError:
            print("[ERROR] ID de laboratorio no válido")
    
    def estadisticas_laboratorios(self):
        """ Muestra estadísticas de un laboratorio específico """
        print("\n--- Estadísticas de Laboratorio ---")

        # Primero listar por materia
        self.listar_laboratorios_por_materia()

        try:
            laboratorio_id = int(input("\nID del laboratorio: "))
            laboratorio = LaboratorioManager.obtener_laboratorio(laboratorio_id)

            if not laboratorio:
                print("[ERROR] No existe laboratorio con ese ID.")
                return
            
            stats = laboratorio.estadisticas_detalladas()
            print(f"\n--- Estadísticas: {laboratorio} ---")
            print(f"Total Calificaciones: {stats['total_calificaciones']}")
            print(f"Promedio general: {stats['promedio']:.2f}")
            print(f"Nota máxima: {stats['nota_maxima']:.2f}")
            print(f"Nota mínima: {stats['nota_minima']:.2f}")
            print(f"Aprobados: {stats['aprobados']}")
            print(f"Reprobados: {stats['reprobados']}")

            if stats['total_calificaciones'] > 0:
                porcentaje_aprobacion = (stats['aprobados'] / stats['total_calificaciones'])*100
                print(f"Porcentaje de Aprobación: {porcentaje_aprobacion:.2f}%")

        except ValueError:
            print("[ERROR] ID de laboratorio no válido")
    
    # ==========================================================================
    # GESTIÓN DE CALIFICACIONES
    # ==========================================================================

    def menu_calificaciones(self):
        """ Menú completo de gestión de calificaciones """
        while True:
            print("")
            print("-"*40)
            print("     GESTIÓN DE CALIFICACIONES")
            print("-"*40)
            print("1. Registrar Calificación")
            print("2. Ver Calificaciones por estudiante")
            print("3. Ver Calificaciones por Laboratorio")
            print("4. Actualizar Calificación")
            print("5. Eliminar Calificación")
            print("6. Calificar por Lote")
            print("7. Estadísticas por Paralelo")
            print("0. Volver al menú principal")

            opcion = self.obtener_opcion()
            if opcion == "1":
                self.registrar_calificacion()
            elif opcion == "2":
                self.ver_calificaciones_por_estudiante()
            elif opcion == "3":
                self.ver_calificaciones_por_laboratorio()
            elif opcion == "4":
                self.actualizar_calificacion()
            elif opcion == "5":
                self.eliminar_calificacion()
            elif opcion == "6":
                self.calificar_por_lote()
            elif opcion == "7":
                self.estadisticas_calificaciones_paralelo()
            elif opcion == "0":
                break
            else:
                print("[ERROR] Opción no válida.")

    def registrar_calificacion(self):
        """ Registra un nueva calificación """
        print("\n--- Registrar Calificación ---")
        # Mostrar estructura disponible
        materias = MateriaManager.listar_materias()
        if not materias:
            print("[ERROR] no hay materias registradas")
            return
        
        print("\nEstructura disponible:")
        for materia in materias:
            laboratorios = LaboratorioManager.listar_laboratorios_por_materia(materia.id)
            if laboratorios:
                print(f"{materia.sigla} | {materia.materia}")
                for laboratorio in laboratorios:
                    print(f"ID: {laboratorio.id} - {laboratorio.titulo} (PuntajeMáximo: {laboratorio.puntaje_maximo})")
    
        try:
            laboratorio_id = int(input("\nID del laboratorio: "))
            laboratorio = LaboratorioManager.obtener_laboratorio(laboratorio_id)

            if not laboratorio:
                print("[ERROR] No existe laboratorio con ese ID.")
                return
            
            print(f"Laboratorio seleccionado: {laboratorio}")
            print(f"Puntaje máximo: {laboratorio.puntaje_maximo}")

            ci = input("\CI del estudiante:").strip()
            estudiante = EstudianteManager.obtener_por_ci(ci)

            if not estudiante:
                print("[ERROR] No existe estudiante con ese CI.")
                return
            
            print(f"Estudiante: {estudiante.nombre}")

            try:
                calificacion = float(iput("Calificación: "))
            except ValueError:
                print("[ERROR] La calificación debe ser un número.")
                return
            
            observaciones = input("Observaciones (Opcional): ").strip() or None

            resultado = CalificacionManager.registrar_calificacion(laboratorio_id, estudiante_id, calificacion, observaciones) 

            if resultado:
                print(f"[OK] Calificación registrada exitosamente.")
            else:
                print("[ERROR] No se pudo registrar la calificación.")
        
        except ValueError:
            print("[ERROR] ID de laboratorio no válido")
    
    def ver_calificaciones_por_estudiante(self):
        """ Muestra todas las calificaciones de un estudiante """
        print("\n--- Ver Calificaciones por Estudiante ---")

        ci = input("CI del estudiante:").strip()
        estudiante = EstudianteManager.buscar_por_ci(ci)
        if not estudiante:
            print("[ERROR] No existe estudiante con es CI")
            return
        
        calificaciones = CalificacionManager.obtener_calificaciones_estudiante(estudiante.id)

        if not calificaciones:
            print("No hay calificaciones registradas para {estudiante.nombre}")
            return
        
        print(f"\n--- Calificaciones de {estudiante.nombre} ---")
        print("ID | Lab | Título                   | Nota   | Estado | Fecha")
        print("-"*80)
        for calificacion in calificaciones:
            lab = calificacion.id_laboratorio
            estado = calificacion.estado_aprobacion()
            fecha = calificacion.fecha_registro_strftime("%d %m %Y")
            nota_str = f"{calificacion.calificacion:.2f}" if calificacion.calificacion else "None"

            print(f"{calificacion.id:2d} | {lab.numero:2d} | {lab.titulo:20s} | {nota_str:5.2f} | {estado:10s} | {fecha}")

        # Mostrar promedio
        promedio = estudiante.promedio_calificaciones()
        print(f"\nPromedio: {promedio:.2f}")

    def ver_calificaciones_por_laboratorio(self):
        """ Muestra todas las calificaciones de un laboratorio """
        print("\n--- Ver Calificaciones por Laboratorio ---")

        # Mostrar laboratorio disponibles
        materias = MateriaManager.listar_materias()
        if not materias:
            print("[ERROR] No hay materias registradas.")
            return

        print("\nLaboratorio Disponibles:")
        for materia in materias:
            laboratorios = LaboratorioManager.listar_laboratorios_por_materia(materia.id)
            if laboratorios:
                print(f"\n{materia.sigla}")
                for laboratorio in laboratorios:
                    print(f"  ID: {laboratorio.id} - {laboratorio.titulo}")

        try:
            laboratorio_id = int(input("\nID del laboratorio: "))
            laboratorio = LaboratorioManager.obtener_laboratorio(laboratorio_id)

            if not laboratorio:
                print("[ERROR] No existe laboratorio con ese ID.")
                return
            
            calificaciones = CalificacionManager.obtener_calificaciones_laboratorio(laboratorio_id)

            if not calificaciones:
                print("No hay calificaciones registradas para {laboratorio}.")
                return
            
            print(f"\n--- Calificaciones de {laboratorio} ---")
            print("ID | CI       | Estudiante                   | Nota   | Estado | Fecha")
            print("-"*80)

            for calificacion in calificaciones:
                estudiante = calificacion.id_estudiante
                estado = calificacion.estado_aprobacion()
                fecha = calificacion.fecha_registro_strftime("%d %m %Y")
                nota_str = f"{calificacion.calificacion:.2f}" if calificacion.calificacion else "Sin nota"
                print(f"{calificacion.id:2d} | {estudiante.ci:10s} | {estudiante.nombre:20s} | {nota_str:5.2f} | {estado:10s} | {fecha}")
            
            # Mostrar estadísticas
            stats = laboratorio.estadisticas_detalladas()
            print(f"\nPromedio del Laboratorio: {stats['promedio']:.2f}")
            print(f"Aprobados: {stats['aprobados']}")
            print(f"Reprobados: {stats['reprobados']}")
            print(f"Sin nota: {stats['sin_nota']}")

        except ValueError:
            print("[ERROR] ID de laboratorio no válido")
    
    def actualizar_calificacion(self):
        """ Actualiza una calificación existente """
        print("\n--- Actualizar Calificación ---")

        ci = input("CI del estudiante:").strip()
        estudiante = EstudianteManager.obtener_por_ci(ci)
        if not estudiante:
            print("[ERROR] No existe estudiante con ese CI")
            return
        
        # Mostrarcalifiaciones del estudiante
        calificaciones = CalificacionManager.obtener_calificaciones_estudiante(estudiante.id)
        if not calificaciones:
            print(f"No hay calificaciones registradas para {estudiante.nombre}")
            return
        
        print(f"\n--- Calificaciones de {estudiante.nombre} ---")
        print("ID | Lab | Título                   | Nota   Actual")
        print("-"*80)

        for calificacion in calificaciones:
            lab = calificacion.id_laboratorio
            nota_str = f"{calificacion.calificacion:.2f}" if calificacion.calificacion else "Sin nota"
            print(f"{calificacion.id:2d} | {lab.numero:2d} | {lab.titulo:20s} | {nota_str:5.2f}")

        try:
            calificacion_id = int(input("\nID de la calificación a actualizar:"))

            # Verificar que la calificacion pertenezca al estudiante

            calificacion_encontrada = None

            for calificacion in calificaciones:
                if calificacion.id == calificacion_id:
                    calificacion_encontrada = calificacion
                    break
            
            if not calificacion_encontrada:
                print("[ERROR] No existe calificación con ese ID")
                return

            lab = calificacion_encontrada.id_laboratorio
            print(f"Actualizando Calificación: {lab.titulo}")
            print(f"Puntaje máximo: {lab.puntaje_maximo}")
            print(f"Nota actual: {calificacion_encontrada.calificacion}")

            try:
                nueva_calificacion = input("Nueva calificación (Dejar en blanco para no cambiar): ").strip()
                nueva_calificacion = float(nueva_calificacion) if nueva_calificacion else None
            except ValueError:
                nueva_calificacion = None

            nuevas_observaciones = input("Nuevas Observaciones (Dejar en blanco para no cambiar): ").strip()
            nuevas_observaciones = nuevas_observaciones  if nuevas_observaciones else None

            if nueva_calificacion is None and nuevas_observaciones is None:
                print("[ERROR] No se realizaron cambios.")
                return
            
            if CalificacionManager.actualizar_calificacion(calificacion_id, nueva_calificacion, nuevas_observaciones):
                print("[OK] Calificación actualizada exitosamente.")
            else:
                print("[ERROR] No se pudo actualizar la calificación.")
        
        except ValueError:
            print("[ERROR] ID de laboratorio no válido")
    
    def eliminar_calificacion(self):
        """ Elimina una calificación del sistema """
        print("\n--- Eliminar Calificación ---")

        ci = input("CI del estudiante:").strip()

        estudiante = EstudianteManager.obtener_por_ci(ci)
        if not estudiante:
            print("[ERROR] No existe estudiante con ese CI")
            return
        
        # Mostrar calificaciones del estudiante
        calificaciones = CalificacionManager.obtener_calificaciones_estudiante(estudiante.id)

        if not calificaciones:
            print(f"No hay calificaciones registradas para {estudiante.nombre}")
            return
        
        print(f"\nCalificaciones de {estudiante.nombre}:")
        print("ID | Lab | Título                   | Nota   ")
        print("-"*80)

        for calificacion in calificaciones:
            lab = calificacion.id_laboratorio
            nota_str = f"{calificacion.calificacion:.2f}" if calificacion.calificacion else "Sin nota"
            print(f"{calificacion.id:2d} | {lab.numero:2d} | {lab.titulo:20s} | {nota_str:5.2f}")
        
        try:
            calificacion_id = int(input("\nID de la calificación a eliminar:"))

            # Verificar que la calificacion pertenezca al estudiante
            calificacion_encontrada = None
            for calificacion in calificaciones:
                if calificacion.id == calificacion_id:
                    calificacion_encontrada = calificacion
                    break

            if not calificacion_encontrada:
                print("[ERROR] Calificación no encontrada para este estudiante")
                return
            
            lab = calificacion_encontrada.id_laboratorio
            print(f"\nCalificación a eliminar: {lab.titulo} - {calificacion_encontrada.calificacion}")

            confirmacion = input("\n¿Está seguro de eliminar la calificación? (s/N): ").strip().lower()

            if confirmacion != "s":
                print("Operacion Cancelada")
                return
            
            resultado = CalificacionManager.eliminar_calificacion(calificacion_id)

            if resultado['success']:
                print(f"[OK] {resultado['mensaje']}")
            else:
                print(f"[ERROR] {resultado['mensaje']}")

        except ValueError:
            print("[ERROR] ID no valido")
    
    def calificar_por_lotes(self):
        """ Permite calificar varios estudiantes al mismo tiempo """

        print("\n--- Calificar por Lotes ---")

        # Mostrar laboratorios disponibles
        materias = MateriaManager.listar_materias()
        if not materias:
            print("[ERROR] No hay materias registradas.")
            return
        
        print("\nLaboratorios Disponibles:")
        for materia in materias:
            laboratorios = LaboratorioManager.listar_laboratorios_por_materia(materia.id)
            if laboratorios:
                print(f"\n{materia.sigla}")
                for laboratorio in laboratorios:
                    print(f"  ID: {laboratorio.id} - {laboratorio.titulo}")
        
        try:
            laboratorio_id = int(input("\nID del laboratorio: "))
            laboratorio = LaboratorioManager.obtener_laboratorio(laboratorio_id)

            if not laboratorio:
                print("[ERROR] No existe laboratorio con ese ID.")
                return

            print("\nIngrese las calificaciones en formato: CI, calificacion")
            print("Ejemplo: 123456789, 10.0")
            print("Ingrese 'fin' para finalizar.")

            calificaiones_dict = {}
            while True:
                entrada = input("\nIngrese CI, calificacion (fin para finalizar): ").strip()

                if not entrada.lower() == "fin":
                    break

                if ',' not in entrada:
                    print("[ERROR] Formato incorrecto. Ingrese CI, calificacion (ej: 123456789, 10.0)")                    
                    continue

                try:
                    ci, calificacion_str = entrada.split(',')
                    ci = ci.strip()
                    calificacion = float(calificacion_str.strip())

                    # Verificar que el estudiante existe
                    estudiante = EstudianteManager.obtener_por_ci
                    if not estudiante:
                        print("[ERROR] No existe estudiante con ese CI")
                        return
                    
                    calificacion = float(calificacion_str.strip())

                    print(f"[OK] Calificando {estudiante.nombre} con {calificacion}")
            
                except ValueError:
                    print("[ERROR] Calificacion no válida")
                    continue
            
            if not calificaciones_dict:
                print("[ERROR] No se ingresaron calificaciones")
                return
            
            confirmacion = input("\n¿Está seguro de calificar estos estudiantes? (s/N): ").strip().lower()

            if confirmacion != "s":
                print("Operacion Cancelada")
                return
            
            resultado = CalificacionManager.calificar_por_lote(laboratorio_id, calificaciones_dict)

            if resultado['success']:
                print(f"[OK] {resultado['mensaje']}")

                if resultado['errores']:
                    print("\nErrores encontrados:")
                    for error in resultado['errores']:
                        print(f"    - {error}")
            else:
                print(f"[ERROR] {resultado['mensaje']}")
        
        except ValueError:
                print(f"ID de laboratorio no válico")
        
    def estadisticas_calificaciones_paralelo(self):
        """ Muestra estadísticas de calificaciones de un paralelo """

        # Mostrar paralelos disponibles

        materias = MateriaManager.listar_materias()

        if not materias:
            print("[ERROR] No hay materias registradas.")
            return

        print("\nParalelos disponibles:")

        for materia in materias:
            paralelos = ParaleloManager.listar_paralelos_por_materia(materia.id)

            for paralelo in paralelos:
                print(f"ID: {paralelo.id} - {materia.sigla} Paralelo {paralelo.paralelo}")
        
        try:
            paralelo_id = int(input("\nID del paralelo: "))
            paralelo = ParaleloManager.obtener_paralelo(paralelo_id)
            if not paralelo:
                print("[ERROR] No existe paralelo con ese ID.")
                return
            
            from models.calificacion import Calificacion

            stats = Calificacion.estadisticas_paralelo(paralelo)

            print(f"\n---Estadisticas de Calificaciones del Paralelo {paralelo.paralelo} ---")
            print(f"Total Calificaciones: {stats['total_calificaciones']}")
            print(f"Promedio General: {stats['promedio_general']:.2f}")
            print(f"Aprobados: {stats['aprobados']}")
            print(f"Reprobados: {stats['reprobados']}")
            print(f"Sin calificar: {stats['sin_calificar']}")

            if stats['total_calificaciones'] > 0:
                porcentaje_aprobacion = (stats['aprobados'] / stats['total_calificaciones'])*100
                print(f"Porcentaje de Aprobación: {porcentaje_aprobacion:.2f}%")
        
        except ValueError:
            print("[ERROR] ID de paralelo no válido")
    
    # ==========================================================================
    # REPORTES Y EXPORTACION
    # ==========================================================================
    def menu_reportes(self):
        """ Menú de reportes y exportación """
        while True:
            print("")
            print("-"*40)
            print("     REPORTES Y EXPORTACION")
            print("-"*40)
            print("1. Generar reporte PDF por paralelo")
            print("2. Matriz de calificaciones")
            print("3. Ver archivos generados")
            print("0. Volver al menú principal")

            opcion = self.obtener_opcion()
            if opcion == "1":
                self.generar_reporte_pdf()
            elif opcion == "2":
                self.matriz_calificaciones()
            elif opcion == "3":
                self.ver_archivos()
            elif opcion == "0":
                break
            else:
                print("[ERROR] Opción no válida.")
    
    def generar_reporte_pdf(self):
        """ Genera un reporte PDF por paralelo """
        print("\n--- Generar Reporte PDF ---")
        # Mostrar paralelos disponibles
        materias = MateriaManager.listar_materias()
        if not materias:
            print("[ERROR] No hay materias registradas.")
            return
        
        print("\nParalelos Disponibles:")
        for materia in materias:
            paralelos = ParaleloManager.listar_paralelos_por_materia(materia.id)
            for paralelo in paralelos:
                print(f"ID: {paralelo.id} - {materia.sigla} Paralelo {paralelo.paralelo} ({paralelo.contar_estudiantes()} estudiantes) ")        
            
        try:
            paralelo_id = int(input("\nID del paralelo: "))
            paralelo = ParaleloManager.obtener_paralelo(paralelo_id)
            if not paralelo:
                print("[ERROR] No existe paralelo con ese ID.")
                return
            
            print(f"\nGenerando reporte PDF para {paralelo} ...")
            archivo_generado = PDFExporter.generar_reporte_paralelo(paralelo_id)

            if archivo_generado:
                print(f"[OK] Archivo generado: {archivo_generado}")
            else:
                print("[ERROR] No se pudo generar el archivo")
        
        except ValueError:
            print("[ERROR] ID de paralelo no válido")
        
        except Exception as e:
            print(f"[ERROR] Error: {e}")
    
    def matriz_calificaciones(self):
        """ Muestra matriz de calificaciones """
        print("\n--- Matriz de Calificaciones ---")

        materias = MateriaManager.listar_materias()
        if not materias:
            print("[ERROR] No hay materias registradas.")
            return
        
        print("\nParalelos Disponibles:")
        for materia in materias:
            paralelos = ParaleloManager.listar_paralelos_por_materia(materia.id)
            for paralelo in paralelos:
                print(f"ID: {paralelo.id} - {materia.sigla} Paralelo {paralelo.paralelo}")        
        
        try:
            paralelo_id = int(input("\nID del paralelo:"))
            paralelo = ParaleloManager.obtener_paralelo(paralelo_id)
            if not paralelo:
                print("[ERROR] No existe paralelo con ese ID.")
                return
            
            # Obtener matriz de calificaciones

            from models.calificacion import Calificacion
            matriz = Calificacion.matriz_calificaciones_paralelo(paralelo)

            if not matriz:
                print("[ERROR] No hay datos de calificaciones para mostrar.")
                return

            # Obtener laboratorios
            from models.laboratorio import Laboratorio
            laboratorios = list(Laboratorio.obtener_por_materia(paralelo.id_materia))

            if not laboratorios:
                print("[ERROR] No hay laboratorios para mostrar.")
                return
        
            print(f"\n--- Matriz de Calificaciones: {paralelo} ---")

            # Encabezado
            header = "Estudainte".ljust(20)
            for lab in laboratorios:
                header = header + f"Lab {lab.numero:2d}"
            
            header = header + " Prom"
            print(header)
            print("-"*len(header))

            # Datos
            for fila in matriz:
                linea = fila['estudiante'][:24].ljust(25)

                for laboratorio in laboratorios:
                    calificacion = fila['calificaciones'].get(f"lab_{laboratorio.numero}")
                    if calificacion is not None:
                        linea = linea + f"{calificacion:4.2f}"
                    else:
                        linea = linea + "  --"
                linea = linea + f" {fila['promedio']:5.2f}"
                print(linea)
        
        except ValueError:
            print("[ERROR] ID de paralelo no válido")
    
    def ver_archivos(self):
        """ Muestra los archivos generados """
        print("\n--- Archivos Generados ---")

        carpeta_export = "exports"

        if not os.path.exists(carpeta_export):
            print("[ERROR] No hay archivos generados.")
            return
        
        # Buscar Archivos PDF y Excel

        archivos_pdf = []
        archivos_excel = []

        for root, dirs, files in os.walk(carpeta_export):
            for file in files:
                if file.endswith(".pdf"):
                    archivos_pdf.append(os.path.join(root, file))
                elif file.endswith(".xlsx", '.xls'):
                    archivos_excel.append(os.path.join(root, file))
        
        if archivos_pdf:
            print("\Archivos PDF generados: ")
            for i, archivo in enumerate(archivos_pdf, 1):
                print(f" {i}. {os.path.basename(archivo)}")
        
        if archivos_excel:
            print("\nArchivos Excel generados: ")
            for i, archivo in enumerate(archivos_excel, 1):
                print(f" {i}. {os.path.basename(archivo)}")
        
        if not archivos_pdf and not archivos_excel:
            print("[ERROR] No hay archivos generados.")
    
    def salir(self):
        """ Cierra el Sistema """
        print("\nGracias por usar Away (Sistema de Gestión de Laboratorio).")
        print("¡Hasta pronto!")
        self.running = False

def main():
    """ Funcion principal """
    interfaz = InterfazConsola()
    interfaz.ejecutar()

if __name__ == "__main__":
    main()