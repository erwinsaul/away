"""
Modelo para los paralelos de cada materia.
Un paralelo es una sección específica (A,B,C,D, etc) de una materia.
"""
from peewee import *
from .database import BaseModel
from .materia import Materia

class Paralelo(BaseModel):
    """
    Representa un paralelo de una materia.
    Por ejemplo: SIS1110 tiene Paralelo A y Paralelo B
    """
    paralelo = CharField(max_length=10) # A, B, C, D, etc.
    id_materia = ForeignKeyField(Materia, backref='paralelos')
    docente_teoria = CharField(max_length=200)

    class Meta:
        table_name = 'paralelos'
        # No puede haber dos paralelos A en la misma materia

        indexes = (
            (('id_materia', 'paralelo'), True),
        )
    
    def __str__(self):
        return f"{self.id_materia.sigla} - Paralelo {self.paralelo}"
    
    def contar_estudiantes(self):
        """Cuenta la cantidad de estudiantes registrados en el paralelo"""
        return self.estudiantes.count()
    
    def contar_grupos(self):
        """Cuenta cuántos grupos tiene cada paralelo"""
        grupos = set()
        for estudiante in self.estudiantes:
            if estudiante.grupo:
                grupos.add(estudiante.grupo)
        return len(grupos)

    def obtener_grupos_lista(self):
        """Retorna lista con nombres de todos los grupos"""
        grupos = set()
        for estudiante in self.estudiantes:
            if estudiante.grupo:
                grupos.add(estudiante.grupo)
        return sorted(list(grupos))
    
    def promedio_general(self):
        """Retorna el promedio general de todos los estudiantes"""
        from .calificacion import Calificacion
        from .estudiante import Estudiante
        from .laboratorio import Laboratorio
        # Obtener todos los laboratorios de la materia de este paralelo
        total_laboratorios = Laboratorio.select().where(Laboratorio.id_materia == self.id_materia).count()
        if total_laboratorios == 0:
            return 0.0
        
        # Obtener estudiantes de este paralelo
        estudiantes = self.estudiantes
        total_promedios = 0.0
        total_estudiantes = estudiantes.count()
        
        if total_estudiantes == 0:
            return 0.0
        
        # Sumar el promedio de cada estudiante
        for estudiante in estudiantes:
            total_promedios += estudiante.promedio_calificaciones()
        
        # Dividir por el total de estudiantes
        return round(total_promedios / total_estudiantes, 2)

    @classmethod
    def obtener_por_materia_paralelo(cls, materia_id, paralelo_nombre):
        """Busca un paralelo específico de una materia"""   
        try:
            return cls.get(
                (cls.id_materia == materia_id) &
                (cls.paralelo == paralelo_nombre.upper())
            )
        except cls.DoesNotExist:
            return None
