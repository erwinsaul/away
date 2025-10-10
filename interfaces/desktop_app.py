"""
Aplicación desktop completa para el sistema de gestión de laboratorios.
Utiliza Tkinter para crear una interfaz gráfica completa con todos los CRUDs.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
from datetime import datetime

from models.database import inicializar_bd, cerrar_bd
from managers.materia_manager import MateriaManager
from managers.paralelo_manager import ParaleloManager
from managers.estudiante_manager import EstudianteManager
from managers.laboratorio_manager import LaboratorioManager
from managers.calificacion_manager import CalificacionManager
from utils.pdf_exporter import PDFExporter

class MainDesktopApp:
    """Aplicación principal desktop del sistema de laboratorios"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Gestión de Laboratorios - Desktop")
        self.root.geometry("1200x800")
        self.root.state('zoomed')  # Maximizado en Windows
        
        # Variables de control
        self.current_module = None
        
        # Configurar cierre
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        
        # Inicializar base de datos
        inicializar_bd()
        
        # Crear interfaz
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz principal"""
        
        # Crear menú principal
        self.crear_menu()
        
        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Header
        self.crear_header()
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Crear pestañas
        self.crear_pestaña_dashboard()
        self.crear_pestaña_materias()
        self.crear_pestaña_paralelos()
        self.crear_pestaña_estudiantes()
        self.crear_pestaña_laboratorios()
        self.crear_pestaña_calificaciones()
        self.crear_pestaña_reportes()
        
        # Barra de estado
        self.crear_barra_estado()
    
    def crear_menu(self):
        """Crea el menú principal"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        archivo_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)
        archivo_menu.add_command(label="Nuevo", command=self.nuevo_elemento)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Exportar PDF", command=self.exportar_pdf)
        archivo_menu.add_command(label="Exportar Excel", command=self.exportar_excel)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=self.cerrar_aplicacion)
        
        # Menú Gestión
        gestion_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Gestión", menu=gestion_menu)
        gestion_menu.add_command(label="Materias", command=lambda: self.notebook.select(1))
        gestion_menu.add_command(label="Paralelos", command=lambda: self.notebook.select(2))
        gestion_menu.add_command(label="Estudiantes", command=lambda: self.notebook.select(3))
        gestion_menu.add_command(label="Laboratorios", command=lambda: self.notebook.select(4))
        gestion_menu.add_command(label="Calificaciones", command=lambda: self.notebook.select(5))
        
        # Menú Reportes
        reportes_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reportes", menu=reportes_menu)
        reportes_menu.add_command(label="Estadísticas", command=self.mostrar_estadisticas)
        reportes_menu.add_command(label="Matriz de Calificaciones", command=self.mostrar_matriz_calificaciones)
        reportes_menu.add_separator()
        reportes_menu.add_command(label="Generar PDF", command=self.generar_pdf_directo)
        
        # Menú Ayuda
        ayuda_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=ayuda_menu)
        ayuda_menu.add_command(label="Acerca de", command=self.mostrar_acerca_de)
    
    def crear_header(self):
        """Crea el encabezado de la aplicación"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Título principal
        titulo = ttk.Label(
            header_frame,
            text="Sistema de Gestión de Laboratorios",
            font=('Arial', 18, 'bold'),
            foreground='#2E86AB'
        )
        titulo.pack()
        
        # Subtítulo
        subtitulo = ttk.Label(
            header_frame,
            text="Universidad Técnica de Oruro - SIS 2420 - Actualización Tecnológica",
            font=('Arial', 12),
            foreground='#A23B72'
        )
        subtitulo.pack()
        
        # Separador
        ttk.Separator(header_frame, orient='horizontal').pack(fill=tk.X, pady=10)
    
    def crear_pestaña_dashboard(self):
        """Crea la pestaña del dashboard"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Dashboard")
        
        # Título
        titulo = ttk.Label(frame, text="Resumen General del Sistema", font=('Arial', 16, 'bold'))
        titulo.pack(pady=(10, 20))
        
        # Frame para métricas
        self.metrics_frame = ttk.LabelFrame(frame, text="Estadísticas del Sistema", padding=20)
        self.metrics_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Botones de acceso rápido
        actions_frame = ttk.LabelFrame(frame, text="Acciones Rápidas", padding=10)
        actions_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Grid de botones
        botones = [
            ("Nueva Materia", self.nueva_materia_rapida),
            ("Nuevo Estudiante", self.nuevo_estudiante_rapido),
            ("Nueva Calificación", self.nueva_calificacion_rapida),
            ("Generar Reporte", self.generar_reporte_rapido)
        ]
        
        for i, (texto, comando) in enumerate(botones):
            btn = ttk.Button(actions_frame, text=texto, command=comando)
            btn.grid(row=i//2, column=i%2, padx=10, pady=5, sticky=(tk.W, tk.E))
        
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)
        
        # Cargar estadísticas
        self.actualizar_dashboard()
    
    def crear_pestaña_materias(self):
        """Crea la pestaña de gestión de materias"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Materias")
        
        # Barra de herramientas
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(toolbar, text="Nueva Materia", command=self.nueva_materia).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Editar", command=self.editar_materia).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Eliminar", command=self.eliminar_materia).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Actualizar", command=self.cargar_materias).pack(side=tk.LEFT, padx=5)
        
        # Frame para búsqueda
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=5)
        self.search_materias_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_materias_var)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<KeyRelease>', self.buscar_materias)
        
        # Tabla
        columns = ('ID', 'Sigla', 'Materia', 'Docente', 'Paralelos', 'Estudiantes', 'Laboratorios')
        self.tree_materias = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.tree_materias.heading('ID', text='ID')
        self.tree_materias.heading('Sigla', text='Sigla')
        self.tree_materias.heading('Materia', text='Materia')
        self.tree_materias.heading('Docente', text='Docente')
        self.tree_materias.heading('Paralelos', text='Paralelos')
        self.tree_materias.heading('Estudiantes', text='Estudiantes')
        self.tree_materias.heading('Laboratorios', text='Laboratorios')
        
        self.tree_materias.column('ID', width=50)
        self.tree_materias.column('Sigla', width=80)
        self.tree_materias.column('Materia', width=200)
        self.tree_materias.column('Docente', width=150)
        self.tree_materias.column('Paralelos', width=80)
        self.tree_materias.column('Estudiantes', width=100)
        self.tree_materias.column('Laboratorios', width=100)
        
        # Scrollbars
        scrollbar_v = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree_materias.yview)
        self.tree_materias.configure(yscrollcommand=scrollbar_v.set)
        
        # Empaquetar tabla y scrollbar
        self.tree_materias.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
        
        # Doble click para editar
        self.tree_materias.bind('<Double-1>', lambda e: self.editar_materia())
        
        # Cargar datos
        self.cargar_materias()
    
    def crear_pestaña_paralelos(self):
        """Crea la pestaña de gestión de paralelos"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Paralelos")
        
        # Frame superior para selección de materia
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(top_frame, text="Materia:").pack(side=tk.LEFT, padx=5)
        self.combo_paralelos_materia = ttk.Combobox(top_frame, state="readonly", width=50)
        self.combo_paralelos_materia.pack(side=tk.LEFT, padx=5)
        self.combo_paralelos_materia.bind('<<ComboboxSelected>>', self.on_materia_paralelos_changed)
        
        # Barra de herramientas
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(toolbar, text="Nuevo Paralelo", command=self.nuevo_paralelo).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Editar", command=self.editar_paralelo).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Eliminar", command=self.eliminar_paralelo).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Actualizar", command=self.cargar_paralelos).pack(side=tk.LEFT, padx=5)
        
        # Tabla
        columns = ('ID', 'Paralelo', 'Estudiantes', 'Grupos', 'Promedio')
        self.tree_paralelos = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree_paralelos.heading(col, text=col)
            self.tree_paralelos.column(col, width=100)
        
        self.tree_paralelos.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree_paralelos.bind('<Double-1>', lambda e: self.editar_paralelo())
        
        # Cargar materias en combo
        self.cargar_combo_materias_paralelos()
    
    def crear_pestaña_estudiantes(self):
        """Crea la pestaña de gestión de estudiantes"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Estudiantes")
        
        # Frame superior para selección de paralelo
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(top_frame, text="Paralelo:").pack(side=tk.LEFT, padx=5)
        self.combo_estudiantes_paralelo = ttk.Combobox(top_frame, state="readonly", width=50)
        self.combo_estudiantes_paralelo.pack(side=tk.LEFT, padx=5)
        self.combo_estudiantes_paralelo.bind('<<ComboboxSelected>>', self.on_paralelo_estudiantes_changed)
        
        # Barra de herramientas
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(toolbar, text="Nuevo Estudiante", command=self.nuevo_estudiante).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Editar", command=self.editar_estudiante).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Eliminar", command=self.eliminar_estudiante).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Organizar Grupos", command=self.organizar_grupos).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Actualizar", command=self.cargar_estudiantes).pack(side=tk.LEFT, padx=5)
        
        # Frame para búsqueda
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(search_frame, text="Buscar por CI:").pack(side=tk.LEFT, padx=5)
        self.search_estudiantes_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_estudiantes_var)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<KeyRelease>', self.buscar_estudiantes)
        
        # Tabla
        columns = ('ID', 'CI', 'Nombre', 'Grupo', 'Calificaciones', 'Promedio')
        self.tree_estudiantes = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree_estudiantes.heading(col, text=col)
        
        self.tree_estudiantes.column('ID', width=50)
        self.tree_estudiantes.column('CI', width=100)
        self.tree_estudiantes.column('Nombre', width=200)
        self.tree_estudiantes.column('Grupo', width=100)
        self.tree_estudiantes.column('Calificaciones', width=100)
        self.tree_estudiantes.column('Promedio', width=80)
        
        self.tree_estudiantes.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree_estudiantes.bind('<Double-1>', lambda e: self.editar_estudiante())
        
        # Cargar paralelos en combo
        self.cargar_combo_paralelos_estudiantes()
    
    def crear_pestaña_laboratorios(self):
        """Crea la pestaña de gestión de laboratorios"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Laboratorios")
        
        # Frame superior para selección de materia
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(top_frame, text="Materia:").pack(side=tk.LEFT, padx=5)
        self.combo_laboratorios_materia = ttk.Combobox(top_frame, state="readonly", width=50)
        self.combo_laboratorios_materia.pack(side=tk.LEFT, padx=5)
        self.combo_laboratorios_materia.bind('<<ComboboxSelected>>', self.on_materia_laboratorios_changed)
        
        # Barra de herramientas
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(toolbar, text="Nuevo Laboratorio", command=self.nuevo_laboratorio).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Editar", command=self.editar_laboratorio).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Eliminar", command=self.eliminar_laboratorio).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Actualizar", command=self.cargar_laboratorios).pack(side=tk.LEFT, padx=5)
        
        # Tabla
        columns = ('ID', 'Número', 'Título', 'Descripción', 'Puntaje', 'Calificaciones')
        self.tree_laboratorios = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree_laboratorios.heading(col, text=col)
        
        self.tree_laboratorios.column('ID', width=50)
        self.tree_laboratorios.column('Número', width=80)
        self.tree_laboratorios.column('Título', width=200)
        self.tree_laboratorios.column('Descripción', width=150)
        self.tree_laboratorios.column('Puntaje', width=80)
        self.tree_laboratorios.column('Calificaciones', width=100)
        
        self.tree_laboratorios.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree_laboratorios.bind('<Double-1>', lambda e: self.editar_laboratorio())
        
        # Cargar materias en combo
        self.cargar_combo_materias_laboratorios()
    
    def crear_pestaña_calificaciones(self):
        """Crea la pestaña de gestión de calificaciones"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Calificaciones")
        
        # Frame superior para selección de laboratorio
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(top_frame, text="Laboratorio:").pack(side=tk.LEFT, padx=5)
        self.combo_calificaciones_laboratorio = ttk.Combobox(top_frame, state="readonly", width=60)
        self.combo_calificaciones_laboratorio.pack(side=tk.LEFT, padx=5)
        self.combo_calificaciones_laboratorio.bind('<<ComboboxSelected>>', self.on_laboratorio_calificaciones_changed)
        
        # Barra de herramientas
        toolbar = ttk.Frame(frame)
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(toolbar, text="Nueva Calificación", command=self.nueva_calificacion).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Editar", command=self.editar_calificacion).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Eliminar", command=self.eliminar_calificacion).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Calificar Lotes", command=self.calificar_lotes).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Actualizar", command=self.cargar_calificaciones).pack(side=tk.LEFT, padx=5)
        
        # Tabla
        columns = ('ID', 'CI', 'Estudiante', 'Calificación', 'Estado', 'Fecha', 'Observaciones')
        self.tree_calificaciones = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree_calificaciones.heading(col, text=col)
        
        self.tree_calificaciones.column('ID', width=50)
        self.tree_calificaciones.column('CI', width=100)
        self.tree_calificaciones.column('Estudiante', width=200)
        self.tree_calificaciones.column('Calificación', width=80)
        self.tree_calificaciones.column('Estado', width=80)
        self.tree_calificaciones.column('Fecha', width=100)
        self.tree_calificaciones.column('Observaciones', width=150)
        
        self.tree_calificaciones.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree_calificaciones.bind('<Double-1>', lambda e: self.editar_calificacion())
        
        # Cargar laboratorios en combo
        self.cargar_combo_laboratorios_calificaciones()
    
    def crear_pestaña_reportes(self):
        """Crea la pestaña de reportes"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Reportes")
        
        # Título
        titulo = ttk.Label(frame, text="Generación de Reportes", font=('Arial', 16, 'bold'))
        titulo.pack(pady=20)
        
        # Frame de opciones
        options_frame = ttk.LabelFrame(frame, text="Opciones de Reporte", padding=20)
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Selector de paralelo
        ttk.Label(options_frame, text="Seleccione paralelo:").pack(anchor=tk.W)
        
        self.combo_reportes_paralelo = ttk.Combobox(options_frame, state="readonly", width=60)
        self.combo_reportes_paralelo.pack(fill=tk.X, pady=5)
        
        # Botones de generación
        btn_frame = ttk.Frame(options_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Generar PDF", command=self.generar_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Generar Excel", command=self.generar_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Ver Matriz", command=self.ver_matriz).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Estadísticas", command=self.ver_estadisticas_paralelo).pack(side=tk.LEFT, padx=5)
        
        # Frame de información
        info_frame = ttk.LabelFrame(frame, text="Información del Sistema", padding=20)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.info_text = tk.Text(info_frame, height=10, state=tk.DISABLED)
        scrollbar_info = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=scrollbar_info.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_info.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cargar paralelos en combo
        self.cargar_combo_paralelos_reportes()
        
        # Cargar información inicial
        self.actualizar_info_reportes()
    
    def crear_barra_estado(self):
        """Crea la barra de estado"""
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
        # Separador
        ttk.Separator(self.status_frame, orient='horizontal').pack(fill=tk.X)
        
        # Label de estado
        self.status_label = ttk.Label(self.status_frame, text="Sistema listo")
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Información adicional
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        info_label = ttk.Label(
            self.status_frame,
            text=f"Sistema de Gestión de Laboratorios - UTO | {fecha_actual}",
            font=("Arial", 8)
        )
        info_label.pack(side=tk.RIGHT, padx=5, pady=2)
    
    # ==========================================
    # MÉTODOS DEL DASHBOARD
    # ==========================================
    
    def actualizar_dashboard(self):
        """Actualiza el dashboard con estadísticas actuales"""
        try:
            stats = MateriaManager.obtener_estadisticas_generales()
            
            # Limpiar frame de métricas
            for widget in self.metrics_frame.winfo_children():
                widget.destroy()
            
            # Crear métricas
            metrics = [
                ("Total Materias", stats['total_materias'], "#4CAF50"),
                ("Total Paralelos", stats['total_paralelos'], "#2196F3"),
                ("Total Estudiantes", stats['total_estudiantes'], "#FF9800"),
                ("Total Laboratorios", stats['total_laboratorios'], "#9C27B0")
            ]
            
            for i, (label, valor, color) in enumerate(metrics):
                frame_metric = tk.Frame(self.metrics_frame, bg=color, relief=tk.RAISED, bd=2)
                frame_metric.grid(row=i//2, column=i%2, padx=10, pady=10, sticky=(tk.W, tk.E))
                
                # Valor
                valor_label = tk.Label(
                    frame_metric,
                    text=str(valor),
                    font=("Arial", 20, "bold"),
                    fg="white",
                    bg=color
                )
                valor_label.pack(pady=(10, 0))
                
                # Etiqueta
                label_widget = tk.Label(
                    frame_metric,
                    text=label,
                    font=("Arial", 10),
                    fg="white",
                    bg=color
                )
                label_widget.pack(pady=(0, 10))
            
            self.metrics_frame.grid_columnconfigure(0, weight=1)
            self.metrics_frame.grid_columnconfigure(1, weight=1)
            
            self.actualizar_estado("Dashboard actualizado")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar dashboard: {e}")
    
    # ==========================================
    # MÉTODOS DE MATERIAS
    # ==========================================
    
    def cargar_materias(self):
        """Carga las materias en la tabla"""
        try:
            # Limpiar tabla
            for item in self.tree_materias.get_children():
                self.tree_materias.delete(item)
            
            # Cargar datos
            materias = MateriaManager.listar_materias()
            
            for materia in materias:
                self.tree_materias.insert('', tk.END, values=(
                    materia.id,
                    materia.sigla,
                    materia.materia,
                    materia.docente_teoria,
                    materia.contar_paralelos(),
                    materia.contar_estudiantes_total(),
                    materia.contar_laboratorios()
                ))
            
            self.actualizar_estado(f"{len(materias)} materias cargadas")
            self.actualizar_dashboard()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar materias: {e}")
    
    def nueva_materia(self):
        """Abre formulario para nueva materia"""
        self.abrir_formulario_materia()
    
    def nueva_materia_rapida(self):
        """Nueva materia desde dashboard"""
        self.notebook.select(1)  # Cambiar a pestaña materias
        self.nueva_materia()
    
    def editar_materia(self):
        """Edita la materia seleccionada"""
        selection = self.tree_materias.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una materia para editar")
            return
        
        item = selection[0]
        materia_id = self.tree_materias.item(item)['values'][0]
        materia = MateriaManager.obtener_materia(materia_id)
        
        if materia:
            self.abrir_formulario_materia(materia)
    
    def eliminar_materia(self):
        """Elimina la materia seleccionada"""
        selection = self.tree_materias.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una materia para eliminar")
            return
        
        item = selection[0]
        values = self.tree_materias.item(item)['values']
        materia_id = values[0]
        sigla = values[1]
        
        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar la materia {sigla}?\n\n"
            "Esta acción eliminará todos los datos relacionados."
        )
        
        if respuesta:
            resultado = MateriaManager.eliminar_materia(materia_id, forzar=True)
            
            if resultado['success']:
                messagebox.showinfo("Éxito", resultado['mensaje'])
                self.cargar_materias()
            else:
                messagebox.showerror("Error", resultado['mensaje'])
    
    def buscar_materias(self, event=None):
        """Busca materias por término"""
        termino = self.search_materias_var.get().strip()
        
        if not termino:
            self.cargar_materias()
            return
        
        try:
            # Limpiar tabla
            for item in self.tree_materias.get_children():
                self.tree_materias.delete(item)
            
            # Buscar materias
            materias = MateriaManager.buscar_materias(termino)
            
            for materia in materias:
                self.tree_materias.insert('', tk.END, values=(
                    materia.id,
                    materia.sigla,
                    materia.materia,
                    materia.docente_teoria,
                    materia.contar_paralelos(),
                    materia.contar_estudiantes_total(),
                    materia.contar_laboratorios()
                ))
            
            self.actualizar_estado(f"{len(materias)} materias encontradas")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en búsqueda: {e}")
    
    def abrir_formulario_materia(self, materia=None):
        """Abre el formulario de materia"""
        FormularioMateriaDialog(self.root, materia, self.callback_materia)
    
    def callback_materia(self, resultado):
        """Callback del formulario de materia"""
        if resultado:
            self.cargar_materias()
            self.cargar_combos_dependientes()
    
    # ==========================================
    # MÉTODOS DE PARALELOS
    # ==========================================
    
    def cargar_combo_materias_paralelos(self):
        """Carga materias en el combo de paralelos"""
        try:
            materias = MateriaManager.listar_materias()
            valores = ["Seleccione una materia..."]
            valores.extend([f"{m.sigla} - {m.materia}" for m in materias])
            
            self.combo_paralelos_materia['values'] = valores
            if len(valores) > 1:
                self.combo_paralelos_materia.set(valores[0])
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar materias: {e}")
    
    def on_materia_paralelos_changed(self, event=None):
        """Maneja el cambio de materia en paralelos"""
        seleccion = self.combo_paralelos_materia.get()
        if seleccion and seleccion != "Seleccione una materia...":
            # Obtener ID de materia del texto seleccionado
            sigla = seleccion.split(' - ')[0]
            materia = MateriaManager.obtener_por_sigla(sigla)
            if materia:
                self.cargar_paralelos(materia.id)
    
    def cargar_paralelos(self, materia_id=None):
        """Carga paralelos de una materia"""
        try:
            # Limpiar tabla
            for item in self.tree_paralelos.get_children():
                self.tree_paralelos.delete(item)
            
            if not materia_id:
                return
            
            paralelos = ParaleloManager.listar_paralelos_por_materia(materia_id)
            
            for paralelo in paralelos:
                self.tree_paralelos.insert('', tk.END, values=(
                    paralelo.id,
                    paralelo.paralelo,
                    paralelo.contar_estudiantes(),
                    paralelo.contar_grupos(),
                    f"{paralelo.promedio_general():.2f}"
                ))
            
            self.actualizar_estado(f"{len(paralelos)} paralelos cargados")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar paralelos: {e}")
    
    def nuevo_paralelo(self):
        """Abre formulario para nuevo paralelo"""
        seleccion = self.combo_paralelos_materia.get()
        if not seleccion or seleccion == "Seleccione una materia...":
            messagebox.showwarning("Advertencia", "Seleccione una materia primero")
            return
        
        sigla = seleccion.split(' - ')[0]
        materia = MateriaManager.obtener_por_sigla(sigla)
        if materia:
            self.abrir_formulario_paralelo(materia.id)
    
    def editar_paralelo(self):
        """Edita el paralelo seleccionado"""
        selection = self.tree_paralelos.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un paralelo para editar")
            return
        
        item = selection[0]
        paralelo_id = self.tree_paralelos.item(item)['values'][0]
        paralelo = ParaleloManager.obtener_paralelo(paralelo_id)
        
        if paralelo:
            self.abrir_formulario_paralelo(paralelo.id_materia.id, paralelo)
    
    def eliminar_paralelo(self):
        """Elimina el paralelo seleccionado"""
        selection = self.tree_paralelos.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un paralelo para eliminar")
            return
        
        item = selection[0]
        values = self.tree_paralelos.item(item)['values']
        paralelo_id = values[0]
        paralelo_nombre = values[1]
        
        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el paralelo {paralelo_nombre}?\n\n"
            "Esta acción eliminará todos los estudiantes y calificaciones relacionadas."
        )
        
        if respuesta:
            resultado = ParaleloManager.eliminar_paralelo(paralelo_id, forzar=True)
            
            if resultado['success']:
                messagebox.showinfo("Éxito", resultado['mensaje'])
                seleccion = self.combo_paralelos_materia.get()
                if seleccion and seleccion != "Seleccione una materia...":
                    sigla = seleccion.split(' - ')[0]
                    materia = MateriaManager.obtener_por_sigla(sigla)
                    if materia:
                        self.cargar_paralelos(materia.id)
            else:
                messagebox.showerror("Error", resultado['mensaje'])
    
    def abrir_formulario_paralelo(self, materia_id, paralelo=None):
        """Abre el formulario de paralelo"""
        FormularioParaleloDialog(self.root, materia_id, paralelo, self.callback_paralelo)
    
    def callback_paralelo(self, resultado):
        """Callback del formulario de paralelo"""
        if resultado:
            seleccion = self.combo_paralelos_materia.get()
            if seleccion and seleccion != "Seleccione una materia...":
                sigla = seleccion.split(' - ')[0]
                materia = MateriaManager.obtener_por_sigla(sigla)
                if materia:
                    self.cargar_paralelos(materia.id)
            self.cargar_combos_dependientes()
    
    # ==========================================
    # MÉTODOS DE ESTUDIANTES
    # ==========================================
    
    def cargar_combo_paralelos_estudiantes(self):
        """Carga paralelos en el combo de estudiantes"""
        try:
            materias = MateriaManager.listar_materias()
            valores = ["Seleccione un paralelo..."]
            
            for materia in materias:
                paralelos = ParaleloManager.listar_paralelos_por_materia(materia.id)
                for paralelo in paralelos:
                    valores.append(f"{materia.sigla} - Paralelo {paralelo.paralelo}")
            
            self.combo_estudiantes_paralelo['values'] = valores
            if len(valores) > 1:
                self.combo_estudiantes_paralelo.set(valores[0])
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar paralelos: {e}")
    
    def on_paralelo_estudiantes_changed(self, event=None):
        """Maneja el cambio de paralelo en estudiantes"""
        seleccion = self.combo_estudiantes_paralelo.get()
        if seleccion and seleccion != "Seleccione un paralelo...":
            # Obtener paralelo del texto seleccionado
            parts = seleccion.split(' - Paralelo ')
            if len(parts) == 2:
                sigla = parts[0]
                paralelo_nombre = parts[1]
                materia = MateriaManager.obtener_por_sigla(sigla)
                if materia:
                    paralelo = ParaleloManager.obtener_por_materia_paralelo(materia.id, paralelo_nombre)
                    if paralelo:
                        self.cargar_estudiantes(paralelo.id)
    
    def cargar_estudiantes(self, paralelo_id=None):
        """Carga estudiantes de un paralelo"""
        try:
            # Limpiar tabla
            for item in self.tree_estudiantes.get_children():
                self.tree_estudiantes.delete(item)
            
            if not paralelo_id:
                return
            
            estudiantes = EstudianteManager.listar_por_paralelo(paralelo_id)
            
            for estudiante in estudiantes:
                self.tree_estudiantes.insert('', tk.END, values=(
                    estudiante.id,
                    estudiante.ci,
                    estudiante.nombre,
                    estudiante.grupo or "Sin asignar",
                    estudiante.contar_calificaciones(),
                    f"{estudiante.promedio_calificaciones():.2f}"
                ))
            
            self.actualizar_estado(f"{len(estudiantes)} estudiantes cargados")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar estudiantes: {e}")
    
    def nuevo_estudiante(self):
        """Abre formulario para nuevo estudiante"""
        seleccion = self.combo_estudiantes_paralelo.get()
        if not seleccion or seleccion == "Seleccione un paralelo...":
            messagebox.showwarning("Advertencia", "Seleccione un paralelo primero")
            return
        
        # Obtener ID del paralelo
        parts = seleccion.split(' - Paralelo ')
        if len(parts) == 2:
            sigla = parts[0]
            paralelo_nombre = parts[1]
            materia = MateriaManager.obtener_por_sigla(sigla)
            if materia:
                paralelo = ParaleloManager.obtener_por_materia_paralelo(materia.id, paralelo_nombre)
                if paralelo:
                    self.abrir_formulario_estudiante(paralelo.id)
    
    def nuevo_estudiante_rapido(self):
        """Nuevo estudiante desde dashboard"""
        self.notebook.select(3)  # Cambiar a pestaña estudiantes
        self.nuevo_estudiante()
    
    def editar_estudiante(self):
        """Edita el estudiante seleccionado"""
        selection = self.tree_estudiantes.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un estudiante para editar")
            return
        
        item = selection[0]
        estudiante_id = self.tree_estudiantes.item(item)['values'][0]
        estudiante = EstudianteManager.obtener_estudiante(estudiante_id)
        
        if estudiante:
            self.abrir_formulario_estudiante(estudiante.id_paralelo.id, estudiante)
    
    def eliminar_estudiante(self):
        """Elimina el estudiante seleccionado"""
        selection = self.tree_estudiantes.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un estudiante para eliminar")
            return
        
        item = selection[0]
        values = self.tree_estudiantes.item(item)['values']
        estudiante_id = values[0]
        nombre = values[2]
        
        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar al estudiante {nombre}?\n\n"
            "Esta acción eliminará todas las calificaciones relacionadas."
        )
        
        if respuesta:
            resultado = EstudianteManager.eliminar_estudiante(estudiante_id, forzar=True)
            
            if resultado['success']:
                messagebox.showinfo("Éxito", resultado['mensaje'])
                seleccion = self.combo_estudiantes_paralelo.get()
                if seleccion and seleccion != "Seleccione un paralelo...":
                    parts = seleccion.split(' - Paralelo ')
                    if len(parts) == 2:
                        sigla = parts[0]
                        paralelo_nombre = parts[1]
                        materia = MateriaManager.obtener_por_sigla(sigla)
                        if materia:
                            paralelo = ParaleloManager.obtener_por_materia_paralelo(materia.id, paralelo_nombre)
                            if paralelo:
                                self.cargar_estudiantes(paralelo.id)
            else:
                messagebox.showerror("Error", resultado['mensaje'])
    
    def organizar_grupos(self):
        """Organiza grupos automáticamente"""
        seleccion = self.combo_estudiantes_paralelo.get()
        if not seleccion or seleccion == "Seleccione un paralelo...":
            messagebox.showwarning("Advertencia", "Seleccione un paralelo primero")
            return
        
        # Obtener número de estudiantes por grupo
        estudiantes_por_grupo = simpledialog.askinteger(
            "Organizar Grupos",
            "Número de estudiantes por grupo:",
            initialvalue=5,
            minvalue=2,
            maxvalue=10
        )
        
        if estudiantes_por_grupo:
            parts = seleccion.split(' - Paralelo ')
            if len(parts) == 2:
                sigla = parts[0]
                paralelo_nombre = parts[1]
                materia = MateriaManager.obtener_por_sigla(sigla)
                if materia:
                    paralelo = ParaleloManager.obtener_por_materia_paralelo(materia.id, paralelo_nombre)
                    if paralelo:
                        resultado = EstudianteManager.organizar_grupos_automatico(paralelo.id, estudiantes_por_grupo)
                        
                        if resultado['success']:
                            messagebox.showinfo("Éxito", resultado['mensaje'])
                            self.cargar_estudiantes(paralelo.id)
                        else:
                            messagebox.showerror("Error", resultado['mensaje'])
    
    def buscar_estudiantes(self, event=None):
        """Busca estudiantes por CI"""
        ci = self.search_estudiantes_var.get().strip()
        
        if not ci:
            seleccion = self.combo_estudiantes_paralelo.get()
            if seleccion and seleccion != "Seleccione un paralelo...":
                parts = seleccion.split(' - Paralelo ')
                if len(parts) == 2:
                    sigla = parts[0]
                    paralelo_nombre = parts[1]
                    materia = MateriaManager.obtener_por_sigla(sigla)
                    if materia:
                        paralelo = ParaleloManager.obtener_por_materia_paralelo(materia.id, paralelo_nombre)
                        if paralelo:
                            self.cargar_estudiantes(paralelo.id)
            return
        
        try:
            estudiante = EstudianteManager.obtener_por_ci(ci)
            
            # Limpiar tabla
            for item in self.tree_estudiantes.get_children():
                self.tree_estudiantes.delete(item)
            
            if estudiante:
                self.tree_estudiantes.insert('', tk.END, values=(
                    estudiante.id,
                    estudiante.ci,
                    estudiante.nombre,
                    estudiante.grupo or "Sin asignar",
                    estudiante.contar_calificaciones(),
                    f"{estudiante.promedio_calificaciones():.2f}"
                ))
                self.actualizar_estado("1 estudiante encontrado")
            else:
                self.actualizar_estado("No se encontró estudiante con ese CI")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en búsqueda: {e}")
    
    def abrir_formulario_estudiante(self, paralelo_id, estudiante=None):
        """Abre el formulario de estudiante"""
        FormularioEstudianteDialog(self.root, paralelo_id, estudiante, self.callback_estudiante)
    
    def callback_estudiante(self, resultado):
        """Callback del formulario de estudiante"""
        if resultado:
            seleccion = self.combo_estudiantes_paralelo.get()
            if seleccion and seleccion != "Seleccione un paralelo...":
                parts = seleccion.split(' - Paralelo ')
                if len(parts) == 2:
                    sigla = parts[0]
                    paralelo_nombre = parts[1]
                    materia = MateriaManager.obtener_por_sigla(sigla)
                    if materia:
                        paralelo = ParaleloManager.obtener_por_materia_paralelo(materia.id, paralelo_nombre)
                        if paralelo:
                            self.cargar_estudiantes(paralelo.id)
    
    # ==========================================
    # MÉTODOS DE LABORATORIOS
    # ==========================================
    
    def cargar_combo_materias_laboratorios(self):
        """Carga materias en el combo de laboratorios"""
        try:
            materias = MateriaManager.listar_materias()
            valores = ["Seleccione una materia..."]
            valores.extend([f"{m.sigla} - {m.materia}" for m in materias])
            
            self.combo_laboratorios_materia['values'] = valores
            if len(valores) > 1:
                self.combo_laboratorios_materia.set(valores[0])
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar materias: {e}")
    
    def on_materia_laboratorios_changed(self, event=None):
        """Maneja el cambio de materia en laboratorios"""
        seleccion = self.combo_laboratorios_materia.get()
        if seleccion and seleccion != "Seleccione una materia...":
            sigla = seleccion.split(' - ')[0]
            materia = MateriaManager.obtener_por_sigla(sigla)
            if materia:
                self.cargar_laboratorios(materia.id)
    
    def cargar_laboratorios(self, materia_id=None):
        """Carga laboratorios de una materia"""
        try:
            # Limpiar tabla
            for item in self.tree_laboratorios.get_children():
                self.tree_laboratorios.delete(item)
            
            if not materia_id:
                return
            
            laboratorios = LaboratorioManager.listar_laboratorios_por_materia(materia_id)
            
            for lab in laboratorios:
                self.tree_laboratorios.insert('', tk.END, values=(
                    lab.id,
                    lab.numero,
                    lab.titulo,
                    lab.descripcion[:50] + "..." if lab.descripcion and len(lab.descripcion) > 50 else (lab.descripcion or ""),
                    f"{lab.puntaje_maximo:.1f}",
                    lab.contar_calificaciones()
                ))
            
            self.actualizar_estado(f"{len(laboratorios)} laboratorios cargados")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar laboratorios: {e}")
    
    def nuevo_laboratorio(self):
        """Abre formulario para nuevo laboratorio"""
        seleccion = self.combo_laboratorios_materia.get()
        if not seleccion or seleccion == "Seleccione una materia...":
            messagebox.showwarning("Advertencia", "Seleccione una materia primero")
            return
        
        sigla = seleccion.split(' - ')[0]
        materia = MateriaManager.obtener_por_sigla(sigla)
        if materia:
            self.abrir_formulario_laboratorio(materia.id)
    
    def editar_laboratorio(self):
        """Edita el laboratorio seleccionado"""
        selection = self.tree_laboratorios.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un laboratorio para editar")
            return
        
        item = selection[0]
        laboratorio_id = self.tree_laboratorios.item(item)['values'][0]
        laboratorio = LaboratorioManager.obtener_laboratorio(laboratorio_id)
        
        if laboratorio:
            self.abrir_formulario_laboratorio(laboratorio.id_materia.id, laboratorio)
    
    def eliminar_laboratorio(self):
        """Elimina el laboratorio seleccionado"""
        selection = self.tree_laboratorios.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un laboratorio para eliminar")
            return
        
        item = selection[0]
        values = self.tree_laboratorios.item(item)['values']
        laboratorio_id = values[0]
        titulo = values[2]
        
        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el laboratorio '{titulo}'?\n\n"
            "Esta acción eliminará todas las calificaciones relacionadas."
        )
        
        if respuesta:
            resultado = LaboratorioManager.eliminar_laboratorio(laboratorio_id, forzar=True)
            
            if resultado['success']:
                messagebox.showinfo("Éxito", resultado['mensaje'])
                seleccion = self.combo_laboratorios_materia.get()
                if seleccion and seleccion != "Seleccione una materia...":
                    sigla = seleccion.split(' - ')[0]
                    materia = MateriaManager.obtener_por_sigla(sigla)
                    if materia:
                        self.cargar_laboratorios(materia.id)
            else:
                messagebox.showerror("Error", resultado['mensaje'])
    
    def abrir_formulario_laboratorio(self, materia_id, laboratorio=None):
        """Abre el formulario de laboratorio"""
        FormularioLaboratorioDialog(self.root, materia_id, laboratorio, self.callback_laboratorio)
    
    def callback_laboratorio(self, resultado):
        """Callback del formulario de laboratorio"""
        if resultado:
            seleccion = self.combo_laboratorios_materia.get()
            if seleccion and seleccion != "Seleccione una materia...":
                sigla = seleccion.split(' - ')[0]
                materia = MateriaManager.obtener_por_sigla(sigla)
                if materia:
                    self.cargar_laboratorios(materia.id)
            self.cargar_combos_dependientes()
    
    # ==========================================
    # MÉTODOS DE CALIFICACIONES
    # ==========================================
    
    def cargar_combo_laboratorios_calificaciones(self):
        """Carga laboratorios en el combo de calificaciones"""
        try:
            materias = MateriaManager.listar_materias()
            valores = ["Seleccione un laboratorio..."]
            
            for materia in materias:
                laboratorios = LaboratorioManager.listar_laboratorios_por_materia(materia.id)
                for lab in laboratorios:
                    valores.append(f"{materia.sigla} - Lab {lab.numero}: {lab.titulo}")
            
            self.combo_calificaciones_laboratorio['values'] = valores
            if len(valores) > 1:
                self.combo_calificaciones_laboratorio.set(valores[0])
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar laboratorios: {e}")
    
    def on_laboratorio_calificaciones_changed(self, event=None):
        """Maneja el cambio de laboratorio en calificaciones"""
        seleccion = self.combo_calificaciones_laboratorio.get()
        if seleccion and seleccion != "Seleccione un laboratorio...":
            # Extraer información del laboratorio
            parts = seleccion.split(" - Lab ")
            if len(parts) == 2:
                sigla = parts[0]
                lab_info = parts[1].split(": ")
                if len(lab_info) == 2:
                    lab_numero = int(lab_info[0])
                    materia = MateriaManager.obtener_por_sigla(sigla)
                    if materia:
                        laboratorios = LaboratorioManager.listar_laboratorios_por_materia(materia.id)
                        for lab in laboratorios:
                            if lab.numero == lab_numero:
                                self.cargar_calificaciones(lab.id)
                                break
    
    def cargar_calificaciones(self, laboratorio_id=None):
        """Carga calificaciones de un laboratorio"""
        try:
            # Limpiar tabla
            for item in self.tree_calificaciones.get_children():
                self.tree_calificaciones.delete(item)
            
            if not laboratorio_id:
                return
            
            calificaciones = CalificacionManager.obtener_calificaciones_laboratorio(laboratorio_id)
            
            for cal in calificaciones:
                estudiante = cal.id_estudiante
                nota_str = f"{cal.calificacion:.1f}" if cal.calificacion else "Sin nota"
                estado = cal.estado_aprobacion()
                fecha = cal.fecha_registro.strftime("%d/%m/%Y")
                observaciones = cal.observaciones[:30] + "..." if cal.observaciones and len(cal.observaciones) > 30 else (cal.observaciones or "")
                
                self.tree_calificaciones.insert('', tk.END, values=(
                    cal.id,
                    estudiante.ci,
                    estudiante.nombre,
                    nota_str,
                    estado,
                    fecha,
                    observaciones
                ))
            
            self.actualizar_estado(f"{len(calificaciones)} calificaciones cargadas")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar calificaciones: {e}")
    
    def nueva_calificacion(self):
        """Abre formulario para nueva calificación"""
        seleccion = self.combo_calificaciones_laboratorio.get()
        if not seleccion or seleccion == "Seleccione un laboratorio...":
            messagebox.showwarning("Advertencia", "Seleccione un laboratorio primero")
            return
        
        # Obtener ID del laboratorio
        parts = seleccion.split(" - Lab ")
        if len(parts) == 2:
            sigla = parts[0]
            lab_info = parts[1].split(": ")
            if len(lab_info) == 2:
                lab_numero = int(lab_info[0])
                materia = MateriaManager.obtener_por_sigla(sigla)
                if materia:
                    laboratorios = LaboratorioManager.listar_laboratorios_por_materia(materia.id)
                    for lab in laboratorios:
                        if lab.numero == lab_numero:
                            self.abrir_formulario_calificacion(lab.id)
                            break
    
    def nueva_calificacion_rapida(self):
        """Nueva calificación desde dashboard"""
        self.notebook.select(5)  # Cambiar a pestaña calificaciones
        self.nueva_calificacion()
    
    def editar_calificacion(self):
        """Edita la calificación seleccionada"""
        selection = self.tree_calificaciones.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una calificación para editar")
            return
        
        item = selection[0]
        calificacion_id = self.tree_calificaciones.item(item)['values'][0]
        
        # Obtener laboratorio actual
        seleccion = self.combo_calificaciones_laboratorio.get()
        if seleccion and seleccion != "Seleccione un laboratorio...":
            parts = seleccion.split(" - Lab ")
            if len(parts) == 2:
                sigla = parts[0]
                lab_info = parts[1].split(": ")
                if len(lab_info) == 2:
                    lab_numero = int(lab_info[0])
                    materia = MateriaManager.obtener_por_sigla(sigla)
                    if materia:
                        laboratorios = LaboratorioManager.listar_laboratorios_por_materia(materia.id)
                        for lab in laboratorios:
                            if lab.numero == lab_numero:
                                self.abrir_formulario_calificacion(lab.id, calificacion_id)
                                break
    
    def eliminar_calificacion(self):
        """Elimina la calificación seleccionada"""
        selection = self.tree_calificaciones.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una calificación para eliminar")
            return
        
        item = selection[0]
        values = self.tree_calificaciones.item(item)['values']
        calificacion_id = values[0]
        estudiante = values[2]
        
        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar la calificación de {estudiante}?"
        )
        
        if respuesta:
            resultado = CalificacionManager.eliminar_calificacion(calificacion_id)
            
            if resultado['success']:
                messagebox.showinfo("Éxito", resultado['mensaje'])
                seleccion = self.combo_calificaciones_laboratorio.get()
                if seleccion and seleccion != "Seleccione un laboratorio...":
                    parts = seleccion.split(" - Lab ")
                    if len(parts) == 2:
                        sigla = parts[0]
                        lab_info = parts[1].split(": ")
                        if len(lab_info) == 2:
                            lab_numero = int(lab_info[0])
                            materia = MateriaManager.obtener_por_sigla(sigla)
                            if materia:
                                laboratorios = LaboratorioManager.listar_laboratorios_por_materia(materia.id)
                                for lab in laboratorios:
                                    if lab.numero == lab_numero:
                                        self.cargar_calificaciones(lab.id)
                                        break
            else:
                messagebox.showerror("Error", resultado['mensaje'])
    
    def calificar_lotes(self):
        """Califica múltiples estudiantes por lotes"""
        seleccion = self.combo_calificaciones_laboratorio.get()
        if not seleccion or seleccion == "Seleccione un laboratorio...":
            messagebox.showwarning("Advertencia", "Seleccione un laboratorio primero")
            return
        
        # Obtener laboratorio
        parts = seleccion.split(" - Lab ")
        if len(parts) == 2:
            sigla = parts[0]
            lab_info = parts[1].split(": ")
            if len(lab_info) == 2:
                lab_numero = int(lab_info[0])
                materia = MateriaManager.obtener_por_sigla(sigla)
                if materia:
                    laboratorios = LaboratorioManager.listar_laboratorios_por_materia(materia.id)
                    for lab in laboratorios:
                        if lab.numero == lab_numero:
                            CalificacionLotesDialog(self.root, lab.id, self.callback_calificacion_lotes)
                            break
    
    def abrir_formulario_calificacion(self, laboratorio_id, calificacion_id=None):
        """Abre el formulario de calificación"""
        FormularioCalificacionDialog(self.root, laboratorio_id, calificacion_id, self.callback_calificacion)
    
    def callback_calificacion(self, resultado):
        """Callback del formulario de calificación"""
        if resultado:
            seleccion = self.combo_calificaciones_laboratorio.get()
            if seleccion and seleccion != "Seleccione un laboratorio...":
                parts = seleccion.split(" - Lab ")
                if len(parts) == 2:
                    sigla = parts[0]
                    lab_info = parts[1].split(": ")
                    if len(lab_info) == 2:
                        lab_numero = int(lab_info[0])
                        materia = MateriaManager.obtener_por_sigla(sigla)
                        if materia:
                            laboratorios = LaboratorioManager.listar_laboratorios_por_materia(materia.id)
                            for lab in laboratorios:
                                if lab.numero == lab_numero:
                                    self.cargar_calificaciones(lab.id)
                                    break
    
    def callback_calificacion_lotes(self, resultado):
        """Callback de calificación por lotes"""
        if resultado:
            self.callback_calificacion(True)
    
    # ==========================================
    # MÉTODOS DE REPORTES
    # ==========================================
    
    def cargar_combo_paralelos_reportes(self):
        """Carga paralelos en el combo de reportes"""
        try:
            materias = MateriaManager.listar_materias()
            valores = ["Seleccione un paralelo..."]
            
            for materia in materias:
                paralelos = ParaleloManager.listar_paralelos_por_materia(materia.id)
                for paralelo in paralelos:
                    valores.append(f"{materia.sigla} - Paralelo {paralelo.paralelo}")
            
            self.combo_reportes_paralelo['values'] = valores
            if len(valores) > 1:
                self.combo_reportes_paralelo.set(valores[0])
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar paralelos: {e}")
    
    def actualizar_info_reportes(self):
        """Actualiza la información en la pestaña de reportes"""
        try:
            stats = MateriaManager.obtener_estadisticas_generales()
            
            info = f"""INFORMACIÓN DEL SISTEMA DE GESTIÓN DE LABORATORIOS
{'=' * 60}

ESTADÍSTICAS GENERALES:
- Total de materias: {stats['total_materias']}
- Total de paralelos: {stats['total_paralelos']}
- Total de estudiantes: {stats['total_estudiantes']}
- Total de laboratorios: {stats['total_laboratorios']}

PROMEDIOS:
- Paralelos por materia: {stats['promedio_paralelos_por_materia']:.1f}
- Estudiantes por materia: {stats['promedio_estudiantes_por_materia']:.1f}

DETALLE POR MATERIA:
{'=' * 60}
"""
            
            materias = MateriaManager.listar_materias()
            for materia in materias:
                stats_materia = materia.estadisticas_completas()
                info += f"""
{materia.sigla} - {materia.materia}
  Docente: {materia.docente_teoria}
  Paralelos: {stats_materia['paralelos']}
  Estudiantes: {stats_materia['estudiantes_total']}
  Laboratorios: {stats_materia['laboratorios']}
"""
            
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info)
            self.info_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar información: {e}")
    
    def generar_pdf(self):
        """Genera reporte PDF del paralelo seleccionado"""
        seleccion = self.combo_reportes_paralelo.get()
        if not seleccion or seleccion == "Seleccione un paralelo...":
            messagebox.showwarning("Advertencia", "Seleccione un paralelo primero")
            return
        
        try:
            # Obtener paralelo
            parts = seleccion.split(' - Paralelo ')
            if len(parts) == 2:
                sigla = parts[0]
                paralelo_nombre = parts[1]
                materia = MateriaManager.obtener_por_sigla(sigla)
                if materia:
                    paralelo = ParaleloManager.obtener_por_materia_paralelo(materia.id, paralelo_nombre)
                    if paralelo:
                        self.actualizar_estado("Generando PDF...")
                        archivo = PDFExporter.generar_reporte_paralelo(paralelo.id)
                        
                        if archivo:
                            messagebox.showinfo("Éxito", f"PDF generado exitosamente:\n{archivo}")
                            self.actualizar_estado("PDF generado exitosamente")
                        else:
                            messagebox.showerror("Error", "Error al generar PDF")
                            self.actualizar_estado("Error al generar PDF")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
            self.actualizar_estado(f"Error: {e}")
    
    def generar_pdf_directo(self):
        """Genera PDF directo desde menú"""
        self.notebook.select(6)  # Cambiar a pestaña reportes
        self.generar_pdf()
    
    def generar_excel(self):
        """Genera reporte Excel"""
        messagebox.showinfo("Información", "Funcionalidad Excel próximamente disponible")
    
    def ver_matriz(self):
        """Muestra matriz de calificaciones"""
        seleccion = self.combo_reportes_paralelo.get()
        if not seleccion or seleccion == "Seleccione un paralelo...":
            messagebox.showwarning("Advertencia", "Seleccione un paralelo primero")
            return
        
        # Obtener paralelo
        parts = seleccion.split(' - Paralelo ')
        if len(parts) == 2:
            sigla = parts[0]
            paralelo_nombre = parts[1]
            materia = MateriaManager.obtener_por_sigla(sigla)
            if materia:
                paralelo = ParaleloManager.obtener_por_materia_paralelo(materia.id, paralelo_nombre)
                if paralelo:
                    MatrizCalificacionesDialog(self.root, paralelo.id)
    
    def ver_estadisticas_paralelo(self):
        """Muestra estadísticas del paralelo seleccionado"""
        seleccion = self.combo_reportes_paralelo.get()
        if not seleccion or seleccion == "Seleccione un paralelo...":
            messagebox.showwarning("Advertencia", "Seleccione un paralelo primero")
            return
        
        # Obtener paralelo
        parts = seleccion.split(' - Paralelo ')
        if len(parts) == 2:
            sigla = parts[0]
            paralelo_nombre = parts[1]
            materia = MateriaManager.obtener_por_sigla(sigla)
            if materia:
                paralelo = ParaleloManager.obtener_por_materia_paralelo(materia.id, paralelo_nombre)
                if paralelo:
                    EstadisticasParaleloDialog(self.root, paralelo.id)
    
    def mostrar_matriz_calificaciones(self):
        """Muestra diálogo de matriz de calificaciones"""
        SelectorParaleloDialog(self.root, "Seleccionar Paralelo para Matriz", self.callback_matriz)
    
    def callback_matriz(self, paralelo_id):
        """Callback para mostrar matriz"""
        if paralelo_id:
            MatrizCalificacionesDialog(self.root, paralelo_id)
    
    # ==========================================
    # MÉTODOS AUXILIARES
    # ==========================================
    
    def cargar_combos_dependientes(self):
        """Recarga todos los combos que dependen de otros datos"""
        self.cargar_combo_materias_paralelos()
        self.cargar_combo_paralelos_estudiantes()
        self.cargar_combo_materias_laboratorios()
        self.cargar_combo_laboratorios_calificaciones()
        self.cargar_combo_paralelos_reportes()
    
    def actualizar_estado(self, mensaje):
        """Actualiza la barra de estado"""
        self.status_label.config(text=mensaje)
        self.root.update_idletasks()
    
    def nuevo_elemento(self):
        """Nuevo elemento según pestaña activa"""
        tab_actual = self.notebook.index(self.notebook.select())
        
        if tab_actual == 1:  # Materias
            self.nueva_materia()
        elif tab_actual == 2:  # Paralelos
            self.nuevo_paralelo()
        elif tab_actual == 3:  # Estudiantes
            self.nuevo_estudiante()
        elif tab_actual == 4:  # Laboratorios
            self.nuevo_laboratorio()
        elif tab_actual == 5:  # Calificaciones
            self.nueva_calificacion()
    
    def exportar_pdf(self):
        """Exporta PDF desde menú"""
        self.generar_pdf_directo()
    
    def exportar_excel(self):
        """Exporta Excel desde menú"""
        self.generar_excel()
    
    def generar_reporte_rapido(self):
        """Generar reporte desde dashboard"""
        self.notebook.select(6)  # Cambiar a pestaña reportes
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas generales"""
        EstadisticasGeneralesDialog(self.root)
    
    def mostrar_acerca_de(self):
        """Muestra información acerca de"""
        messagebox.showinfo(
            "Acerca de",
            "Sistema de Gestión de Laboratorios\n\n"
            "Universidad Técnica de Oruro\n"
            "SIS 2420 - Actualización Tecnológica\n\n"
            "Desarrollado con Python + Tkinter\n"
            "Versión: 1.0"
        )
    
    def cerrar_aplicacion(self):
        """Cierra la aplicación"""
        if messagebox.askyesno("Confirmar Salida", "¿Está seguro que desea cerrar el sistema?"):
            cerrar_bd()
            self.root.destroy()
    
    def ejecutar(self):
        """Ejecuta la aplicación desktop"""
        self.actualizar_estado("Sistema iniciado correctamente")
        self.root.mainloop()

# ==========================================
# FORMULARIOS DE DIÁLOGO
# ==========================================

class FormularioMateriaDialog:
    """Diálogo para crear/editar materias"""
    
    def __init__(self, parent, materia=None, callback=None):
        self.materia = materia
        self.callback = callback
        self.resultado = False
        
        # Crear ventana
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Editar Materia" if materia else "Nueva Materia")
        self.dialog.geometry("500x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Centrar ventana
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (350 // 2)
        self.dialog.geometry(f"500x350+{x}+{y}")
        
        self.crear_formulario()
        
        # Protocolo de cierre
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancelar)
    
    def crear_formulario(self):
        """Crea el formulario"""
        # Frame principal
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = ttk.Label(
            main_frame, 
            text="Editar Materia" if self.materia else "Nueva Materia",
            font=("Arial", 14, "bold")
        )
        titulo.pack(pady=(0, 20))
        
        # Campos del formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Materia
        ttk.Label(form_frame, text="Nombre de la materia:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_materia = ttk.Entry(form_frame, width=50)
        self.entry_materia.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Sigla
        ttk.Label(form_frame, text="Sigla:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_sigla = ttk.Entry(form_frame, width=50)
        self.entry_sigla.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Docente
        ttk.Label(form_frame, text="Docente de teoría:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_docente = ttk.Entry(form_frame, width=50)
        self.entry_docente.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame, text="Guardar", command=self.guardar).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cancelar", command=self.cancelar).pack(side=tk.LEFT, padx=10)
        
        # Cargar datos si es edición
        if self.materia:
            self.entry_materia.insert(0, self.materia.materia)
            self.entry_sigla.insert(0, self.materia.sigla)
            self.entry_docente.insert(0, self.materia.docente_teoria)
        
        # Focus inicial
        self.entry_materia.focus()
    
    def guardar(self):
        """Guarda la materia"""
        materia = self.entry_materia.get().strip()
        sigla = self.entry_sigla.get().strip()
        docente = self.entry_docente.get().strip()
        
        if not materia or not sigla or not docente:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        try:
            if self.materia:  # Edición
                resultado = MateriaManager.actualizar_materia(
                    self.materia.id,
                    materia=materia,
                    sigla=sigla,
                    docente_teoria=docente
                )
            else:  # Creación
                resultado = MateriaManager.crear_materia(materia, sigla, docente)
            
            if resultado:
                messagebox.showinfo("Éxito", "Materia guardada exitosamente")
                self.resultado = True
                self.dialog.destroy()
                if self.callback:
                    self.callback(True)
            else:
                messagebox.showerror("Error", "No se pudo guardar la materia")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")
    
    def cancelar(self):
        """Cancela el formulario"""
        self.dialog.destroy()
        if self.callback:
            self.callback(False)

class FormularioParaleloDialog:
    """Diálogo para crear/editar paralelos"""
    
    def __init__(self, parent, materia_id, paralelo=None, callback=None):
        self.materia_id = materia_id
        self.paralelo = paralelo
        self.callback = callback
        
        # Crear ventana
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Editar Paralelo" if paralelo else "Nuevo Paralelo")
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Centrar ventana
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (250 // 2)
        self.dialog.geometry(f"400x250+{x}+{y}")
        
        self.crear_formulario()
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancelar)
    
    def crear_formulario(self):
        """Crea el formulario"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        titulo = ttk.Label(
            main_frame,
            text="Editar Paralelo" if self.paralelo else "Nuevo Paralelo",
            font=("Arial", 14, "bold")
        )
        titulo.pack(pady=(0, 20))
        
        # Mostrar materia
        materia = MateriaManager.obtener_materia(self.materia_id)
        if materia:
            info_label = ttk.Label(main_frame, text=f"Materia: {materia.sigla} - {materia.materia}")
            info_label.pack(pady=(0, 20))
        
        # Campo paralelo
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(form_frame, text="Paralelo:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_paralelo = ttk.Entry(form_frame, width=20)
        self.entry_paralelo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(form_frame, text="Ejemplos: A, B, C, 1, 2, etc.").grid(row=1, column=1, sticky=tk.W, pady=5)
        
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame, text="Guardar", command=self.guardar).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cancelar", command=self.cancelar).pack(side=tk.LEFT, padx=10)
        
        # Cargar datos si es edición
        if self.paralelo:
            self.entry_paralelo.insert(0, self.paralelo.paralelo)
        
        self.entry_paralelo.focus()
    
    def guardar(self):
        """Guarda el paralelo"""
        paralelo = self.entry_paralelo.get().strip()
        
        if not paralelo:
            messagebox.showerror("Error", "El nombre del paralelo es obligatorio")
            return
        
        try:
            if self.paralelo:  # Edición
                resultado = ParaleloManager.actualizar_paralelo(self.paralelo.id, paralelo=paralelo)
            else:  # Creación
                resultado = ParaleloManager.crear_paralelo(self.materia_id, paralelo)
            
            if resultado:
                messagebox.showinfo("Éxito", "Paralelo guardado exitosamente")
                self.dialog.destroy()
                if self.callback:
                    self.callback(True)
            else:
                messagebox.showerror("Error", "No se pudo guardar el paralelo")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")
    
    def cancelar(self):
        """Cancela el formulario"""
        self.dialog.destroy()
        if self.callback:
            self.callback(False)

