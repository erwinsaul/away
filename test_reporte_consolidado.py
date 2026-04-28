#!/usr/bin/env python3
"""
Script de prueba para generar reporte consolidado de todas las materias y paralelos
"""

import sys
from utils.pdf_exporter import PDFExporter

def main():
    """Prueba la generación del reporte consolidado"""
    print("=" * 60)
    print("GENERANDO REPORTE CONSOLIDADO")
    print("=" * 60)

    # Generar reporte consolidado
    ruta = PDFExporter.generar_reporte_consolidado()

    if ruta:
        print(f"\n✓ Reporte consolidado generado exitosamente")
        print(f"Ubicación: {ruta}")
    else:
        print("\n✗ Error al generar el reporte consolidado")
        sys.exit(1)

if __name__ == "__main__":
    main()
