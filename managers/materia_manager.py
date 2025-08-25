"""
Manager para la tabla de materias.
Contiene toda la lógica relacionada con crear, buscar y moficiar materias.
"""

from models.materia import Materia
from peewee import IntegrityError

class MateriaManager:
    """
    Encapsula toda la lógica de negocio para materias.
    """

    @staticmethod
    def crear_materia(materia, sigla):
        """
        Crea una nueva materia.
        Args:
            materia (str): Nombre de la materia
            sigla (str): Sigla de la materia (ej: SIS1110)
        Returns:
            Materia: La materia creada
        """

        try:
            nueva_materia = Materia.create(
                materia=materia.strip().upper(),
                sigla=sigla.strip().upper()
            )

            print(f"[OK] Materia {sigla} creada exitosamente")
            return nueva_materia
        except IntegrityError:
            print(f"[ERROR] Ya existe una materia con sigla {sigla}")
            return None
        except Exception as e:
            print(f"[ERROR] Error inesperado: {e}")
            return None
    
    @staticmethod
    def listar_materias():
        """
        Obtiene todas las materias ordenadas por su sigla.
        Returns:
            List: LIsta de Materias
        """
        return list(Materia.select().order_by(Materia.sigla))
    
    @staticmethod
    def obtener_materia(materia_id):
        """
        Obtiene una materia por su id.

        Args:
            materia_id (int): ID de la materia

        Returns:
            Materia: Instancia o None si no existe
        """
        try:
            return Materia.get_by_id(materia_id)
        except Materia.DoesNotExist:
            print(f"[ERROR] No existe materia con ID {materia_id}")
            return None
    
    @staticmethod
    def obtener_materia_por_sigla(sigla):
        """
        Busca una materia por su sigla.

        Args:
            sigla (str): Sigla de la materia

        Returns:
            Materia: Instancia o None si no existe
        """
        return Materia.obtener_por_sigla(sigla)
    
    @staticmethod
    def actualizar_materia(materia_id, **campos):
        """
        Actualiza datos de una materia.

        Args:
            materia_id (int): ID de la materia
            **campos: Campos a actualizar
        
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            materia = Materia.get_by_id(materia_id)

            # Validar sigla única si se está actualizando
            if 'sigla' in campos:
                sigla_nueva = campos['sigla'].strip().upper()
                if sigla_nueva != materia.sigla:
                    existe = Materia.select().where(
                        (Materia.sigla == sigla_nueva) &
                        (Materia.id != materia_id)
                    ).exist()

                    if existe:
                        print(f"[ERROR] Ya existe una materia con la sigla {sigla_nueva}")
                        return False
                
                campos['sigla'] = sigla_nueva

            #Actualizar solo los campos proporcionados
            for campo, calor in campos.items():
                if hassattr(materia, campo):
                    if isinstance(valor, str):
                        setattr(materia, campo, valor.strip().upper())
                    else:
                        setattr(materia, campo, valor)
            
            materia.save()
            print(f"[OK] Materia {materia.sigla} actualizada")
            return True
        
        except Materia.DoesNotExist:
            printf(f"[ERROR] No existe materia con ID {materia_id}")
            return False
        except IntegrityError:
            printf(f"[ERROR] Error de integridad al actualizar")
            return False
        except Exception as e:
            printf(f"[ERROR] Error al actualizar: {e}")
            return False
    
    @staticmethod
    def eliminar_materia(materia_id, forzar=False):
        """
        Elimina una materia del sistema.

        Args:
            materia_id (int): ID de la materia
            forzar (bool): Forzar eliminación, si True se elimina incluso si tiene estudiantes
        
        Returns:
            dict: Resultado de la operación
        """
        try:
            materia = Materia.get_by_id(materia_id)

            # Verificar dependencias
            num_paralelos = materia.contar_paralelos()
            num_laboratorio = materia.contar_laboratorios()
            num_estudiantes = materia.contar_estudiantes_total()

            if not forzar and (num_paralelos > 0 or num_laboratorio > 0 or num_estudiantes > 0):
                return {
                    'succes': False,
                    'mensaje': f'No se puede eliminar {materia.sigla}. Tiene {num_paralelos} paralelos, {num_laboratorio} laboratorios y {num_estudiantes} estudiantes',
                    'dependencias':{
                        'paralelos': num_paralelos,
                        'laboratorios': num_laboratorio,
                        'estudiantes': num_estudiantes
                    }
                }
            
            # Si se fuerza la eliminación, eliminar dependencias primero
            if forzar:
                from models.calificacion import calificacion
                from models.estudiante import Estudiante
                from models.paralelo import Paralelo
                from models.laboratorio import Laboratorio

                # Eliminar calificaciones
                calificaciones_eliminadas = 0
                for paralelo in materia.paralelos:
                    for estudiante in paralelo.estudiantes:
                        eliminadas = Calificacion.delete().where(
                            Calificacion.id_estudiante == estudiante
                        ).execute()
                        calificaciones_eliminadas = calificaciones_eliminadas
                
                # Eliminar estudiantes
                estudiantes_eliminados = 0
                for paralelo in materia.paralelos:
                    eliminados = Estudiante.delete().where(
                        Estudiante.id_paralelo == paralelo
                    ).execute()
                    estudiantes_eliminados = estudiantes_eliminados + eliminados

                # Eliminar laboratorios
                laboratorios_eliminados = Laboratorio.delete().where(
                    Laboratorio.id_materia == materia
                ).execute()

                # Eliminar paralelos
                paralelos_eliminados = Paralelo.delete().where(
                    Paralelo.id_materia == materia
                ).execute()

                print(f"[INFO] Eliminadas {calificaciones_eliminadas} calificaciones")
                print(f"[INFO] Eliminados {estudiantes_eliminados} estudiantes")
                print(f"[INFO] Eliminados {laboratorios_eliminados} laboratorios")
                print(f"[INFO] Eliminados {paralelos_eliminados} paralelos")
            
            # Eliminar la materia
            sigla_eliminada = materia.sigla
            materia.delete_instance()

            print(f"[OK] Materia {sigla_eliminada} eliminada")

            return {
                'succes': True,
                'mensaje': f'Materia {sigla_eliminada} eliminada',
                'materia_eliminada': sigla_eliminada
            }
        except Materia.DoesNotExist:
            return {
                'succes': False,
                'mensaje': f'No existe materia con ID {materia_id}'
            }
        except Exception as e:
            return {
                'succes': False,
                'mensaje': f'Error al eliminar materia: {e}'
            }
    
    @staticmethod
    def obtener_estadisticasgenerales():
        """
        Obtiene estadísticas generales del sistema.

        Returns:
            dict: Diccionario con estadísticas
        """

        materias = Materia.select()

        total_materias = materias.count()
        total_paralelos = sum(m.contar_paralelos() for m in materias)
        total_estudiante = sum(m.contar_estudiantes_total() for m in materias)
        total_laboratorios = sum(m.contar_laboratorios() for m in materias)

        return {
            'total_materias': total_materias,
            'total_paralelos': total_paralelos,
            'total_estudiantes': total_estudiante,
            'total_laboratorios': total_laboratorios,
            'promedio_paralelos_por_materia': round(total_paralelos / total_materias, 1) if total_materias > 0 else 0,
            'promedio_estudiantes_por_materia': round(total_estudiante / total_materias, 1) if total_materias > 0 else 0,
        }

    @staticmethod
    def buscar_materias(termino_busqueda):
        """
        Busca materias por nombre o sigla.

        Args:
            termino_busqueda (str): Término a buscar
        
        Returns:
            list: Materias que coinciden
        """
        return list(Materia.select().where(
            (Materia.materia.contains(termino_busqueda)) |
            (Materia.sigla.contains(termino_busqueda)) 
        ).order_by(Materia.sigla))

                

