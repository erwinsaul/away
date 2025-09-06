"""
Sistema de exportación a PDF usando ReportLab.
Generar reportes con formato
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from datetime import datetime
import os
from models.materia import Materia
from models.paralelo import Paralelo
from models.estudiante import Estudiante
from models.calificacion import Calificacion
from models.laboratorio import Laboratorio

class PDFExporter:
    """
    Generador de reportes PDF con formato
    """

    @staticmethod
    def generar_reporte_paralelo(paralelo_id, ruta_archivo=None):
        """
        Genera un reporte completo de un paralelo

        Args:
            paralelo_id (int): ID del paralelo
            ruta_archivo (str): Ruta donde guardar el archivo (Opcional)
        
        Returns:
            str: Ruta del archivo generado o None si hay error
        """
        try:
            # Obtener datos
            paralelo = Paralelo.get_by_id(paralelo_id)
            materia = paralelo.id_materia

            # Genera nombre de archivo si no se proporciona
            if not ruta_archivo:
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                nombre_archivo = f"reporte_{materia.sigla}_{paralelo.paralelo}_{timestamp}.pdf"
                ruta_archivo = os.path.join("exports", "pdfs", nombre_archivo)
            
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)

            # Crear Documento
            doc = SimpleDocTemplate(
                ruta_archivo,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )

            # Construir contenido
            contenido = []
            styles = getSampleStyleSheet()

            # Agregar elementos del reporte
            PDFExporter._agregar_encabezado(contenido, styles)
            PDFExporter._agregar_info_materia(contenido, materia, paralelo, styles)
            PDFExporter._agregar_lista_estudiantes(contenido, paralelo, styles)
            PDFExporter._agregar_matriz_calificaciones(contenido, paralelo, styles)
            PDFExporter._agregar_estadisticas(contenido, paralelo, styles)
            PDFExporter._agregar_pie_documento(contenido, styles)

            # Generar PDF
            doc.build(contenido)

            print(f"[OK] Reporte PDF generado: {ruta_archivo}")
            return ruta_archivo
        except Exception as e:
            print(f"[ERROR] Error al generar PDF: {e}")
            return None
    
    @staticmethod
    def _agregar_encabezado(contenido, styles):
        """
        Agrega el encabezado del reporte.

        Args:
            contenido (list): Contenido del documento
            styles (Styles): Estilos del documento
        """

        # Encabezado
        titulo_principal = Paragraph(
            "<b>UNIVERSIDAD TÉCNICA DE ORURO</b><br/>"
            "Facultad Nacional de Ingeniería<br/>"
            "Carrera de Ingeniería de Sistemas e Ingeniería Informática",
            styles["Title"]
        )

        contenido.append(titulo_principal)
        contenido.append(Spacer(1, 20))

        titulo_reporte = Paragraph(
            "<b>CALIFICACIONES DE LABORATORIO</b>",
            styles["Title"]
        )

        contenido.append(titulo_reporte)
        contenido.append(Spacer(1, 20))

    @staticmethod
    def _agregar_info_materia(contenido, materia, paralelo, styles):
        """
        Agrega información de la materia y paralelo.
        """
        fecha_actual = datetime.now().strftime("%d de %m de %Y")
        info_data = [
            ['Materia: ', materia.materia],
            ['Sigla: ', materia.sigla],
            ['Paralelo: ', paralelo.paralelo],
            ['Docente: ', paralelo.docente_teoria],
            ['Fecha: ', fecha_actual]
        ]

        tabla_info = Table(info_data, colWidths=[4*cm, 8*cm])
        tabla_info.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME', (1,0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1, -1), 11),
            ('BOTTOMPADDING', (0,0), (-1, -1), 8),
        ]))

        contenido.append(tabla_info)
        contenido.append(Spacer(1, 25))
    
    @staticmethod
    def _agregar_lista_estudiantes(contenido, paralelo, styles):
        """
        Agrega tabla de estudiantes
        """
        titulo_seccion = Paragraph("<b>LISTA DE ESTUDIANTES</b>", styles["Heading2"])
        contenido.append(titulo_seccion)
        contenido.append(Spacer(1, 10))

        estudiantes = list(paralelo.estudiantes.order_by(Estudiante.nombre))

        if not estudiantes:
            no_estudiantes = Paragraph(
                "No hay estudiantes registrados",
                styles["Normal"]
            )
            contenido.append(no_estudiantes)
            contenido.append(Spacer(1, 20))
            return
        
        # Crea tabla
        datos_tabla = [['N', 'C.I.', 'Nombre Completo', 'Promedio']]

        for i, estudiante in enumerate(estudiantes, 1):
            promedio = estudiante.promedio_calificaciones()
            datos_tabla.append([
                str(i),
                estudiante.ci,
                estudiante.nombre,
                f"{promedio:.2f}"
            ])
        
        tabla_estudiantes = Table(datos_tabla, colWidths=[1*cm, 2.5*cm, 8*cm, 3*cm])
        tabla_estudiantes.setStyle(TableStyle([
            #Encabezado
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),

            #Datos

            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 9),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),

            # Nombres alineados a la izquierda
            ('ALIGN', (2,1), (2,-1), 'LEFT'),
        ]))

        contenido.append(tabla_estudiantes)
        contenido.append(Spacer(1, 25))

    @staticmethod
    def _agregar_matriz_calificaciones(contenido, paralelo, styles):
        """ Agrega Matriz de Calificaciones """

        titulo_seccion = Paragraph("<b>CALIFICACIONES</b>", styles["Heading2"])
        contenido.append(titulo_seccion)
        contenido.append(Spacer(1, 10))

        # Obtener matriz de calificaciones
        matriz = Calificacion.matriz_calificaciones_paralelo(paralelo)

        if not matriz:
            sin_calificaciones = Paragraph("No hay calificaciones registradas", styles["Normal"])
            contenido.append(sin_calificaciones)
            return
        
        # Obtener laboratorios
        laboratorios = list(Laboratorio.obtener_por_materia(paralelo.id_materia))

        # Construir tabla
        encabezados = ['Estudiante'] + [f"L{lab.numero}" for lab in laboratorios] + ['Prom.']
        datos_tabla = [encabezados]

        for fila in matriz:
            datos_fila = [fila['estudiante'][:25] ] # Truncar nombres largos

            # Agregar calificaciones
            for lab in laboratorios:
                cal = fila['calificaciones'].get(f'lab_{lab.numero}')
                if cal is not None:
                    datos_fila.append(f"{cal:.2f}")
                else:
                    datos_fila.append("--")
            
            # Agregar promedio
            datos_fila.append(f"{fila['promedio']:.2f}")
            datos_tabla.append(datos_fila)
        
        # Calcular anchos dinámicamente

        num_labs = len(laboratorios)
        ancho_nombre = 4*cm
        ancho_lab = 0.8*cm
        ancho_promedio = 1.2*cm

        anchos = [ancho_nombre] + [ancho_lab] * num_labs + [ancho_promedio]

        tabla_calificaciones = Table(datos_tabla, colWidths=anchos)
        tabla_calificaciones.setStyle(TableStyle([
            # Encabezados
            ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 8),

            # Datos
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),

            # Nombres a la izquierda
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),

            # Resaltr promedio
            ('BACKGROUND', (-1, 1), (-1, -1), colors.lightgrey),
        ]))

        contenido.append(tabla_calificaciones)
        contenido.append(Spacer(1, 25))
    
    @staticmethod
    def _agregar_estadisticas(contenido, paralelo, styles):
        """ Agrega estadísticas generales """
        titulo_seccion = Paragraph("<b>ESTADÍSTICAS GENERALES</b>", styles["Heading2"])
        contenido.append(titulo_seccion)
        contenido.append(Spacer(1, 10))

        stats = Calificacion.estadisticas_paralelo(paralelo)

        stats_data = [
            ['Total de calificaciones', str(stats.get('total_calificaciones', 0))],
            ['Promedio General', f"{stats.get('promedio_general', 0):.2f}"],
            ['Aprobados', str(stats.get('aprobados', 0))],
            ['Reprobados', str(stats.get('reprobados', 0))],
            ['Sin Calificar', str(stats.get('sin_calificar', 0))],
        ]
        tabla_stats = Table(stats_data, colWidths=[8*cm, 4*cm])

        tabla_stats.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ]))

        contenido.append(tabla_stats)
        contenido.append(Spacer(1, 30))
    
    @staticmethod
    def _agregar_pie_documento(contenido, styles):
        """ Agrega pie del documento """
        fecha_generacion = datetime.now().strftime("%d de %m de %Y a las %H:%M")
        pie_texto = f"""
            <i>Reporte generado por <b>Away - Sistema de Gestión de Laboratorios</b>
            Universidad Técnica de Oruro - Carrera de Ingeniería de Sistemas e Ingeniería Informática<br/>
            Fecha: {fecha_generacion}</i>
        """
        pie = Paragraph(pie_texto, styles["Normal"])
        contenido.append(pie)


        
        
    





    