class FormularioEstudianteDialog:
    """Diálogo para crear/editar estudiantes"""
    
    def __init__(self, parent, paralelo_id, estudiante=None, callback=None):
        self.paralelo_id = paralelo_id
        self.estudiante = estudiante
        self.callback = callback
        
        # Crear ventana
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Editar Estudiante" if estudiante else "Nuevo Estudiante")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Centrar ventana
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        self.crear_formulario()
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancelar)
    
    def crear_formulario(self):
        """Crea el formulario"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        titulo = ttk.Label(
            main_frame,
            text="Editar Estudiante" if self.estudiante else "Nuevo Estudiante",
            font=("Arial", 14, "bold")
        )
        titulo.pack(pady=(0, 20))
        
        # Mostrar paralelo
        paralelo = ParaleloManager.obtener_paralelo(self.paralelo_id)
        if paralelo:
            info_label = ttk.Label(
                main_frame,
                text=f"Paralelo: {paralelo.id_materia.sigla} - Paralelo {paralelo.paralelo}"
            )
            info_label.pack(pady=(0, 20))
        
        # Campos del formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Nombre
        ttk.Label(form_frame, text="Nombre completo:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_nombre = ttk.Entry(form_frame, width=50)
        self.entry_nombre.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # CI
        ttk.Label(form_frame, text="Cédula de identidad:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_ci = ttk.Entry(form_frame, width=50)
        self.entry_ci.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Grupo
        ttk.Label(form_frame, text="Grupo (opcional):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_grupo = ttk.Entry(form_frame, width=50)
        self.entry_grupo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame, text="Guardar", command=self.guardar).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cancelar", command=self.cancelar).pack(side=tk.LEFT, padx=10)
        
        # Cargar datos si es edición
        if self.estudiante:
            self.entry_nombre.insert(0, self.estudiante.nombre)
            self.entry_ci.insert(0, self.estudiante.ci)
            self.entry_grupo.insert(0, self.estudiante.grupo or "")
        
        self.entry_nombre.focus()
    
    def guardar(self):
        """Guarda el estudiante"""
        nombre = self.entry_nombre.get().strip()
        ci = self.entry_ci.get().strip()
        grupo = self.entry_grupo.get().strip()
        
        if not nombre or not ci:
            messagebox.showerror("Error", "Nombre y CI son obligatorios")
            return
        
        try:
            if self.estudiante:  # Edición
                resultado = EstudianteManager.actualizar_estudiante(
                    self.estudiante.id,
                    nombre=nombre,
                    ci=ci,
                    grupo=grupo or None
                )
            else:  # Creación
                resultado = EstudianteManager.registrar_estudiante(
                    nombre, ci, self.paralelo_id, grupo or None
                )
            
            if resultado:
                messagebox.showinfo("Éxito", "Estudiante guardado exitosamente")
                self.dialog.destroy()
                if self.callback:
                    self.callback(True)
            else:
                messagebox.showerror("Error", "No se pudo guardar el estudiante")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")
    
    def cancelar(self):
        """Cancela el formulario"""
        self.dialog.destroy()
        if self.callback:
            self.callback(False)

class FormularioLaboratorioDialog:
    """Diálogo para crear/editar laboratorios"""
    
    def __init__(self, parent, materia_id, laboratorio=None, callback=None):
        self.materia_id = materia_id
        self.laboratorio = laboratorio
        self.callback = callback
        
        # Crear ventana
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Editar Laboratorio" if laboratorio else "Nuevo Laboratorio")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Centrar ventana
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        self.crear_formulario()
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancelar)
    
    def crear_formulario(self):
        """Crea el formulario"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        titulo = ttk.Label(
            main_frame,
            text="Editar Laboratorio" if self.laboratorio else "Nuevo Laboratorio",
            font=("Arial", 14, "bold")
        )
        titulo.pack(pady=(0, 20))
        
        # Mostrar materia
        materia = MateriaManager.obtener_materia(self.materia_id)
        if materia:
            info_label = ttk.Label(main_frame, text=f"Materia: {materia.sigla} - {materia.materia}")
            info_label.pack(pady=(0, 20))
        
        # Campos del formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Título
        ttk.Label(form_frame, text="Título del laboratorio:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_titulo = ttk.Entry(form_frame, width=50)
        self.entry_titulo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Descripción
        ttk.Label(form_frame, text="Descripción:").grid(row=1, column=0, sticky=(tk.W, tk.N), pady=5)
        self.text_descripcion = tk.Text(form_frame, width=50, height=5)
        self.text_descripcion.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Puntaje máximo
        ttk.Label(form_frame, text="Puntaje máximo:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_puntaje = ttk.Entry(form_frame, width=20)
        self.entry_puntaje.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        self.entry_puntaje.insert(0, "100")
        
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame, text="Guardar", command=self.guardar).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cancelar", command=self.cancelar).pack(side=tk.LEFT, padx=10)
        
        # Cargar datos si es edición
        if self.laboratorio:
            self.entry_titulo.insert(0, self.laboratorio.titulo)
            self.text_descripcion.insert(1.0, self.laboratorio.descripcion or "")
            self.entry_puntaje.delete(0, tk.END)
            self.entry_puntaje.insert(0, str(self.laboratorio.puntaje_maximo))
        
        self.entry_titulo.focus()
    
    def guardar(self):
        """Guarda el laboratorio"""
        titulo = self.entry_titulo.get().strip()
        descripcion = self.text_descripcion.get(1.0, tk.END).strip()
        puntaje_str = self.entry_puntaje.get().strip()
        
        if not titulo:
            messagebox.showerror("Error", "El título es obligatorio")
            return
        
        try:
            puntaje = float(puntaje_str) if puntaje_str else 100.0
        except ValueError:
            messagebox.showerror("Error", "El puntaje debe ser un número")
            return
        
        try:
            if self.laboratorio:  # Edición
                resultado = LaboratorioManager.actualizar_laboratorio(
                    self.laboratorio.id,
                    titulo=titulo,
                    descripcion=descripcion or None,
                    puntaje_maximo=puntaje
                )
            else:  # Creación
                resultado = LaboratorioManager.crear_laboratorio(
                    self.materia_id, titulo, descripcion or None, puntaje
                )
            
            if resultado:
                messagebox.showinfo("Éxito", "Laboratorio guardado exitosamente")
                self.dialog.destroy()
                if self.callback:
                    self.callback(True)
            else:
                messagebox.showerror("Error", "No se pudo guardar el laboratorio")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")
    
    def cancelar(self):
        """Cancela el formulario"""
        self.dialog.destroy()
        if self.callback:
            self.callback(False)

class FormularioCalificacionDialog:
    """Diálogo para crear/editar calificaciones"""
    
    def __init__(self, parent, laboratorio_id, calificacion_id=None, callback=None):
        self.laboratorio_id = laboratorio_id
        self.calificacion_id = calificacion_id
        self.callback = callback
        self.es_edicion = calificacion_id is not None
        
        # Crear ventana
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Editar Calificación" if self.es_edicion else "Nueva Calificación")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Centrar ventana
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        self.crear_formulario()
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancelar)
    
    def crear_formulario(self):
        """Crea el formulario"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        titulo = ttk.Label(
            main_frame,
            text="Editar Calificación" if self.es_edicion else "Nueva Calificación",
            font=("Arial", 14, "bold")
        )
        titulo.pack(pady=(0, 20))
        
        # Mostrar laboratorio
        laboratorio = LaboratorioManager.obtener_laboratorio(self.laboratorio_id)
        if laboratorio:
            info_label = ttk.Label(
                main_frame,
                text=f"Laboratorio: {laboratorio.id_materia.sigla} - Lab {laboratorio.numero}: {laboratorio.titulo}"
            )
            info_label.pack(pady=(0, 10))
            
            puntaje_label = ttk.Label(
                main_frame,
                text=f"Puntaje máximo: {laboratorio.puntaje_maximo}",
                font=("Arial", 10, "italic")
            )
            puntaje_label.pack(pady=(0, 20))
        
        # Campos del formulario
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        row = 0
        
        # CI del estudiante (solo para nueva calificación)
        if not self.es_edicion:
            ttk.Label(form_frame, text="CI del estudiante:").grid(row=row, column=0, sticky=tk.W, pady=5)
            self.entry_ci = ttk.Entry(form_frame, width=30)
            self.entry_ci.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
            row += 1
        
        # Calificación
        ttk.Label(form_frame, text="Calificación:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.entry_calificacion = ttk.Entry(form_frame, width=20)
        self.entry_calificacion.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Observaciones
        ttk.Label(form_frame, text="Observaciones:").grid(row=row, column=0, sticky=(tk.W, tk.N), pady=5)
        self.text_observaciones = tk.Text(form_frame, width=40, height=5)
        self.text_observaciones.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=30)
        
        ttk.Button(btn_frame, text="Guardar", command=self.guardar).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cancelar", command=self.cancelar).pack(side=tk.LEFT, padx=10)
        
        # Cargar datos si es edición
        if self.es_edicion:
            self.cargar_datos_calificacion()
        
        # Focus inicial
        if self.es_edicion:
            self.entry_calificacion.focus()
        else:
            self.entry_ci.focus()
    
    def cargar_datos_calificacion(self):
        """Carga datos de la calificación para edición"""
        try:
            from models.calificacion import Calificacion
            calificacion = Calificacion.get_by_id(self.calificacion_id)
            
            if calificacion.calificacion is not None:
                self.entry_calificacion.insert(0, str(calificacion.calificacion))
            
            if calificacion.observaciones:
                self.text_observaciones.insert(1.0, calificacion.observaciones)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar calificación: {e}")
    
    def guardar(self):
        """Guarda la calificación"""
        calificacion_str = self.entry_calificacion.get().strip()
        observaciones = self.text_observaciones.get(1.0, tk.END).strip()
        
        if not calificacion_str:
            messagebox.showerror("Error", "La calificación es obligatoria")
            return
        
        try:
            calificacion = float(calificacion_str)
        except ValueError:
            messagebox.showerror("Error", "La calificación debe ser un número")
            return
        
        try:
            if self.es_edicion:
                resultado = CalificacionManager.actualizar_calificacion(
                    self.calificacion_id,
                    calificacion,
                    observaciones or None
                )
            else:
                ci = self.entry_ci.get().strip()
                if not ci:
                    messagebox.showerror("Error", "El CI del estudiante es obligatorio")
                    return
                
                estudiante = EstudianteManager.obtener_por_ci(ci)
                if not estudiante:
                    messagebox.showerror("Error", "No existe estudiante con ese CI")
                    return
                
                resultado = CalificacionManager.registrar_calificacion(
                    self.laboratorio_id, estudiante.id, calificacion, observaciones or None
                )
            
            if resultado:
                messagebox.showinfo("Éxito", "Calificación guardada exitosamente")
                self.dialog.destroy()
                if self.callback:
                    self.callback(True)
            else:
                messagebox.showerror("Error", "No se pudo guardar la calificación")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")
    
    def cancelar(self):
        """Cancela el formulario"""
        self.dialog.destroy()
        if self.callback:
            self.callback(False)

class CalificacionLotesDialog:
    """Diálogo para calificar por lotes"""
    
    def __init__(self, parent, laboratorio_id, callback=None):
        self.laboratorio_id = laboratorio_id
        self.callback = callback
        
        # Crear ventana
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Calificar por Lotes")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Centrar ventana
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        self.crear_formulario()
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancelar)
    
    def crear_formulario(self):
        """Crea el formulario"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        titulo = ttk.Label(main_frame, text="Calificar por Lotes", font=("Arial", 14, "bold"))
        titulo.pack(pady=(0, 20))
        
        # Mostrar laboratorio
        laboratorio = LaboratorioManager.obtener_laboratorio(self.laboratorio_id)
        if laboratorio:
            info_label = ttk.Label(
                main_frame,
                text=f"Laboratorio: {laboratorio.id_materia.sigla} - Lab {laboratorio.numero}: {laboratorio.titulo}"
            )
            info_label.pack(pady=(0, 10))
            
            puntaje_label = ttk.Label(
                main_frame,
                text=f"Puntaje máximo: {laboratorio.puntaje_maximo}",
                font=("Arial", 10, "italic")
            )
            puntaje_label.pack(pady=(0, 20))
        
        # Instrucciones
        instrucciones = ttk.Label(
            main_frame,
            text="Ingrese las calificaciones en el siguiente formato:\nCI,calificacion (ejemplo: 12345678,85.5)\nUna por línea:",
            font=("Arial", 10)
        )
        instrucciones.pack(pady=(0, 10))
        
        # Area de texto para calificaciones
        self.text_calificaciones = tk.Text(main_frame, width=60, height=15)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.text_calificaciones.yview)
        self.text_calificaciones.configure(yscrollcommand=scrollbar.set)
        
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.text_calificaciones.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Procesar Calificaciones", command=self.procesar).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cancelar", command=self.cancelar).pack(side=tk.LEFT, padx=10)
        
        self.text_calificaciones.focus()
    
    def procesar(self):
        """Procesa las calificaciones por lotes"""
        texto = self.text_calificaciones.get(1.0, tk.END).strip()
        
        if not texto:
            messagebox.showerror("Error", "Debe ingresar al menos una calificación")
            return
        
        lineas = [linea.strip() for linea in texto.split('\n') if linea.strip()]
        calificaciones_dict = {}
        errores = []
        
        for i, linea in enumerate(lineas, 1):
            if ',' not in linea:
                errores.append(f"Línea {i}: Formato incorrecto")
                continue
            
            try:
                ci, calificacion_str = linea.split(',', 1)
                ci = ci.strip()
                calificacion = float(calificacion_str.strip())
                
                # Verificar estudiante
                estudiante = EstudianteManager.obtener_por_ci(ci)
                if not estudiante:
                    errores.append(f"Línea {i}: No existe estudiante con CI {ci}")
                    continue
                
                calificaciones_dict[estudiante.id] = calificacion
                
            except ValueError:
                errores.append(f"Línea {i}: La calificación debe ser un número")
                continue
            except Exception as e:
                errores.append(f"Línea {i}: {e}")
                continue
        
        if not calificaciones_dict:
            messagebox.showerror("Error", "No hay calificaciones válidas para procesar")
            return
        
        # Mostrar resumen
        mensaje = f"Se procesarán {len(calificaciones_dict)} calificaciones."
        if errores:
            mensaje += f"\n{len(errores)} líneas con errores serán omitidas."
        
        mensaje += "\n\n¿Continuar?"
        
        if not messagebox.askyesno("Confirmar", mensaje):
            return
        
        try:
            resultado = CalificacionManager.calificar_por_lotes(self.laboratorio_id, calificaciones_dict)
            
            if resultado['success']:
                mensaje_resultado = f"Procesamiento completado:\n"
                mensaje_resultado += f"- Calificaciones exitosas: {resultado['exitosas']}\n"
                
                if resultado['errores']:
                    mensaje_resultado += f"- Errores: {len(resultado['errores'])}\n\n"
                    mensaje_resultado += "Errores encontrados:\n"
                    for error in resultado['errores'][:5]:  # Mostrar solo los primeros 5
                        mensaje_resultado += f"- {error}\n"
                    if len(resultado['errores']) > 5:
                        mensaje_resultado += f"... y {len(resultado['errores']) - 5} más"
                
                messagebox.showinfo("Resultado", mensaje_resultado)
                
                self.dialog.destroy()
                if self.callback:
                    self.callback(True)
            else:
                messagebox.showerror("Error", resultado['mensaje'])
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar calificaciones: {e}")
    
    def cancelar(self):
        """Cancela la operación"""
        self.dialog.destroy()
        if self.callback:
            self.callback(False)

