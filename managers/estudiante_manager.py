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
    

