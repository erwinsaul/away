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
    
    
