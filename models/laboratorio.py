"""
Modelo para los laboratorios de cada materia.
Cada materia define sus propios laboratorios con numeración independiente.
"""
from peewee import *
from .database import BaseModel
from .materia import Materia

class Laboratorio(BaseModel):
    """
    Representa un laboratorio específico de una materia.
    Cada materia define sus propios laboratorios:
    - SIS1110: Lab 1(Variables), Lab 2(Condicionales), etc
    - SIS2430: Lab 1(SQL Básico), Lab 2(SQL Avanzado), etc
    """
    numero = IntegerField()
    titulo = CharField(max_length=200)
    id_materia = ForeignKeyField(Materia, backref='laboratorios')
    descripcion = TextField(null=True)
    puntaje_maximo = FloatField(default=100.0)

    class Meta:
        table_name = 'laboratorios'
        #el número es unico dentro de cada materia
        indexes = (
            (('id_materia', 'numero'), True),
        )
        order_by = ('numero',)
    
    def __str__(self):
        return f"{self.numero}: {self.titulo} ({self.id_materia.sigla})"

    def contar_calificaciones(self):
        """Cuenta calificaciones resgistradas para este laboratorio"""
        return self.calificaciones.count()
    
    def promedio_calificaciones(self):
        """Calcula el promedio de todas las calificaciones"""
        from .calificacion import Calificacion
        from .estudiante import Estudiante
        from .paralelo import Paralelo

        # Obtener total de estudiantes en la materia de este laboratorio
        materia = self.id_materia
        total_estudiantes = Estudiante.select().join(
            Paralelo
        ).where(
            Paralelo.id_materia == materia
        ).count()
        
        if total_estudiantes == 0:
            return 0.0
        
        # Obtener solo las calificaciones que tienen valor
        calificaciones = self.calificaciones.where(Calificacion.calificacion.is_null(False))
        total_calificaciones = sum(cal.calificacion for cal in calificaciones)
        
        # Dividir por el total de estudiantes posibles, no solo los que tienen nota
        return round(total_calificaciones / total_estudiantes, 2)
    
    def estadisticas_detalladas(self):
        """Retorna estadísticas completas del laboratorio"""
        from .calificacion import Calificacion
        from .estudiante import Estudiante
        from .paralelo import Paralelo

        # Obtener total de estudiantes en la materia de este laboratorio
        materia = self.id_materia
        total_estudiantes = Estudiante.select().join(
            Paralelo
        ).where(
            Paralelo.id_materia == materia
        ).count()
        
        if total_estudiantes == 0:
            return {
                "total_calificaciones": 0,
                "promedio": 0.0,
                "nota_maxima": self.puntaje_maximo,
                "nota_minima": 0.0,
                "aprobados": 0,
                "reprobados": 0
            }
        
        # Obtener calificaciones con valor
        calificaciones_con_valor = self.calificaciones.where(Calificacion.calificacion.is_null(False))
        notas = [cal.calificacion for cal in calificaciones_con_valor]
        total_calificaciones = sum(notas)
        
        # Calcular promedio considerando todos los estudiantes posibles
        promedio = total_calificaciones / total_estudiantes
        aprobados = len([nota for nota in notas if nota >= 51])
        
        return{
            "total_calificaciones": len(notas),
            "promedio": promedio,
            "nota_maxima": max(notas) if notas else 0.0,
            "nota_minima": min(notas) if notas else 0.0,
            "aprobados": aprobados,
            "reprobados": len(notas) - aprobados
        }

    @classmethod
    def obtener_por_materia(cls, materia, ordenar_por_numero=True):
        """Obtiene todos los laboratorios de una materia"""
        query = cls.select().where(cls.id_materia == materia)
        if ordenar_por_numero:
            query = query.order_by(cls.numero)
        
        return query
    
    @classmethod
    def obtener_siguiente_numero(cls, materia):
        """ Obtiene el siguiente numero de laboratorio para una materia """
        ultimo = (cls.select()
            .where(cls.id_materia == materia)
            .order_by(cls.numero.desc())
            .first())
        
        return (ultimo.numero + 1) if ultimo else 1
    

    