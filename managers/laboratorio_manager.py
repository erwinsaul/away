"""
Manager para gestionar laboratorios.
Contiene toda la lógica relacionada con crear, buscar y moficiar laboratorios.
"""

from models.laboratorio import Laboratorio
from models.materia import Materia
from peewee import IntegrityError

class LaboratorioManager:
    """
    Encapsula toda la lógica de negocio para laboratorios.

    Gestiona los laboratorios (prácticas) de cada materia.
    """

    @staticmethod
    def crear_laboratorio(materia_id, titulo, descripcion=None, puntaje_maximo=100.0):
        """
        Crea un nuevo laboratorio para una materia.

        Args:
            materia_id (int): ID de la materia
            titulo (str): Título del laboratorio
            descripcion (str): Descripción del laboratorio
            puntaje_maximo (float): Puntaje máximo del laboratorio
        
        Returns:
            Laboratorio: Instancia creada o None si hubo error
        """
        try:
            materia = Materia.get_by_id(materia_id)

            # Obtener siguiente número
            numero = Laboratorio.obtener_siguiente_numero(materia)
            laboratorio = Laboratorio.create(
                numero=numero,
                titulo=titulo.strip().upper(),
                descripcion=descripcion.strip().upper() if descripcion else None,
                id_materia=materia,
                puntaje_maximo=puntaje_maximo
            )

            print(f"[OK] Laboratorio {numero} creado para {materia.sigla}")
            return laboratorio
        
        except Materia.DoesNotExist:
            print(f"[ERROR] No existe materia con ID {materia_id}")
            return None
        except Exception as e:
            print(f"[ERROR] Error al crear laboratorio: {e}")
            return None
    
    @staticmethod
    def listar_laboratorios_por_materia(materia_id):
        """
        Lista todos los laboratorios de una materia.
        
        Args:
            materia_id (int): ID de la materia
        
        Returns:
            list: Lista de laboratorios ordenados por numero
        """
        try:
            materia = Materia.get_by_id(materia_id)
            return list(Laboratorio.obtener_por_materia(materia))
        except Materia.DoesNotExist:
            print(f"[ERROR] No existe materia con ID {materia_id}")
            return []
    
    @staticmethod
    def obtener_laboratorio(laboratorio_id):
        """
        Obtiene un laboratorio por si ID.

        Args:
            laboratorio_id (int): ID del laboratorio

        Returns:
            Laboratorio: Instancia o None si no existe
        """
        try:
            return Laboratorio.get_by_id(laboratorio_id)
        except Laboratorio.DoesNotExist:
            print(f"[ERROR] No existe laboratorio con ID {laboratorio_id}")
            return None

    @staticmethod
    def actualizar_laboratorio(laboratorio_id, **campos):
        """
        Actualiza un laboratorio.

        Args:
            laboratorio_id (int): ID del laboratorio
            **campos: Campos a actualizar
        
        Returns:
            bool: True si se actualizó correctamente
        """

        try:
            laboratorio = Laboratorio.get_by_id(laboratorio_id)

            # Validar número único dentro de la materia si se actualiza
            if 'numero' in campos:
                nuevo_numero = campos['numero']
                if nuevo_numero != laboratorio.numero:
                    existe = Laboratorio.select().where(
                        (Laboratorio.id_materia == laboratorio.id_materia) &
                        (Laboratorio.numero == nuevo_numero) &
                        (Laboratorio.id != laboratorio_id)
                    ).exists()

                    if existe:
                        print(f"[ERROR] Ya existe un laboratorio con el número {nuevo_numero} en esta materia")
                        return False
            
            for campo, valor in campo.items():
                if hasattr(laboratorio, campo):
                    if isinstance(valor, str):
                        setattr(laboratorio, campo, valor.strip().upper() if valor else None)
                    else:
                        setattr(laboratorio, campo, valor)
            
            laboratorio.save()
            print(f"[OK] Laboratorio {laboratorio.numero} actualizado")
            return True
        
        except Laboratorio.DoesNotExist:
            print(f"[ERROR] No existe laboratorio con ID {laboratorio_id}")
            return False
        except Exception as e:
            print(f"[ERROR] Error al actualizar laboratorio: {e}")
            return False
    
    @staticmethod
    def eliminar_laboratorio(laboratorio_id, forzar=False):
        """
        Elimina un laboratorio del sistema.

        Args:
            laboratorio_id (int): ID del laboratorio
            forzar (bool): Si True, elimina incluso si tiene calificaciones

        Returns:
            dict: Resultado de la operación
        """

        try:
            laboratorio = Laboratorio.get_by_id(laboratorio_id)
            num_calificaciones = laboratorio.contar_calificaciones()

            if not forzar and num_calificaciones > 0:
                return {
                    'success': False,
                    'message': f'No se puede eliminar {laboratorio.numero}. Tiene {num_calificaciones} calificaciones.',
                    'calificaciones': num_calificaciones
                }
            
            if forzar and num_calificaciones > 0:
                # Eliminar calificaciones primero
                from models.calificacion import calificaciones

                eliminadas = Calificacion.delete().where(
                    Calificacion.id_laboratorio == laboratorio
                ).execute()

                print(f"[INFO] Eliminadas {eliminadas} calificaciones")
            
            lab_info = str(laboratorio)

            laboratorio.delete_instance()

            return {
                'success': True,
                'mensaje': f'laboratorio eliminado exitosamente',
            }
        
        except Laboratorio.DoesNotExist:
            return {
                'success': False,
                'mensaje': f'No existe laboratorio con ID {laboratorio_id}'
            }
        except Exception as e:
            return {
                'success': False,
                'mensaje': f'Error al eliminar laboratorio: {e}'
            }