class MatrizCalificacionesDialog:
    """Diálogo para mostrar matriz de calificaciones"""
    
    def __init__(self, parent, paralelo_id):
        self.paralelo_id = paralelo_id
        
        # Crear ventana
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Matriz de Calificaciones")
        self.dialog.geometry("900x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar ventana
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"900x600+{x}+{y}")
        
        self.crear_interfaz()
        self.dialog.protocol("WM_DELETE_WINDOW", self.cerrar)
    
    def crear_interfaz(self):
        """Crea la interfaz de la matriz"""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        paralelo = ParaleloManager.obtener_paralelo(self.paralelo_id)
        if paralelo:
            titulo = ttk.Label(
                main_frame,
                text=f"Matriz de Calificaciones - {paralelo.id_materia.sigla} Paralelo {paralelo.paralelo}",
                font=("Arial", 14, "bold")
            )
            titulo.pack(pady=(0, 20))
        
        # Frame para la matriz
        matriz_frame = ttk.Frame(main_frame)
        matriz_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear tabla con scrollbars
        self.tree = ttk.Treeview(matriz_frame, show='headings')
        
        scrollbar_v = ttk.Scrollbar(matriz_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_h = ttk.Scrollbar(matriz_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_v.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_h.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        matriz_frame.grid_rowconfigure(0, weight=1)
        matriz_frame.grid_columnconfigure(0, weight=1)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Exportar PDF", command=self.exportar_pdf).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cerrar", command=self.cerrar).pack(side=tk.LEFT, padx=10)
        
        # Cargar datos
        self.cargar_matriz()
    
    def cargar_matriz(self):
        """Carga la matriz de calificaciones"""
        try:
            paralelo = ParaleloManager.obtener_paralelo(self.paralelo_id)
            if not paralelo:
                return
            
            from models.calificacion import Calificacion
            from models.laboratorio import Laboratorio
            
            # Obtener matriz y laboratorios
            matriz = Calificacion.matriz_calificaciones_paralelo(paralelo)
            laboratorios = list(Laboratorio.obtener_por_materia(paralelo.id_materia))
            
            if not matriz or not laboratorios:
                messagebox.showinfo("Información", "No hay datos de calificaciones disponibles")
                return
            
            # Configurar columnas
            columnas = ['CI', 'Estudiante', 'Grupo']
            columnas.extend([f'Lab {lab.numero}' for lab in laboratorios])
            columnas.append('Promedio')
            
            self.tree['columns'] = columnas
            
            # Configurar encabezados
            for col in columnas:
                self.tree.heading(col, text=col)
                if col in ['CI', 'Grupo', 'Promedio']:
                    self.tree.column(col, width=80)
                elif col == 'Estudiante':
                    self.tree.column(col, width=200)
                else:
                    self.tree.column(col, width=60)
            
            # Insertar datos
            for fila in matriz:
                valores = [
                    fila['ci'],
                    fila['estudiante'],
                    fila['grupo'] or 'Sin asignar'
                ]
                
                # Agregar calificaciones por laboratorio
                for lab in laboratorios:
                    cal = fila['calificaciones'].get(f'lab_{lab.numero}')
                    if cal is not None:
                        valores.append(f"{cal:.0f}")
                    else:
                        valores.append("--")
                
                # Agregar promedio
                valores.append(f"{fila['promedio']:.1f}")
                
                self.tree.insert('', tk.END, values=valores)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar matriz: {e}")
    
    def exportar_pdf(self):
        """Exporta la matriz a PDF"""
        try:
            archivo = PDFExporter.generar_reporte_paralelo(self.paralelo_id)
            if archivo:
                messagebox.showinfo("Éxito", f"PDF generado: {archivo}")
            else:
                messagebox.showerror("Error", "Error al generar PDF")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
    
    def cerrar(self):
        """Cierra el diálogo"""
        self.dialog.destroy()

class EstadisticasGeneralesDialog:
    """Diálogo para mostrar estadísticas generales"""
    
    def __init__(self, parent):
        # Crear ventana
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Estadísticas Generales del Sistema")
        self.dialog.geometry("700x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar ventana
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"700x500+{x}+{y}")
        
        self.crear_interfaz()
        self.dialog.protocol("WM_DELETE_WINDOW", self.cerrar)
    
    def crear_interfaz(self):
        """Crea la interfaz de estadísticas"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        titulo = ttk.Label(
            main_frame,
            text="Estadísticas Generales del Sistema",
            font=("Arial", 16, "bold")
        )
        titulo.pack(pady=(0, 20))
        
        # Area de texto con scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_stats = tk.Text(text_frame, state=tk.DISABLED, font=("Courier", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_stats.yview)
        self.text_stats.configure(yscrollcommand=scrollbar.set)
        
        self.text_stats.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", command=self.cerrar).pack(pady=20)
        
        # Cargar estadísticas
        self.cargar_estadisticas()
    
    def cargar_estadisticas(self):
        """Carga las estadísticas del sistema"""
        try:
            stats = MateriaManager.obtener_estadisticas_generales()
            materias = MateriaManager.listar_materias()
            
            contenido = f"""ESTADÍSTICAS GENERALES DEL SISTEMA
{'=' * 60}

RESUMEN GLOBAL:
  Total de materias:     {stats['total_materias']:3d}
  Total de paralelos:    {stats['total_paralelos']:3d}
  Total de estudiantes:  {stats['total_estudiantes']:3d}
  Total de laboratorios: {stats['total_laboratorios']:3d}

PROMEDIOS:
  Paralelos por materia:  {stats['promedio_paralelos_por_materia']:5.1f}
  Estudiantes por materia: {stats['promedio_estudiantes_por_materia']:5.1f}

DETALLE POR MATERIA:
{'=' * 60}

Sigla      | Materia                  | Par | Est | Lab
{'-' * 60}
"""
            
            for materia in materias:
                stats_materia = materia.estadisticas_completas()
                contenido += f"{stats_materia['sigla']:10s} | {materia.materia[:23]:23s} | {stats_materia['paralelos']:3d} | {stats_materia['estudiantes_total']:3d} | {stats_materia['laboratorios']:3d}\n"
            
            contenido += f"\n\nReporte generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            
            self.text_stats.config(state=tk.NORMAL)
            self.text_stats.insert(1.0, contenido)
            self.text_stats.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar estadísticas: {e}")
    
    def cerrar(self):
        """Cierra el diálogo"""
        self.dialog.destroy()

class EstadisticasParaleloDialog:
    """Diálogo para mostrar estadísticas de un paralelo"""
    
    def __init__(self, parent, paralelo_id):
        self.paralelo_id = paralelo_id
        
        # Crear ventana
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Estadísticas del Paralelo")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar ventana
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"600x400+{x}+{y}")
        
        self.crear_interfaz()
        self.dialog.protocol("WM_DELETE_WINDOW", self.cerrar)
    
    def crear_interfaz(self):
        """Crea la interfaz de estadísticas"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        paralelo = ParaleloManager.obtener_paralelo(self.paralelo_id)
        if paralelo:
            titulo = ttk.Label(
                main_frame,
                text=f"Estadísticas - {paralelo.id_materia.sigla} Paralelo {paralelo.paralelo}",
                font=("Arial", 14, "bold")
            )
            titulo.pack(pady=(0, 20))
        
        # Area de texto
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_stats = tk.Text(text_frame, state=tk.DISABLED, font=("Courier", 11))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_stats.yview)
        self.text_stats.configure(yscrollcommand=scrollbar.set)
        
        self.text_stats.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", command=self.cerrar).pack(pady=20)
        
        # Cargar estadísticas
        self.cargar_estadisticas()
    
    def cargar_estadisticas(self):
        """Carga las estadísticas del paralelo"""
        try:
            paralelo = ParaleloManager.obtener_paralelo(self.paralelo_id)
            if not paralelo:
                return
            
            # Estadísticas de estudiantes
            stats_estudiantes = EstudianteManager.obtener_estadisticas_paralelo(self.paralelo_id)
            
            # Estadísticas de calificaciones
            from models.calificacion import Calificacion
            stats_calificaciones = Calificacion.estadisticas_paralelo(paralelo)
            
            contenido = f"""ESTADÍSTICAS DEL PARALELO
{'=' * 50}

INFORMACIÓN GENERAL:
  Materia: {paralelo.id_materia.materia}
  Sigla: {paralelo.id_materia.sigla}
  Paralelo: {paralelo.paralelo}
  Docente: {paralelo.id_materia.docente_teoria}

ESTUDIANTES:
  Total estudiantes:      {stats_estudiantes['total_estudiantes']}
  Total grupos:           {stats_estudiantes['total_grupos']}
  Estudiantes sin grupo:  {stats_estudiantes['estudiantes_sin_grupo']}
  
  Grupos creados: {', '.join(stats_estudiantes['grupos_lista']) if stats_estudiantes['grupos_lista'] else 'Ninguno'}

CALIFICACIONES:
  Total calificaciones:   {stats_calificaciones['total_calificaciones']}
  Promedio general:       {stats_calificaciones['promedio_general']:.2f}
  Calificaciones aprobadas (≥51): {stats_calificaciones['aprobados']}
  Calificaciones reprobadas (<51): {stats_calificaciones['reprobados']}
  Sin calificar:          {stats_calificaciones['sin_calificar']}
"""
            
            if stats_calificaciones['total_calificaciones'] > 0:
                porcentaje_aprobacion = (stats_calificaciones['aprobados'] / stats_calificaciones['total_calificaciones']) * 100
                contenido += f"  Porcentaje de aprobación: {porcentaje_aprobacion:.1f}%\n"
            
            contenido += f"\n\nReporte generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            
            self.text_stats.config(state=tk.NORMAL)
            self.text_stats.insert(1.0, contenido)
            self.text_stats.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar estadísticas: {e}")
    
    def cerrar(self):
        """Cierra el diálogo"""
        self.dialog.destroy()

