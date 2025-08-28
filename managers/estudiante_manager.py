"""
Manager para gestionar estudiantes.
Incluye registro, búsqueda y organzación por grupos.
"""

from models.estudiante import Estudiante
from models.paralelo import Paralelo
from peewee import IntegrityError

class EstudianteManager:
    """Gestiona todas las operaciones con estudiantes"""

    @staticmethod
    def registrar_estudiante(nombre, ci, paralelo_id, grupo=None):
        """
        Registra un nuevo estudiante en un paralelo.

        Args:
            nombre (str): Nombre del estudiante
            ci (str): CI del estudiante
            paralelo_id (int): ID del paralelo
            grupo (str): Grupo del estudiante (Opcional)
        
        Returns:
            Estudiante: El estudiante creado o None si hay error
        """
        try:
            # Verificar que el paralelo existe
            paralelo = Paralelo.get_by_id(paralelo_id)

            estudiante = Estudiante.create(
                nombre = nombre.strip().upper(),
                ci = ci.strip().upper(),
                id_paralelo = paralelo,
                grupo = grupo.strip().upper() if grupo else None
            )

            print(f"[OK] Estudiante {nombre} registrado en {paralelo}")
            return estudiante
        except Paralelo.DoesNotExist:
            print(f"[ERROR] No existe paralelo con ID {paralelo_id}")
            return None
        except IntegrityError:
            print(f"[ERROR] Ya existe un estudiante con CI {ci} en este paralelo")
            return None
        except Exception as e:
            print(f"[ERROR] Error al registrar estudiante: {e}")
            return None
        
    @staticmethod
    def listar_por_paralelo(paralelo_id, ordenar_por='nombre'):
        """
        Lista de estudiantes de un paralelo.
        Args:
            paralelo_id (int): ID del paralelo
            ordenar_por (str): Campo por el que ordenar (nombre, grupo, ci)
        Returns:
            list: Lista de estudiantes
        """
        try:
            paralelo = Paralelo.get_by_id(paralelo_id)

            if ordenar_por == 'grupo':
                return list(paralelo.estudiantes.order_by(Estudiante.grupo, Estudiante.nombre))
            elif ordenar_por == 'ci':
                return list(paralelo.estudiantes.order_by(Estudiante.ci, Estudiante.nombre))
            else:
                return list(paralelo.estudiantes.order_by(Estudiante.nombre))
        
        except Paralelo.DoesNotExist:
            print(f"[ERROR] No existe paralelo con ID {paralelo_id}")
            return []

    @staticmethod
    def obtener_estudiante(estudiante_id):
        """
        Obtiene un estudiante por su ID.

        Args:
            estudiante_id (int): ID del estudiante

        Returns:
            Estudiante: Instancia o None si no existe
        """

        try:
            return Estudiante.get_by_id(estudiante_id)
        except Estudiante.DoesNotExist:
            print(f"[ERROR] No existe estudiante con ID {estudiante_id}")
            return None
    
    @staticmethod
    def buscar_por_ci(ci):
        """
        Busca un estudiante por su CI.

        Args:
            ci(str): Cédula de identidad
        
        Returns:
            Estudiante: Instancia encontrada o None
        """
        return Estudiante.buscar_por_ci(ci)
    
    @staticmethod
    def actualizar_estudiante(estudiante_id, **campos):
        """
        Actualiza información de un estudiante.

        Args:
            estudiante_id (int): ID del estudiante
            **campos: Campos a actualizar
        
        Returns:
            bool: True si se actualizó correctamente
        """

        try:
            estudiante = Estudiante.get_by_id(estudiante_id)

            if 'ci' in campos:
                nuevo_ci = campos['ci'].strip()
                if nuevo_ci != estudiante.ci:
                    existe = Estudiante.select().where(
                        (Estudiante.ci == nuevo_ci) &
                        (Estudiante.id != estudiante_id)
                    ).exist()

                    if existe:
                        print("[ERROR] Ya existe estudiante con CI {nuevo_ci}")
                        return False
                
                campos['ci'] = nuevo_ci
            
            # Validar paralelo si se está cambiando

            if 'id_paralelo' in campos:
                try:
                    nuevo_paralelo = Paralelo.get_by_id(campos['id_paralelo'])
                    campos['id_paralelo'] = nuevo_paralelo
                except Paralelo.DoesNotExist:
                    print(f"[ERROR] No existe paralelo con ID {campos['id_paralelo']}")
                    return False
            
            # Actualizar campos
            for campo, valor in campos.items():
                if hasattr(estudiante, campo):
                    setattr(estudiante, campo, valor.strip() if valor else None)
                else:
                    setattr(estudiante, campo, valor)
            
            estudiante.save()
            print(f"[OK] Estudiante{estudiante.nombre} actualizado")
            return True
        except Estudiante.DoesNotExist:
            print(f"[ERROR] No existe estudiante con ID {estudiante_id}")
            return False
        except Exception as e:
            print(f"[ERROR] Error al actualizar: {e}")
            return False
    
    @staticmethod
    def actualizar_grupo(estudiante_id, nuevo_grupo):
        """
        Actualiza el grupo de un estudiante.

        Args:
            estudiante_id (int): ID del estudiante
            nuevo_grupo (str): Nuevo grupo
        
        Returns:
            bool: True si se actualizó correctamente
        """

        return EstudianteManager.actualizar_estudiante(
            estudiante_id,
            grupo=nuevo_grupo
        )
    
    @staticmethod
    def eliminar_estudiante(estudiante_id, forzar=False):
        """
        Elimina un estudiante del sistema.

        Args:
            estudiante_id (int): ID del estudiante
            forzar (bool): Si True, elimina aunque tenga calificaciones
        
        Returns:
            dict: Resultado de la operación
        """

        try:
            estudiante = Estudiante.get_by_id(estudiante_id)
            num_calificaciones = estudiante.contar_calificaciones()

            if not forzar and num_calificaciones > 0:
                return {
                    'success': False,
                    'message': f'No se puede eliminar {estudiante.nombre}. Tiene {num_calificaciones} calificaciones registradas.',
                    'calificaciones': num_calificaciones
                }
            
            if forzar and num_calificaciones > 0:
                # Eliminar calificaciones primero
                from models.calificacion import calificaciones

                calificaciones_eliminadas = Calificacion.delete().where(
                    Calificacion.id_estudiante == estudiante
                ).execute()

                print(f"[INFO] Eliminadas {calificaciones_eliminadas} calificaciones")

            estudiante_info = f"{estudiante.nombre} ({estudiante.ci})"
            estudiante.delete_instance()

            return {
                'sucess': True,
                'message': f'Estudiante {estudiante_info} eliminado exitosamente',
            }
        
        except Estudiante.DoesNotExist:
            return {
                'success': False,
                'mensaje': f"No existe estudiante con ID {estudiante_id}"
            }
        
        except Exception as e:
            return {
                'success': False,
                'mensaje': f"Error al eliminar estudiante: {e}"
            }
    
    @staticmethod
    def organizar_grupos_automatico(paralelo_id, estudiantes_por_grupo=5):
        """
        Organiza los grupos de estudiantes en grupos.

        Args:
            paralelo_id (int): ID del paralelo
            estudiantes_por_grupo (int): Cantidad por grupo
        
        Returns:
            dict: Resultado de la organización
        """

        try:
            estudiantes = EstudianteManager.listar_por_paralelo(paralelo_id)

            if not estudiantes:
                return {
                    'success': False,
                    'message': "No hay estudiantes en el paralelo"
                }

            # Calcular número de grupos necesarios
            total_estudiantes = len(estrudiantes)
            num_grupos = (total_estudiantes + estudiantes_por_grupo - 1) // estudiantes_por_grupo

            grupos_creados = 0

            for i, estudiante in enumerate(estudiantes):
                numero_grupo = (i // estudiantes_por_grupo) + 1
                nombre_grupo = f"Grupo {numero_grupo}"

                estudiante.grupo = nombre_grupo
                estudiante.save()

                if numero_grupo > grupos_creados:
                    grupos_creados = numero_grupo
            
            return {
                'success': True,
                'grupos_creados': grupos_creados,
                'total_estudiantes': total_estudiantes,
                'mensaje': f"{grupos_creados} grupos creados {total_estudiantes} estudiantes"
            }
    
        except Exception as e:
            return {'success': False, 'mensaje': f"Error: {e}"}
        
    @staticmethod
    def obtener_estadisticas_paralelo(paralelo_id):
        """
        Obtiene estadísticas de un paralelo.

        Args:
            paralelo_id (int): ID del paralelo
        
        Returns:
            dict: Estadísticas del paralelo
        """

        try:
            paralelo = Paralelo.get_by_id(paralelo_id)
            estudiantes = list(paralelo.estudiantes)

            # Contar grupos
            grupos = set()
            estudiantes_sin_grupo = 0
            for estudiante in estudiantes:
                if estudiante.grupo:
                    grupos.add(estudiante.grupo)
                else:
                    estudiantes_sin_grupo = estudiantes_sin_grupo + 1

            # Calcular promedios
            promedios = [est.promedio_calificaciones() for est in estudiantes]
            promedio_general = sum(promedios) / len(promedios) if promedios else 0

            return {
                'total_estudiantes': len(estudiantes),
                'total_grupos':len(grupos),
                'estudiantes_sin_grupo': estudiantes_sin_grupo,
                'promedio_general': round(promedio_general, 2),
                'grupos_lista': sorted(list(grupos)),
                'paralelo_info': f"{paralelo.id_materia.sigla} - Paralelo {paralelo.paralelo}"                
            }
        except Paralelo.DoesNotExist:
            return{'error': f"No existe paralelo con ID {paralelo_id}"}
        except Exception as e:
            return{'error': f"Error: {e}"}



            

    

