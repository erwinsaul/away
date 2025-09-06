"""
Manager para gestionar calificaciones.
Contiene toda la lógica relacionada con crear, buscar y moficiar calificaciones.
"""

from models.calificacion import Calificacion
from models.estudiante import Estudiante
from models.laboratorio import Laboratorio
from peewee import IntegrityError

class CalificacionManager:
    """
    Encapsula toda la lógica de negocio para calificaciones.

    Gestiona todas las calificaciones de los estudiantes en cada laboratorio.
    """

    @staticmethod
    def registrar_calificacion(laboratorio_id, estudiante_id, calificacion, observacion=None):
        """
        Registra una calificación

        Args:
            laboratorio_id (int): ID del laboratorio
            estudiante_id (int): ID del estudiante
            calificacion (float): Nota del estudiante
            observacion (str): Comentarios opcionales
        
        Returns:
            Calificacion: Instancia creada o None si hay error
        """

        try:
            laboratorio = Laboratorio.get_by_id(laboratorio_id)
            estudiante = Estudiante.get_by_id(estudiante_id)

            # Validar que la calificación esté en un rango válido
            if calificacion < 0 or calificacion > laboratorio.puntaje_maximo:
                print(f"[ERROR] Calificación de estar entre 0 y {laboratorio.puntaje_maximo}")
                return None
            
            nueva_calificacion = Calificacion.create(
                id_laboratorio=laboratorio,
                id_estudiante=estudiante,
                calificacion=calificacion,
                observaciones=observacion.strip().upper() if observacion else None
            )

            print(f"[OK] Calificación registrada: {estudiante.nombre} - {laboratorio.numero}: {calificacion}")
            return nueva_calificacion
        
        except (Laboratorio.DoesNotExist, Estudiante.DoesNotExist):
            print(f"[ERROR] No existe el laboratorio o el estudiante especificado")
            return None
        except IntegrityError:
            print(f"[ERROR] Ya existe una calificación para este estudiante en este laboratorio")
            return None
        except Exception as e:
            print(f"[ERROR] Error al registrar calificación: {e}")
            return None
    
    @staticmethod
    def obtener_calificaciones_estudiante(estudiante_id):
        """
        Obtiene todas las calificaciones de un estudiante.

        Args:
            estudiante_id (int): ID del estudiante

        Returns:
            list: Lista de calificaciones
        """
        try:
            estudiante = Estudiante.get_by_id(estudiante_id)
            return list(estudiante.calificaciones.join(Laboratorio).order_by(Laboratorio.numero))
        except Estudiante.DoesNotExist:
            print(f"[ERROR] No existe estudiante con ID {estudiante_id}")
            return []
    
    @staticmethod
    def obtener_calificaciones_laboratorio(laboratorio_id):
        """
        Obtiene todas las calificaciones de un laboratorio.

        Args:
            laboratorio_id (int): ID del laboratorio

        Returns:
            list: Lista de calificaciones ordenadas por estudiante
        """

        try:
            laboratorio = Laboratorio.get_by_id(laboratorio_id)
            return list(laboratorio.calificaciones.join(Estudiante).order_by(Estudiante.nombre))
        except Laboratorio.DoesNotExist:
            print(f"[ERROR] No existe laboratorio con ID {laboratorio_id}")
            return []
    
    @staticmethod
    def obtener_calificacion_especifica(laboratorio_id, estudiante_id):
        """
        Obtiene una calificación específica de un estudiante en un laboratorio.

        Args:
            laboratorio_id (int): ID del laboratorio
            estudiante_id (int): ID del estudiante
        
        Returns:
            Calificacion: Instancia o None si no existe
        """
        try:
            return Calificaciones.get(
                (Calificacion.id_laboratorio == laboratorio_id) &
                (Calificacion.id_estudiante == estudiante_id)
            )
        except Calificacion.DoesNotExist:
            return None

    @staticmethod
    def actualizar_calificacion(calificacion_id, nueva_calificacion=None, observacion=None):
        """
        Actualiza una calificación existente.

        Args:
            calificacion_id (int): ID de la calificación
            nueva_calificacion (float): Nueva calificación
            observacion (str): Comentarios opcionales
        
        Returns:
            bool: True si se actualizó correctamente
        """

        try:
            calificacion = Calificacion.get_by_id(calificacion_id)

            if nueva_calificacion is not None:
                # Validar rango
                puntaje_max = calificacion.id_laboratorio.puntaje_maximo
                if nueva_calificacion < 0 or nueva_calificacion > puntaje_max:
                    print(f"[ERROR] Calificación de estar entre 0 y {puntaje_max}")
                    return False
                
                calificacion.calificacion = nueva_calificacion
            
            if observacion is not None:
                calificacion.observaciones = observacion.strip().upper() if observacion else None

            calificacion.save()
            print(f"[OK] Calificacion actualizada")
            return True
    
        except Calificacion.DoesNotExist:
            print(f"[ERROR] No existe calificacion con ID {calificacion_id}")
            return False
        except Exception as e:
            print(f"[ERROR] Error al actualizar: {e}")
            return False
    
    @staticmethod
    def eliminar_calificacion(calificacion_id):
        """
        Elimina un calificación.

        Args:
            calificacion_id (int): ID de la calificación
        
        Returns:
            dict: Resultado de la operación
        """

        try:
            calificacion = Calificacion.get_by_id(calificacion_id)
            calificacion_info = f"{calificacion.id_estudiante.nombre} - {calificacion.id_laboratorio.titulo}"

            calificacion.delete_instance()

            return {
                'success': True,
                'mensaje': f'Calificacion eliminada: {calificacion_info}',                
            }
        
        except Calificacion.DoesNotExist:
            return {
                'success': False,
                'mensaje': f'No existe calificacion con ID {calificacion_id}'
            }
        except Exception as e:
            return {
                'success': False,
                'mensaje': f'Error al eliminar: {e}'
            }
    
    @staticmethod
    def calificar_por_lotes(laboratorio_id, calificacion_dict):
        """
        Registra múltiples calificacion de una vez.

        Args:
            laboratorio_id (int): ID del laboratorio
            calificacion_dict (dict): Diccionario con el formato {estudiante_id: calificacion, ...}
        
        Returns:
            dict: Resultado de la operación por lotes
        """
        try:
            laboratorio = Laboratorio.get_by_id(laboratorio_id)

            exitosas = 0
            errores = []

            for estudiante_id, calificacion in calificacion_dict.items():
                try:
                    estudiante = Estudiante.get_by_id(estudiante_id)

                    # Verificar si ya existe calificación

                    cal_existente = CalificacionManager.obtener_calificacion_especifica(laboratorio_id, estudiante_id)
                    if cal_existente:
                        # Actualizar existente
                        cal_existente.calificacion = nota
                        cal_existente.save()
                    else:
                        # Crear nueva
                        Calificacion.create(
                            id_laboratorio=laboratorio,
                            id_estudiante=estudiante,
                            calificacion=nota 
                        )
                    exitosas = exitosas + 1
                except Exception as e:
                    errores.append(f"Estudiante {estudiante_id}: {e}")
            
            return {
                'success': True,
                'exitosas': exitosas,
                'errores': errores,
                'mensaje': f'Procesadas {exitosas} calificaciones. {len(errores)} errores.'
            }
        
        except Laboratorio.DoesNotExist:
            return {
                'success': False,
                'mensaje': f'No existe laboratorio con ID {laboratorio_id}'
            }
        except Exception as e:
            return {
                'success': False,
                'mensaje': f'Error en procesamiento por lotes: {e}'
            }




