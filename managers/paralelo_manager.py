"""
Manager para gestionar paralelos.
Contiene toda la lógica relacionada con crear, buscar y moficiar paralelos.
"""

from models.paralelo import Paralelo
from models.materia import Materia
from models.estudiante import Estudiante
from peewee import IntegrityError

class ParaleloManager:
    """
    Encapsula toda la lógica de negocio para paralelos.
    """
    @staticmethod
    def crear_paralelo(materia_id, paralelo_nombre, docente_teoria):
        """
        Crea un nuevo paralelo para una materia.

        Args:
            materia_id (int): ID de la materia
            paralelo_nombre (str): Nombre del paralelo
            docente_teoria (str): Docente de la teoria
        
        Returns:
            Paralelo: El paralelo creado o None si hay error
        """
        try:
            materia = Materia.get_by_id(materia_id)
            nuevo_paralelo = Paralelo.create(
                id_materia=materia,
                paralelo=paralelo_nombre.strip().upper(),
                docente_teoria=docente_teoria.strip().upper()
            )
            print(f"[OK] Paralelo {paralelo.nombre} creado para {materia.sigla}")
            return nuevo_paralelo
        except Materia.DoesNotExist:
            print(f"[ERROR] No existe materia con ID {materia_id}")
            return None
        except IntegrityError:
            print(f"[ERROR] Ya existe un paralelo con nombre {paralelo_nombre} para esta materia")
            return None
        except Exception as e:
            print(f"[ERROR] Error inesperado: {e}")
            return None
    
    @staticmethod
    def listar_paralelos_por_materia(materia_id):
        """
        Lista todos los paralelos de una materia.

        Args:
            materia_id (int): ID de la materia

        Returns:
            list: Lista de Paralelos
        """
        try:
            materia = Materia.get_by_id(materia_id)
            return list(materia.paralelos.order_by(Paralelo.paralelo))
        except Materia.DoesNotExist:
            print(f"[ERROR] No existe materia con ID {materia_id}")
            return []
    
    @staticmethod
    def obtener_paralelo(paralelo_id):
        """
        Obtiene un paralelo por su ID.

        Args:
            paralelo_id (int): ID del paralelo

        Returns:
            Paralelo: Instancia o None si no existe
        """
        try:
            return Paralelo.get_by_id(paralelo_id)
        except Paralelo.DoesNotExist:
            print(f"[ERROR] No existe paralelo con ID {paralelo_id}")
            return None

    @staticmethod
    def actualizar_paralelo(paralelo_id, **campos):
        """
        Actualiza un paralelo.

        Args:
            paralelo_id (int): ID del paralelo
            **campos: Campos a actualizar
        
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            paralelo = Paralelo.get_by_id(paralelo_id)

            # Validar nombre único dentro de la materia si se actualiza
            if 'paralelo' in campos:
                nuevo_nombre = campos['paralelo'].strip().upper()
                if nuevo_nombre != paralelo.paralelo:
                    existe = Paralelo.select().where(
                        (Paralelo.id_materia == paralelo.id_materia) &
                        (Paralelo.paralelo == nuevo_nombre) &
                        (Paralelo.id != paralelo_id)
                    ).exist()

                    if existe:
                        print("[ERROR] Ya existe el paralelo {nuevo_nombre} en esta materia")
                        return False
                
                campos['paralelo'] = nuevo_nombre
            
            for campo, valor in campos.items():
                if hasattr(paralelo, campo):
                    setattr(paralelo, campo, valor)
            
            paralelo.save()
            print(f"[OK] Paralelo actualizado")
            return True
        except Paralelo.DoesNotExist:
            print(f"[ERROR] No existe paralelo con ID {paralelo_id}")
            return False
        except Exception as e:
            print(f"[ERROR] Error al actualizar: {e}")
            return False

    @staticmethod
    def eliminar_paralelo(paralelo_id, forzar=False):
        """
        Elimina un paralelo del sistema.

        Args:
            paralelo_id (int): ID del paralelo
            forzar (bool): Si True, elimina aunque tenga estudiantes
        
        Returns:
            dict: Resultado de la operación
        """
        try:
            paralelo = Paralelo.get_by_id(paralelo_id)

            num_estudiantes = paralelo.contar_estudiantes()

            if not forzar and num_estudiantes > 0:
                return {
                    'succes': False,
                    'mensaje': f'No se puede eliminar {paralelo.nombre}. Tiene {num_estudiantes} estudiantes',
                    'estudiantes': num_estudiantes                    
                }
            
            if forzar and num_estudiantes > 0:
                # Eliminar calificaciones de estudiantes primero
                from models.calificacion import calificaciones

                calificaciones_eliminadas = 0
                for estudiante in paralelo.estudiantes:
                    eliminadas = calificaciones.delete().where(
                        Calificacion.id_estudiante == estudiante
                    ).execute()
                    calificaciones_eliminadas = calificaciones_eliminadas + eliminadas
                
                # Eliminar estudiantes
                estudiantes_eliminados = Estudiante.delete().where(
                    Estudiante.id_paralelo == paralelo
                ).execute()

                print(f"[INFO] Eliminadas {calificaciones_eliminadas} calificaciones")
                print(f"[INFO] Eliminados {estudiantes_eliminados} estudiantes")
            
            paralelo_info = str(paralelo)
            paralelo.delete_instance()

            return {
                'succes': True,
                'mensaje': f'Paralelo {paralelo_info} eliminado exitosamente',
            }
        except Paralelo.DoesNotExist:
            return {
                'succes': False,
                'mensaje': f'No existe paralelo con ID {paralelo_id}'
            }
        except Exception as e:
            return {
                'succes': False,
                'mensaje': f'Error al eliminar paralelo: {e}'
            }
        
