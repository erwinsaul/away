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



    