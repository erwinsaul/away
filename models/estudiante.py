"""
Modelo para los estudiantes inscritos en cada paralelo.
Cada estudiante tiene un CI, y pertenece a un grupo de laboratorio.
"""
from peewee import *
from .database import BaseModel
from .paralelo import Paralelo

class Estudiante(BaseModel):
    """
    Representa un estudiante inscrito en un paralelo.
    El CI es único en todo el sistema, pero un estudiante
    puede estar en diferentes paralelos si cursa múltiples materias
    """
    nombre = CharField(max_length=200)
    ci = CharField(max_length=20)
    id_paralelo = ForeignKeyField(Paralelo, backref='estudiantes')
    grupo = CharField(max_length=100, null=True) # Grupo 1, Grupo 2, ec
    
    class Meta:
        table_name = 'estudiantes'
        
        indexes = (
            (('id_paralelo', 'ci'), True),
        )

    def __str__(self):
        return f"{self.nombre} - {self.ci}"
    
    def nombre_completo_con_info(self):
        """Retorna nombre con información de grupo y paralelo"""
        grupo_str = f" - {self.grupo} " if self.grupo else ""
        return f"{self.nombre} ({self.id_paralelo.paralelo}) {grupo_str}"

    def contar_calificaciones(self):
        """Cuenta calificaciones registradas"""
        return self.calificaciones.count()
    

    def promedio_calificaciones(self):
        """Calcula el promedio de calificaciones"""
        from .calificacion import Calificacion
        from .laboratorio import Laboratorio

        # Obtener todos los laboratorios de la materia del estudiante
        materia = self.id_paralelo.id_materia
        total_laboratorios = Laboratorio.select().where(Laboratorio.id_materia == materia).count()

        if total_laboratorios == 0:
            return 0.0

        # Obtener solo las calificaciones que tienen valor
        calificaciones = self.calificaciones.where(Calificacion.calificacion.is_null(False))
        total_calificaciones = sum(cal.calificacion for cal in calificaciones)

        # Dividir por el total de laboratorios posibles, no solo los que tienen nota
        return round(total_calificaciones / total_laboratorios, 2)
    
    def calificaciones_por_laboratorio(self):
        """Retorna diccionario con calificaciones por laboratorio"""
        from .calificacion import Calificacion
        from .laboratorio import Laboratorio

        resultado = {}
        calificaciones = (self.calificaciones
                            .join(Laboratorio)
                            .order_by(Laboratorio.numero))
        
        for cal in calificaciones:
            lab = cal.id_laboratorio
            resultado[f"Lab {lab.numero}"] = {
                'titulo': lab.titulo,
                'calificacion': cal.calificacion,
                'fecha': cal.fecha_registro
            }
        
        return resultado
    
    @classmethod
    def buscar_por_ci(cls, ci):
        """Busca un estudiante por cédula de identidad (retorna el primero si hay múltiples)"""
        try:
            # Buscar en todos los estudiantes con esta CI
            estudiantes = list(cls.select().where(cls.ci == ci))
            if estudiantes:
                # Si hay múltiples, retornar el primero (podríamos especificar criterios adicionales)
                # En la mayoría de los casos, esperamos que sea solo uno
                return estudiantes[0]
            else:
                return None
        except cls.DoesNotExist:
            return None

    @classmethod
    def buscar_por_ci_en_paralelo(cls, ci, paralelo):
        """Busca un estudiante específico con CI en un paralelo específico"""
        try:
            return cls.get((cls.ci == ci) & (cls.id_paralelo == paralelo))
        except cls.DoesNotExist:
            return None

    @classmethod
    def buscar_todos_por_ci(cls, ci):
        """Busca todos los estudiantes con una cédula de identidad específica (múltiples paralelos)"""
        return list(cls.select().where(cls.ci == ci))
    
    @classmethod
    def obtener_por_paralelo_grupo(cls, paralelo, grupo):
        """Obtiene estudiantes de un paralelo y grupo específico"""
        return cls.select().where(
            (cls.id_paralelo == paralelo) &
            (cls.grupo == grupo)
        ).order_by(cls.nombre)

    