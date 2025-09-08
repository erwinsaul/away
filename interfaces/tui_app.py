"""
Interfaz TUI para Away - Sistema de Gestión de Laboratorios.
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Static, DataTable, Input, Button, Select, TextArea, Label, Checkbox
from textual.scree import Screen, ModalScreen
from textual.binding import Binding
from textual.message import Message

from models.database import inicializar_bd, cerrar_bd
from managers.materia_manager import MateriaManager
from managers.paralelo_manager import ParaleloManager
from managers.estudiante_manager import EstudianteManager
from managers.laboratorio_manager import LaboratorioManager
from managers.calificacion_manager import CalificacionManager
from utils.pdf_exporter import PDFExporter

class MenuPrincipal(Screen):
    """
    Pantalla principal de AWAY con dashboard y navegación.
    """

    BINDINGS = [
        Binding("1", "ir_materias", "Materias"),
        Binding("2", "ir_paralelos", "Paralelos"),
        Binding("3", "ir_estudiantes", "Estudiantes"),
        Binding("4", "ir_laboratorios", "Laboratorios"),
        Binding("5", "ir_calificaciones", "Calificaciones"),
        Binding("6", "ir_reportes", "Reportes y Exportación"),
        Binding("7", "ir_estadisticas", "Estadísticas"),
        Binding("0", "salir", "Salir")
    ]

    def compose(self) -> ComposeResult:
        """ Estructura de la pantalla principal """
        yield Header()
        yield Static(
            "AWAY - Sistema de Gestión de Laboratorios",
            classes="titulo-principal"
        )

        with Container(classes="panel-principal"):
            with Horizontal():
                with Vertical(classes="panl-info"):
                    yield Static("ESTADÍSTICAS GNERALES", classes="subtitulo")
                    yield Static("", id="stats-display")
                
                with Vertical(classes="panel-info"):
                    yield Static("MENU", classes="subtitulo")
                    yield Static(
                        "1. Materias\n"
                        "2. Paralelos\n"
                        "3. Estudiantes\n"
                        "4. Laboratorios\n"
                        "5. Calificaciones\n"
                        "6. Reportes y Exportación\n"
                        "7. Estadísticas\n"
                        "0. Salir",
                        id="menu-opciones"
                    )
                
            with Container(classes="tabla-datos"):
                yield Static("MATERIAS REGISTRADAS", classes="subtitulo")
                yield DataTable(id="tabla-materias")
        yield Footer()
    
    def on_ready(self):
        """ Se ejecuta cuando la pantalla esta lista """
        self.title = "AWAY - Sistema de Gestión de Laboratorios"
        self.actualizar_dashboard()
        self.cargar_tabla_materias()
    
    def actualizar_dashboard(self):
        """ Actualiza las estadísticas del dashboard """
        try: 
            stats = MateriaManager.obtener_estadisticas_generales()

            stats_text = f"""
            Resumen del Sistema
            Materias: {stats['total_materias']:3d}
            Paralelos : {stats['total_paralelos']:3d}
            Estudiantes: {stats['total_estudiantes']:3d}
            Laboratorios: {stats['total_laboratorios']:3d}
            """.strip()

            stats_display = self.query_one("#stats-display", Static)
            stats_display.update(stats_text)
        except Exception as e:
            stats_display = self.query_one("#stats-display", Static)
            stats_display.update(f"Error al cargar estadísticas: {e}")
    
    def cargar_tabla_materias(self):
        """ Carga la tabla de materias en el Dashboard """
        try:
            tabla = self.query_one("#tabla-materias", DataTable)
            tabla.clear(columns=True)

            tabla.add_columns("Sigla", "Materia", "Paralelos", "Estudiantes")
            materias = MateriaManager.listar_materias()
            for materia in materias:
                tabla.add_row(
                    materia.sigla,
                    materia.materia,
                    materia.contar_paralelos(),
                    materia.contar_estudiantes_total()
                )
        
        except Exception as e:
            tabla = self.query_one("#tabla-materias", DataTable)
            tabla.clear(columns=True)
            tabla.add_columns("Error")
            tabla.add_row(f"Error al cargar materias: {e}")
    
    def action_ir_materias(self):
        """ Ir a la pantalla de materias """
        self.app.push_screen(MateriasScreen())
    
    def action_ir_paralelos(self):
        """ Ir a la pantalla de paralelos """
        self.app.push_screen(ParalelosScreen())
    
    def action_ir_estudiantes(self):
        """ Ir a la pantalla de estudiantes """
        self.app.push_screen(EstudiantesScreen())
    
    def action_ir_laboratorios(self):
        """ Ir a la pantalla de laboratorios """
        self.app.push_screen(LaboratoriosScreen())
    
    def action_ir_calificaciones(self):
        """ Ir a la pantalla de calificaciones """
        self.app.push_screen(CalificacionesScreen())
    
    def action_ir_reportes(self):
        """ Ir a la pantalla de reportes y exportación """
        self.app.push_screen(ReportesScreen())
    
    def action_ir_estadisticas(self):
        """ Ir a la pantalla de estadísticas """
        self.app.push_screen(EstadisticasScreen())

    def action_salir(self):
        """ Cierra el Sistema """
        self.app.exit()

class MateriasScreen(Screen):
    """ Pantalla de gestión de materias """
    BINDINGS = [
        Binding("n", "nueva_materia", "Nueva"),
        Binding("e", "editar_materia", "Editar"),
        Binding("d", "eliminar_materia", "Eliminar"),
        Binding("r", "refrescar", "Refrescar"),
        Binding("escape", "volver", "Volver"),
    ]

    def compose(self) -> ComposeResult:
        """ Estructura de la pantalla de materias """
        yield Header()
        yield Static("GESTIÓN DE MATERIAS", classes="titulo-seccion")

        with Container(classes="contenedor-principal"):
            with Horizontal(classes="barra-botones"):
                yield Button("Nueva Materia", id="btn-nueva", variant="primary")
                yield Button("Editar", id="btn-ditar")
                yield Button("Eliminar", id="btn-eliminar", variant="error")
                yield Button("Refrescar", id="btn-refrescar")
            
            yield DataTable(id="tabla-materias", cursor_type="row")
        
        yield Footer()
    
    def on_ready(self):
        """ Incializa la pantalla """
        self.title = "AWAY - Gestón de Materias"
        self.cargar_materias()
    
    def cargar_materias(self):
        """ Carga las materias en la tabla """
        tabla = self.query_one("#tabla-materias", DataTable)
        tabla.clear(columns=True)

        tabla.add_columns("ID", "Sigla", "Materia", "Paralelos",  "Estudiantes")
        materias = MateriaManager.listar_materias()

        for materia in materias():
            tabla.add_row(
                str(materia.id),
                materia.sigla,
                materia.materia,
                str(materia.contar_paralelos()),
                str(materia.contar_estudiantes_total()),
                key=str(materia.id)
            )

    def on_button_pressed(self, event: Button.Pressed):
        """ Eventos de los botones """
        if event.button.id == "btn-nueva":
            self.action_nueva_materia()
        elif event.button.id == "btn-editar":
            self.action_editar_materia()
        elif event.button.id == "btn-eliminar":
            self.action_eliminar_materia()
        elif event.button.id == "btn-refrescar":
            self.cargar_materias()

    def action_nueva_materia(self):
        """ Nueva materia """
        self.app.push_screen(FormularioMateriaScreen(), self.callback_formulario)
    
    def action_editar_materia(self):
        """ Edita la materia seleccionada """
        tabla = self.query_one("#tabla-materias", DataTable)

        if tabla.cursor_row < 0:
            self.notify("Seleccione una materia", severity="warning")
            return
        
        row_key = tabla.get_row_at(tabla.cursor_row)
        materia_id = int(row_key[0])
        materia = MateriaManager.obtener_materia(materia_id)

        if materia:
            self.app.push_screen(FormularioMateriaScreen(materia), self.callback_formulario)

    def action_eliminar_materia(self):
        """ Elimina la materia seleccionada """
        tabla = self.query_one("#tabla-materias", DataTable)

        if tabla.cursor_row < 0:
            self.notify("Seleccione una materia", severity="warning")
            return
        
        row_key = tabla.get_row_at(tabla.cursor_row)
        materia_id = int(row_key[0])

        self.app.push_screen(ConfirmarEliminacionScreen("materia", materia_id), self.callback_eliminacion)

    def action_refrescar(self):
        """ Refresca la pantalla """
        self.cargar_materias()
        self.notify("Datos actualizados")
    
    def action_volver(self):
        """ Volver al menú principal """
        self.app.pop_screen()
    
    def callback_formulario(self, resultado):
        """ Callback del formulario de materia """
        if resultado:
            self.cargar_materias()
            self.notify("Materia creada", severity="success")
    
    def callback_eliminacion(self, confirmado):
        """ Callback de confirmación de eliminación """
        if confirmado:
            self.cargar_materias()
            self.notify("Materia eliminada", severity="success")

class ParalelosScreen(Screen):
    """ Pantalla de gestión de paralelos """
    BINDINGS = [
        Binding("n", "nuevo_paralelo", "Nuevo"),
        Binding("e", "editar_paralelo", "Editar"),
        Binding("d", "eliminar_paralelo", "Eliminar"),
        Binding("r", "refrescar", "Refrescar"),
        Binding("escape", "volver", "Volver"),
    ]

    def compose(self) -> ComposeResult:
        """ Estructura de la pantalla de paralelos """
        yield Header()

        yield Static("GESTIÓN DE PARALELOS", classes="titulo-seccion")

        with Container(classes="contenedor-principal"):
            with Horizontal(classes="barra-botones"):
                yield Select([("Seleccione materia...", None)], id="select-materia")
                yield Button("Nuevo Paralelo", id="btn-nuevo", variant="primary")
                yield Button("Editar", id="btn-editar")
                yield Button("Eliminar", id="btn-eliminar", variant="error")
            
            yield DataTable(id="tabla-paralelos", cursor_type="row")
        
        yield Footer()
    
    def on_ready(self):
        """ Inicializa la pantalla """
        self.title = "AWAY - Gestón de Paralelos"
        self.cargar_materias_select()
    
    def cargar_materias_select(self):
        """ Carga las materias en el select """
        select = self.query_one("#select-materia", Select)

        materias = MateriaManager.listar_materias()
        opciones = [("Seleccione materia...", None)]
        opciones.extend([(f"{materia.sigla} - {materia.materia}", materia.id) for materia in materias])
        select.set_options(opciones)
    
    def cargar_paralelos(self, materia_id):
        """ Carga los paralelos de una materia """
        tabla = self.query_one("#tabla-paralelos", DataTable)
        tabla.clear(columns=True)
        tabla.add_columns("ID", "Paralelo", "Docente", "Estudiantes", "Grupos")

        paralelos = ParaleloManager.listar_paralelos_por_materia(materia_id)

        for paralelo in paralelos:
            tabla.add_row(
                str(paralelo.id),
                paralelo.paralelo,
                paralelo.docente_teoria,
                str(paralelo.contar_estudiantes()),
                str(paralelo.contar_grupos()),
                key=str(paralelo.id)
            )
    
    def on_select_changed(self, event: Select.Changed):
        """ Maneja cambio de materia """
        if event.value and event.value != None:
            self.cargar_paralelos(event.value)
    
    def on_button_pressed(self, event: Button.Pressed):
        """ Maneja eventos de los botones """
        if event.button.id == "btn-nuevo":
            self.action_nuevo_paralelo()
        elif event.button.id == "btn-editar":
            self.action_editar_paralelo()
        elif event.button.id == "btn-eliminar":
            self.action_eliminar_paralelo()
    
    def action_nuevo_paralelo(self):
        """ Nuevo Paralelo """
        select = self.query_one("#select-materia", Select)

        if not select.value:
            self.notify("Seleccione una materia", severity="warning")
            return
        
        self.app.push_screen(FormularioParaleloScreen(select.value), self.callback_formulario)
    
    def action_editar_paralelo(self):
        """ Edita paralelo seleccionado """
        tabla = self.query_one("#tabla-paralelos", DataTable)
        if tabla.cursor_row < 0:
            self.notify("Seleccione un paralelo para editar", severity="warning")
            return
        
        row_key = tabla.get_row_at(tabla.cursor_row)
        paralelo_id = int(row_key[0])

        paralelo = ParaleloManager.obtener_paralelo(paralelo_id)
        if paralelo:
            self.app.push_screen(FormularioParaleloScreen(paralelo.id_materia.id, paralelo), self.callback_formulario)

    def action_eliminar_paralelo(self):
        """ Elimina paralelo seleccionado """
        tabla = self.query_one("#tabla-paralelos", DataTable)
        if tabla.cursor_row < 0:
            self.notify("Seleccione un paralelo para eliminar", severity="warning")
            return
        
        row_key = tabla.get_row_at(tabla.cursor_row)
        paralelo_id = int(row_key[0])
        self.app.push_screen(ConfirmarEliminacionScreen("paralelo", paralelo_id), self.callback_eliminacion)
    
    def action_cambiar_materia(self):
        """ Enfoca el selector de materia """
        select = self.query_one("#select-materia", Select)
        select.focus()
    
    def action_refrescar(sel):
        """ Refresca los datos """
        select = self.query_one("#select-materia", Select)
        if select.value:
            self.cargar_paralelos(select.value)
        self.notify("Datos actualizados")
    
    def action_volver(self):
        """ Vuelve al menú principal """
        self.app.pop_screen()
    
    def callback_formulario(self, resultado):
        """ Callback del formulario """
        if resultado:
            select = self.query_one("#select-materia", Select)
            if select.value:
                self.cargar_paralelos(select.value)
            self.notify("Paralelo creado", severity="success")
    
    def callback_eliminacion(self, confirmado):
        """ Callback de eliminación """
        if confirmado:
            select = self.query_one("#select-materia", Select)
            if select.value:
                self.cargar_paralelos(select.value)
            self.notify("Paralelo eliminado", severity="success")

class EstudiantesScreen(Screen):
    """ Pantall de gestión de estudiantes """
    BINDINGS = [
        Binding("n", "nuevo_estudiante", "Nuevo"),
        Binding("e", "editar_estudiante", "Editar"),
        Binding("d", "eliminar_estudiante", "Eliminar"),        
        Binding("r", "refrescar", "Refrescar"),
        Binding("escape", "volver", "Volver"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()

        yield Static("GESTIÓN DE ESTUDIANTES", classes="titulo-seccion")

        with Container(classes="contenedor-principal"):
            with Horizontal(classes="barra-botones"):
                yield Select([("Seleccione paralelo...", None)], id="select-paralelo")
                yield Button("Nuevo Estudiante", id="btn-nuevo", variant="primary")
                yield Button("Editar", id="btn-editar")
                yield Button("Eliminar", id="btn-eliminar", variant="error")
            
            yield DataTable(id="tabla-estudiantes", cursor_type="row")
        
        yield Footer()
    
    def on_ready(self):
        """ Inicializa la pantalla """
        self.title = "AWAY - Gestón de Estudiantes"
        self.cargar_paralelos_select()
    
    def cargar_paralelos_select(self):
        """ Carga paralelos en el selector """
        select = self.query_one("#select-paralelo", Select)
        materias = MateriaManager.listar_materias()

        opciones = [("Seleccione paralelo...", None)]

        for materia in materias:
            paralelos = ParaleloManager.listar_paralelos_por_materia(materia.id)
            for paralelo in paralelos:
                opciones.append((f"{materia.sigla} - {paralelo.paralelo}", paralelo.id))
        
        select.set_options(opciones)
    
    def cargar_estudiantes(self, paralelo_id):
        """ Carga estudiantes de un paralelo """
        tabla = self.query_one("#tabla-estudiantes", DataTable)
        tabla.clear(columns=True)

        tabla.add_columns("ID", "CI","Nombre", "Grupo", "Promedio")

        estudiantes = EstudianteManager.listar_estudiantes_por_paralelo(paralelo_id)

        for estudiante in estudiantes:
            tabla.add_row(
                str(estudiante.id),
                estudiante.ci,
                estudiante.nombre,
                estudiante.grupo or "Sin asignar",
                f"{estudiante.promedio_calificaciones():.2f}",
                key=str(estudiante.id)
            )

    def on_select_changed(self, event: Select.Changed):
        """ Maneja cambio de paralelo """
        if event.value and event.value != None:
            self.cargar_estudiantes(event.value)
    
    def on_button_pressed(self, event: Button.Pressed):
        """ Maneja eventos de los botones """
        if event.button.id == "btn-nuevo":
            self.action_nuevo_estudiante()
        elif event.button.id == "btn-editar":
            self.action_editar_estudiante()
        elif event.button.id == "btn-eliminar":
            self.action_eliminar_estudiante()
    
    def action_nuevo_estudiante(self):
        """ Nuevo estudiante """
        select = self.query_one("#select-paralelo", Select)
        if not select.value:
            self.notify("Seleccione un paralelo", severity="warning")
            return
        
        self.app.push_screen(FormularioEstudianteScreen(select.value), self.callback_formulario)

    def action_editar_estudiante(self):
        """ Editar Estudiante Seleccionado """
        tabla = self.query_one("#tabla-estudiantes", DataTable)

        if tabla.cursor_row < 0:
            self.notify("Seleccione un estudiante para editar", severity="warning")
            return
        
        row_key = tabla.get_row_at(tabla.cursor_row)
        estudiante_id = int(row_key[0])

        estudiante = EstudianteManager.obtener_estudiante(estudiante_id)
        if estudiante:
            self.app.push_screen(FormularioEstudianteScreen(estudiante.id_paralelo.id, estudiante), self.callback_formulario)
    
    def action_eliminar_estudiante(self):
        """ Eliminar estudiante seleccionado """
        tabla = self.query_one("#tabla-estudiantes", DataTable)

        if tabla.cursor_row < 0:
            self.notify("Seleccione un estudiante para eliminar", severity="warning")
            return
        
        row_key = tabla.get_row_at(tabla.cursor_row)
        estudiante_id = int(row_key[0])

        self.app.push_screen(ConfirmarEliminacionScreen("estudiante", estudiante_id), self.callback_eliminacion)
    
    def action_refrescar(self):
        """ Refrescar los datos """
        select = self.query_one("#select-paralelo", Select)
        if select.value:
            self.cargar_estudiantes(select.value)
        self.notify("Datos actualizados")
    
    def action_volver(self):
        """ Volver al menú principal """
        self.app.pop_screen()
    
    def callback_formulario(self, resultado):
        """ Callback del formulario """
        if resultado:
            select = self.query_one("#select-paralelo", Select)
            if select.value:
                self.cargar_estudiantes(select.value)
            self.notify("Estudiante guardado exitosamente", severity="success")
    
    def callback_eliminacion(self, confirmado):
        """ Callback eliminación """
        if confirmado:
            select = self.query_one("#select-paralelo", Select)
            if select.value:
                self.cargar_estudiantes(select.value)
            self.notify("Estudiante eliminado exitosamente", severity="success")
    
class LaboratoriosScreen(Screen):
    """ Pantalla de laboratorios """
    BINDINGS = [
        Binding("n", "nuevo_laboratorio", "Nuevo"),
        Binding("e", "editar_laboratorio", "Editar"),
        Binding("d", "eliminar_laboratorio", "Eliminar"),
        Binding("m", "cambiar_materia", "Cambiar Materia"),
        Binding("r", "refrescar", "Refrescar"),
        Binding("escape", "volver", "Volver"),
    ]

    def compose(self) -> ComposeResult:

        yield Header()
        yield Static("GESTIÓN DE LABORATORIOS", classes="titulo-seccion")

        with Container(classes="contenedor-principal"):
            with Horizontal(classes="barra-botones"):
                yield Select([("Seleccione materia...", None)], id="select-materia")
                yield Button("Nuevo Laboratorio", id="btn-nuevo", variant="primary")
                yield Button("Editar", id="btn-editar")
                yield Button("Eliminar", id="btn-eliminar", variant="error")
            
            yield DataTable(id="tabla-laboratorios", cursor_type="row")

        yield Footer()
    
    def on_ready(self):
        """ Inicializa la pantalla """
        self.title = "AWAY - Gestón de Laboratorios"
        self.cargar_materias_select()
    
    def cargar_materias_select(self):
        """ Carga materias en el selector """
        select = self.query_one("#select-materia", Select)
        materias = MateriaManager.listar_materias()

        opciones = [("Seleccione materia...", None)]
        opciones.extend([(f"{materia.sigla} - {materia.materia}", materia.id) for materia in materias])

        select.set_options(opciones)
    
    def cargar_laboratorios(self, materia_id):
        """ Carga laboratorios de una materia """
        tabla = self.query_one("#tabla-laboratorios", DataTable)
        tabla.clear(columns=True)
        tabla.add_columns("ID", "Num", "Titulo", "Puntaje", "Calificaciones")

        laboratorios = LaboratorioManager.listar_laboratorios_por_materia(materia_id)

        for laboratorio in laboratorios:
            tabla.add_row(
                str(laboratorio.id),
                str(laboratorio.num),
                laboratorio.titulo,
                f"{laboratorio.puntaje_maximo:.2f}",
                str(laboratorio.contar_calificaciones()),
                key=str(laboratorio.id)
            )
        
    def on_select_changed(self, event: Select.Changed):
        """ Maneja cambio de materia """
        if event.value and event.value != None:
            self.cargar_laboratorios(event.value)
    
    def on_button_pressed(self, event: Button.Pressed):
        """ Maneja eventos de botones """
        if event.button.id == "btn-nuevo":
            self.action_nuevo_laboratorio()
        elif event.button.id == "btn-editar":
            self.action_editar_laboratorio()
        elif event.button.id == "btn-eliminar":
            self.action_eliminar_laboratorio()
    
    def action_nuevo_laboratorio(self):
        """ Abre formulario para nuevo laboratorio """
        select = self.query_one("#select-materia", Select)

        if not select.value:
            self.notify("Seleccione una materia", severity="warning")
            return
        
        self.app.push_screen(FormularioLaboratorioScreen(select.value), self.callback_formulario)
    
    def action_editar_laboratorio(self):
        """ Edite laboratorio seleccionado """
        tabla = self.query_one("#tabla-laboratorios", DataTable)
        if tabla.cursor_row < 0:
            self.notify("Seleccione un laboratorio para editar", severity="warning")
            return
        
        row_key = tabla.get_row_at(tabla.cursor_row)
        laboratorio_id = int(row_key[0])
        laboratorio = LaboratorioManager.obtener_laboratorio(laboratorio_id)

        if laboratorio:
            self.app.push_screen(FormularioLaboratorioScreen(laboratorio.id_materia.id, laboratorio), self.callback_formulario)
    
    def action_eliminar_laboratorio(self):
        """ Elimina laboratorio seleccionado """
        tabla = self.query_one("#tabla-laboratorios", DataTable)

        if tabla.cursor_row < 0:
            self.notify("Seleccione un laboratorio para eliminar", severity="warning")
            return
        
        row_key = tabla.get_row_at(tabla.cursor_row)
        laboratorio_id = int(row_key[0])

        self.app.push_screen(ConfirmarEliminacionScreen("laboratorio", laboratorio_id), self.callback_eliminacion)
    
    def action_cambiar_materia(self):
        """ Enfoca el selector de materia """
        select = self.query_one("#select-materia", Select)
        select.focus()
    
    def action_refrescar(self):
        """ Refresca los datos """
        select = self.query_one("#select-materia", Select)
        if select.value:
            self.cargar_laboratorios(select.value)
        self.notify("Datos actualizados")
    
    def action_volver(self):
        """ Vuelve al menú principal """
        self.app.pop_screen()
    
    def callback_formulario(self, resultado):
        """ Callback Formulario """
        if resultado:
            select = self.query_one("#select-materia", Select)
            if select.value:
                self.cargar_laboratorios(select.value)
            self.notify("Laboratorio guardado exitosamente", severity="success")
    
    def callback_eliminacion(self, confirmado):
        """ Callback de eliminación """
        if confirmado:
            select = self.query_one("#select-materia", Select)
            if select.value:
                self.cargar_laboratorios(select.value)
            self.notify("Laboratorio eliminado exitosamente", severity="success")

class CalificacionesScreen(Screen):
    """ Pantalla de gestión de calificaciones """
    BINDINGS = [
        Binding("n", "nuevo_calificacion", "Nueva"),
        Binding("e", "editar_calificacion", "Editar"),
        Binding("d", "eliminar_calificacion", "Eliminar"),
        Binding("l", "cambiar_laboratorio", "Cambiar Laboratorio"),
        Binding("r", "refrescar", "Refrescar"),
        Binding("escape", "volver", "Volver"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("GESTIÓN DE CALIFICACIONES", classes="titulo-seccion")

        with Container(classes="contenedor-principal"):
            with Horizontal(classes="barra-botones"):
                yield Select([("Seleccione laboratorio...", None)], id="select-laboratorio")
                yield Button("Nueva Calificacion", id="btn-nuevo", variant="primary")
                yield Button("Editar", id="btn-editar")
                yield Button("Eliminar", id="btn-eliminar", variant="error")
            
            yield DataTable(id="tabla-calificaciones", cursor_type="row")
        
        yield Footer()
    
    def on_ready(self):
        """ Inicializa la pantalla """
        self.title = "AWAY - Gestón de Calificaciones"
        self.cargar_laboratorios_select()

    def cargar_laboratorios_select(self):
        """ Carga laboratorios en el selector """
        select = self.query_one("#select-laboratorio", Select)
        materias = MateriaManager.listar_materias()

        opciones = [("Seleccione laboratorio...", None)]
        
        for materia in materias:
            laboratorios = LaboratorioManager.listar_laboratorios_por_materia(materia.id)
            for laboratorio in laboratorios:
                opciones.append((f"{materia.sigla} - {laboratorio.numero} - {laboratorio.titulo}", laboratorio.id))
        
        select.set_options(opciones)
    
    def cargar_calificaciones(self, laboratorio_id):
        """ Carga calificaciones de un laboratorio """
        tabla = self.query_one("#tabla-calificaciones", DataTable)
        tabla.clear(columns=True)

        tabla.add_columns("ID", "CI", "Estudiante", "Calificacion", "Estado")

        calificaciones = CalificacionManager.listar_calificaciones_por_laboratorio(laboratorio_id)

        for calificacion in calificaciones:
            estudiante = calificacion.id_estudiante
            nota_str = f"{calificacion.calificacion:.2f}" if calificacion.calificacion else "Sin nota"
            estado = calificacion.estado_aprobacion()

            tabla.add_row(
                str(calificacion.id),
                estudiante.ci,
                estudiante.nombre,
                nota_str,
                estado,
                key=str(calificacion.id)
            )

        def on_select_changed(self, event: Select.Changed):
            """ Maneja cambio de Laboratorio """
            if event.value and event.value != None:
                self.cargar_calificaciones(event.value)
        
        def on_button_pressed(self, event: Button.Pressed):
            """ Maneja eventos de botones """
            if event.button.id == "btn-nuev0":
                self.action_nueva_calificacion()
            elif event.button.id == "btn-editar":
                self.action_editar_calificacion()
            elif event.button.id == "btn-eliminar":
                self.action_eliminar_calificacion()
        
        def action_nueva_calificacion(self):
            """ Abre formulario para nueva calificación """
            select = self.query_one("#select-laboratorio", Select)

            if not select.value:
                self.notify("Seleccione un laboratorio", severity="warning")
                return
            
            self.app.push_screen(FormularioCalificacionScreen(select.value), self.callback_formulario)
        
        def action_editar_calificacion(self):
            """ Edite calificacion seleccionado """
            tabla = self.query_one("#tabla-calificaciones", DataTable)
            if tabla.cursor_row < 0:
                self.notify("Seleccione una calificacion para editar", severity="warning")
                return

            row_key = tabla.get_row_at(tabla.cursor_row)
            calificacion_id = int(row_key[0])

            select = self.query_one("#select-laboratorio", Select)

            self.app.push_screen(FormularioCalificacionScreen(select.value, calificacion_id), self.callback_formulario)
        
        def action_eliminar_calificacion(self):
            """ Elimina calificacion seleccionado """
            
            tabla = self.query_one("#tabla-calificaciones", DataTable)

            if tabla.cursor_row < 0:
                self.notify("Seleccione una calificacion para eliminar", severity="warning")
                return
            
            row_key = tabla.get_row_at(tabla.cursor_row)
            calificacion_id = int(row_key[0])

            self.app.push_screen(ConfirmarEliminacionScreen("calificacion", calificacion_id), self.callback_eliminacion)

        def action_cambiar_laboratorio(self):
            """ Enfoca el selector de Laboratorio """
            select = self.query_one("#select-laboratorio", Select)
            select.focus()
        
        def action_refrescar(self):
            """ Refresca los datos """
            select = self.query_one("#select-laboratorio", Select)
            if select.value:
                self.cargar_calificaciones(select.value)
            self.notify("Datos actualizados")
        
        def action_volver(self):
            """ Vuelve al menú principal """
            self.app.pop_screen()
        
        def callback_formulario(self, resultado):
            """ Callback del Formulario """
            if resultado:
                select = self.query_one("#select-laboratorio", Select)
                if select.value:
                    self.cargar_calificaciones(select.value)
                self.notify("Calificacion guardada exitosamente", severity="success")
        
        def callback_eliminacion(self, confirmado):
            """ Callback de eliminación """
            if confirmado:
                select = self.query_one("#select-laboratorio", Select)
                if select.value:
                    self.cargar_calificaciones(select.value)
                self.notify("Calificacion eliminada", severity="success")

class ReportesScreen(Screen):
    """ Pantalla de reportes y exportación """
    BINDINGS = [
        Binding("p", "generar_pdf", "Generar PDF"),
        Binding("m", "mostrar_matriz", "Matriz"),
        Binding("escape", "volver", "Volver"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()

        yield Static("REPORTES Y EXPORTACIÓN", classes="titulo-seccion")

        with Container(classes="contenedor-principal"):
            with Horizontal(classes="barra-botones"):
                yield Select([("Seleccione materia...", None)], id="select-paralelo")
                yield Button("Generar PDF", id="btn-pdf", variant="primary")
                yield Button("Mostrar Matriz", id="btn-matriz")
            
            yield Static("Seleccione un paralelo para generar el PDF", id="info_reportes")
        
        yield Footer()

    def on_ready(self):
        """ Inicializa la pantalla """
        self.title = "AWAY - Reportes y Exportación"
        self.cargar_paralelos_select()
    
    def cargar_paralelos_select(self):
        """ Carga paralelos en el selector """

        select = self.query_one("#select-paralelo", Select)
        materias = MateriaManager.listar_materias()

        opciones = [("Seleccione materia...", None)]

        for materia in materias:
            paralelos = ParaleloManager.listar_paralelos_por_materia(materia.id)
            for paralelo in paralelos:
                opciones.append((f"{materia.sigla} - Paralelo {paralelo.paralelo}", paralelo.id))
        
        select.set_options(opciones)
    
    def on_button_pressed(self, event: Button.Pressed):
        """ Maneja eventos de botones """

        if event.button.id == "btn-pdf":
            self.action_generar_pdf()
        elif event.button.id == "btn-matriz":
            self.action_mostrar_matriz()
    
    def action_generar_pdf(self):
        """ Genera reporte PDF """
        select = self.query_one("#select-paralelo", Select)

        if not select.value:
            self.notify("Seleccione un paralelo", severity="warning")
            return
        
        try:
            archivo = PDFExporter.generar_reporte_paralelo(select.value)
            if archivo:
                self.notify(f"Reporte generado: {archivo}", severity="success")
            else:
                self.notify("Error al generar el PDF", severity="error")
        except Exception as e:
            self.notify(f"Error al generar el PDF: {e}", severity="error")
    
    def action_mostrar_matriz(self):
        """ Muestra matriz de calificaciones """
        select = self.query_one("#select-paralelo", Select)

        if not select.value:
            self.notify("Seleccione un paralelo", severity="warning")
            return
        
        self.app.push_screen(MatrizScreen(select.value))

    def action_volver(self):
        """ Vuelve al menú principal """
        self.app.pop_screen()

class EstadisticasScreen(Screen):
    """ Pantalla de estadísticas """
    BINDINGS = [
        Binding("escape", "volver", "Volver"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()

        yield Static("ESTADÍSTICAS GENERALES", classes="titulo-seccion")

        with ScrollableContainer():
            yield Static("", classes="stats-content")
        
        yield Footer()

    def on_ready(self):
        """ Inicializa la pantalla """
        selt.title = "AWAY - Estadísticas Generales"
        self.cargar_estadisticas_generales()
    
    def cargar_estadisticas_generales(self):
        """ Carga las estadísticas generales """

        try:
            stats = MateriaManager.obtener_estadisticas_generales()
            materias = MateriaManager.listar_materias()

            contenido = f"""
            RESUMEN GENERAL DEL SISTEMA
            {"=" * 60}
            Total de materias: {stats['total_materias']:3d}
            Total de paralelos: {stats['total_paralelos']:3d}
            Total de estudiantes: {stats['total_estudiantes']:3d}
            Total de laboratorios: {stats['total_laboratorios']:3d}
            Promedio de paralelos por materia: {stats['promedio_paralelos_por_materia']:5.2f}
            Promedio de estudiantes por materia: {stats['promedio_estudiantes_por_materia']:5.2f}
            
            DETALLE POR MATERIA
            {'=' * 50}
            Sigla      | Materia        | Paralelos      | Estudiantes        |Labs
            {"-" * 50}
            """

            for materia in materias:
                stats_materia = materia.estadisticas_completas()
                contenido = contenido + f"{stats_materia['sigla']:10s} | {materia.materia[:23]:23s} | {stats_materia['paralelos']:3d} | {stats_materia['estatudiante_total']:3d} | {stats_materia['laboratorios']:3d}\n"

            stats_display = self.query_one("#stats-content", Static)
            stats_display.update(contenido)

        except Excepcion as e:
            stats_display = self.query_one("#stats-content", Static)
            stats_display.update(f"Error al cargar estadísticas: {e}")

    def action_volver(self):
        """ Vuelve al menú principal """
        self.app.pop_screen()

# ========================================================================
# FORMULARIOS MODALES
# ========================================================================

    


def main():
    """ Funcion principal """
    print("Iniciando AWAY")
    print("Use las teclas de navegacion indicadas en cada pantalla")
    app = LaboratoriosAppTui()

    try:
        app.run()
    except KeyboardInterrupt:
        print("Saliendo del Sistema")
        app.exit()
    except Exception as e:
        print(f"Error: {e}")
        app.exit()


if __name__ == "__main__":
    main()



    