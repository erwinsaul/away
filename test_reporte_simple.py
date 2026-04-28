"""
Script de prueba para el reporte simple PDF
"""
from models.database import inicializar_bd
from models.paralelo import Paralelo
from utils.pdf_exporter import PDFExporter

# Inicializar base de datos
inicializar_bd()

# Obtener el primer paralelo
paralelos = list(Paralelo.select().limit(1))

if paralelos:
    paralelo = paralelos[0]
    print(f"Generando reporte simple para: {paralelo.id_materia.sigla} - Paralelo {paralelo.paralelo}")
    print(f"Docente: {paralelo.docente_teoria}")

    # Generar reporte simple
    archivo = PDFExporter.generar_reporte_simple(paralelo.id)

    if archivo:
        print(f"\n✓ Reporte simple generado exitosamente!")
        print(f"  Ubicación: {archivo}")
    else:
        print("\n✗ Error al generar el reporte")
else:
    print("No hay paralelos en la base de datos")