class SelectorParaleloDialog:
    """Diálogo para seleccionar un paralelo"""
    
    def __init__(self, parent, titulo, callback):
        self.callback = callback
        self.resultado = None
        
        # Crear ventana
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(titulo)
        self.dialog.geometry("500x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Centrar ventana
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"500x300+{x}+{y}")
        
        self.crear_interfaz()
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancelar)
    
    def crear_interfaz(self):
        """Crea la interfaz del selector"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        titulo = ttk.Label(main_frame, text="Seleccionar Paralelo", font=("Arial", 14, "bold"))
        titulo.pack(pady=(0, 20))
        
        # Lista de paralelos
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.listbox = tk.Listbox(list_frame, font=("Arial", 10))
        scrollbar_list = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar_list.set)
        
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_list.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Seleccionar", command=self.seleccionar).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cancelar", command=self.cancelar).pack(side=tk.LEFT, padx=10)
        
        # Cargar paralelos
        self.cargar_paralelos()
        
        # Doble click para seleccionar
        self.listbox.bind('<Double-1>', lambda e: self.seleccionar())
    
    def cargar_paralelos(self):
        """Carga los paralelos en la lista"""
        try:
            materias = MateriaManager.listar_materias()
            self.paralelos_data = []
            
            for materia in materias:
                paralelos = ParaleloManager.listar_paralelos_por_materia(materia.id)
                for paralelo in paralelos:
                    texto = f"{materia.sigla} - Paralelo {paralelo.paralelo} ({paralelo.contar_estudiantes()} estudiantes)"
                    self.listbox.insert(tk.END, texto)
                    self.paralelos_data.append(paralelo.id)
            
            if self.paralelos_data:
                self.listbox.select_set(0)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar paralelos: {e}")
    
    def seleccionar(self):
        """Selecciona el paralelo"""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un paralelo")
            return
        
        index = selection[0]
        paralelo_id = self.paralelos_data[index]
        
        self.resultado = paralelo_id
        self.dialog.destroy()
        
        if self.callback:
            self.callback(paralelo_id)
    
    def cancelar(self):
        """Cancela la selección"""
        self.dialog.destroy()
        if self.callback:
            self.callback(None)

def main():
    """Función principal de la aplicación desktop"""
    try:
        app = MainDesktopApp()
        app.ejecutar()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")

if __name__ == "__main__":
    main()