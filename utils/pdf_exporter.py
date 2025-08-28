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
    
