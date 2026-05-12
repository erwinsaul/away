"""
Cada materia tiene su sigla, nombre y puede tener múltiples paralelos
"""

from peewee import *
from .database import BaseModel

class Materia(BaseModel):
    """
    Representa una materia específica

    Ejemplos:
    - materia: "Metodología de la Programación I", sigla: "SIS-1110"
    - materia: "Base de Datos", sigla: "SIS-2330"
    """

    materia = CharField(max_length=100)
    sigla = CharField(max_length=20, unique=True) # SIS-1110, SIS-2330, etc.
    
    class Meta:
        table_name = 'materias'
    
    def __str__(self):
        return f"{self.sigla} - {self.materia}"
    
    def contar_paralelos(self):
        """Cuenta cuántos paralelos tiene la materia"""
        return self.paralelos.count()

    def contar_laboratorios(self):
        """Cuenta cuántos laboratorios tiene la materia"""
        return self.laboratorios.count()

    def contar_estudiantes_total(self):
        """Cuenta el total de estudiantes en todos los paralelos"""
        total = 0
        for paralelo in self.paralelos:
            total += paralelo.estudiantes.count()
        return total

    @classmethod
    def obtener_por_sigla(cls, sigla):
        """Obtiene una materia por su sigla"""
        try:
            return cls.get(cls.sigla == sigla.upper())
        except cls.DoesNotExist:
            return None
    
    def estadisticas_completas(self):
        """Retorna estadísticas completas de la materia"""
        return {
            "sigla": self.sigla,
            "materia": self.materia,
            "paralelos": self.contar_paralelos(),
            "laboratorios": self.contar_laboratorios(),
            "estudiantes": self.contar_estudiantes_total(),
        }
     