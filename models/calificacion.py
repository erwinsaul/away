"""
Modelo  para el registro de calificaciones.
Conecta estudiantes con el laboratorio y almacena las notas.
"""

from peewee import *
from .database import BaseModel
from .estudiante import Estudiante
from .laboratorio import Laboratorio
from datetime import datetime

class Calificacion(BaseModel):
    """
    Representa una calificación específica de un  estudiante de un laboratorio.

    Esta es la tabla  central donde se almacenara todas las notas.
    Cada registro conecta cun estudiante con un labortaorio específico.
    """
    id_laboratorio = ForeignKeyField(Laboratorio, backref='calificaciones')
    id_estudiante = ForeignKeyField(Estudiante, backref='calificaciones')
    calificacion = FloatField(null=True) # Puede estar vacía al inicio
    observaciones = TextField(null=True) # Comentarios opcionales
    fecha_registro = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'calificaciones'
        # Un estudiantes no puede tener dos notas del mismo laboratorio
        indexes = (
            (('id_estudiante', 'id_laboratorio'), True),    
        )
    
    def __str__(self):
        nota_str = f"{self.calificacion: 0.1f}" if self.calificacion else "Sin nota"
        return f"{self.id_estudiante.nombre} - {self.id_laboratorio.titulo}: {nota_str}"
    
    def porcentaje_nota(self):
        """Calcula el porcentaje respecto al puntaje máximo"""
        if not self.calificacion:
            return 0.0
        
        puntaje_max = self.id_laboratorio.puntaje_maximo
        return round(self.calificacion / puntaje_max * 100, 2)
    
    def estado_aprobacion(self):
        """Retorna el estado de la aprobación"""
        if not self.calificacion:
            return "Sin Nota"
        
        porcentaje = self.porcentaje_nota()
        return "Aprobado" if porcentaje >= 51 else "Reprobado"

    def es_aprobado(self):
        """Retorna True si la calificación es aprobatoria"""
        return self.estado_aprobacion() == "Aprobado"
    
    @classmethod
    def obtener_por_paralelo(cls, paralelo):
        """Obtiene todas las calificaciones de un paralelo"""

        return (cls.select()
                .join(Estudiante)
                .where(Estudiante.id_paralelo == paralelo)
                .order_by(Estudiante.nombre)
                )

    @classmethod
    def estadisticas_paralelo(cls, paralelo):
        """Calcula estadisticas generales de un paralelo"""
        calificaciones = cls.obtener_por_paralelo(paralelo)
        calificaciones_con_nota = calificaciones.where(cls.calificacion.is_null(False))

        if not calificaciones_con_nota.exists():
            return {
                'total_calificaciones': 0,
                'promedio_general': 0.0,
                'aprobados': 0,
                'reprobados': 0,
                'sin_calificar': calificaciones.where(cls.calificacion.is_null(True)).count()
            }

        notas = [cal.calificacion for cal in calificaciones_con_nota]
        aprobados = len([nota for nota in notas if nota >= 51])

        return{
            'total_calificaciones': len(notas),
            'promedio_general': round(sum(notas) / len(notas), 2),
            'aprobados': aprobados,
            'reprobados': len(notas) - aprobados,
            'sin_calificar': calificaciones.where(cls.calificacion.is_null(True)).count()
        }

    @classmethod
    def matriz_calificaciones_paralelo(cls, paralelo):
        """Genera una matriz de calificaciones para reportes."""
        from .laboratorio import Laboratorio
        
        #Obtener estudiantes del paralelo
        estudiantes =  paralelo.estudiantes.order_by(Estudiante.nombre)

        # Obtener laboratorio de la materia
        laboratorios = (Laboratorio.select()
                        .where(Laboratorio.id_materia == paralelo.id_materia)
                        .order_by(Laboratorio.numero))
        
        matriz = []

        for estudiante in estudiantes:
            fila = {
                'estudiante': estudiante.nombre,
                'ci': estudiante.ci,
                'grupo': estudiante.grupo,
                'calificaciones': {},
                'promedio': 0.0
            }

            total_notas = 0
            count_notas = 0

            for lab in laboratorios:
                try:
                    cal = cls.get(
                        (cls.id_estudiante == estudiante) &
                        (cls.id_laboratorio == lab)
                    )
                    nota = cal.calificacion if cal.calificacion else 0
                    fila['calificaciones'][f"lab_{lab.numero}"] = nota

                    if cal.calificacion:
                        total_notas = total_notas + cal.calificacion
                        count_notas = count_notas + 1
                
                except cls.DoesNotExist:
                    fila['calificaciones'][f"lab_{lab.numero}"] = None
            
            fila['promedio'] = round(total_notas / count_notas, 2) if count_notas > 0 else 0.0
            matriz.append(fila)
        
        return matriz     
