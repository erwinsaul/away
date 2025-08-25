from peewee import *
import os
from datetime import datetime

# Definir donde estará nuestra base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'laboratorios.db')

# Crear el directorio si no existe
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Configurar SQLite (base de dats en archivo)
database = SqliteDatabase(DB_PATH)

class BaseModel(Model):
    """
    Clase para todos nuestros modelos.

    Incluye campos de auditoría que nos permiten saber  cuándo
    se creó y modifico cada registro. Esto es muy útil para 
    hacer seguimiento de cambios.
    """

    fecha_creacion = DateTimeField(default=datetime.now)
    fecha_modificacion = DateTimeField(default=datetime.now)

    class Meta:
        database = database

    def save(self, *args, **kwargs):
        """
        Sobreescribimos save para actualizar automáticamente
        la fecha de modificación cada vez que guardamos
        """
        self.fecha_modificacion = datetime.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Representación string básica"""
        return f"{self.__class__.__name__}({self.id})"

def inicializar_bd():
    """
    Inicializar la base de datos creando todas las tablas.
    Es seguro llamar esto múltiples veces.
    """
    # Importar todos los modelos
    from .materia import Materia
    from .paralelo import Paralelo
    from .estudiante import Estudiante
    from .laboratorio import Laboratorio
    from .calificacion import Calificacion

    database.connect()

    # Crear todas las tablas
    database.create_tables([
        Materia, Paralelo, Estudiante, Laboratorio, Calificacion
    ], safe=True)

    print("Base de datos inicializada correctamente")

def cerrar_bd():
    """Cierra la conexión a la base de datos""" 
    if not database.is_closed():
        database.close()
        print("Conexión cerrada")