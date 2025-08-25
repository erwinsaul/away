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
    ci = CharField(max_length=20, unique=True)
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
        return f"{sef.nombre} ({self.id_paralelo.paralelo}) {grupo_str}"

    def contar_calificaciones(self):
        """Cuenta calificaciones registradas"""
        return self.calificaciones.count()
    

    def promedio_calificaciones(self):
        """Calcula el promedio de calificaciones"""
        from .calificacion import Calificacion
        calificaciones = self.calificaciones.where(Calificacion.calificacion.is_null(False))

        if not calificaciones.exist():
            return 0.0

        total = sum(cal.calificaciones for cal in calificaciones)
        return round(total / calificaciones.count(), 2)
    
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
                'fecha': cal.fech_registro
            }
        
        return resultado
    
    @classmethod
    def obtener_por_ci(cls, ci):
        """Busca estudiante por cédula de identidad"""
        try:
            return cls.get(cls.ci == ci)
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def obtener_por_paralelo_grupo(cls, paralelo, grupo):
        """Obtiene estudiantes de un paralelo y grupo específico"""
        return cls.select().where(
            (cls.id_paralelo == paralelo) &
            (cls.grupo == grupo)
        ).order_by(cls.nombre)

    