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
        calificaciones = self.calificaciones.where(Calificacion.calificacion.is_null(False))

        if not calificaciones.exists():
            return 0.0
        
        total = sum(cal.calificacion for cal in calificaciones)
        return round(total / calificaciones.count(), 2)
    
    def estadisticas_detalladas(self):
        """Retorna estadísticas completas del laboratorio"""
        from .calificacion import Calificacion

        calificacion = self.calificaciones.where(Calificacion.calificacion.is_null(False))

        if not calificacion.exists():
            return {
                'total_calificaciones': 0,
                'promedio': 0.0,
                'nota_maxima': self.puntaje_maximo,
                'nota_minima': 0.0,
                'aprobados': 0,
                'reprobados': 0
            }
        
        notas = [cal.calificacion for cal in calificacion]
        promedio = sum(notas) / len(notas)
        aprobados = len([nota for nota in notas if nota >= 51])

        return{
            'total_calificaciones': len(notas),
            'promedio': promedio,
            'nota_maxima': max(notas),
            'nota_minima': min(notas),
            'aprobados': aprobados,
            'reprobados': len(notas) - aprobados
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
    

    