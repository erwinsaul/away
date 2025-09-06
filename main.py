#!/usr/bin/env python
"""
Away - Sistema de Gestión de Laboratorio
"""

import sys
import os

# Agregar el directorio de Away al path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def mostrar_menu_interfaces():
    """ Muestra el menú para elegir interfaz """
    print("="*60)
    print("     AWAY - SISTEMA DE GESTIÓN DE LABORATORIOS")
    print("="*60)
    print()
    print("Seleccione la interfaz que desea usar:")
    print("1. Consola")
    print("2. Textual User Interface")
    print("3. Desktop")
    print("4. Web")
    print()
    print("0. Salir")
    print("-"*60)


def ejecutar_constal():
    """ Ejecuta la interfaz de consola """
    try:
        from interfaces.consola import main as consola_main
        consola_main()
    except Exception as e:
        print(f"[ERROR] al iniciar la interfaz de consola: {e}")

def ejecutar_tui():
    """ Ejecuta la interfaz TUI """

    try:
        from interfaces.tui_app import main as tui_main
        tui_main()
    except ImportError:
        print("[ERROR] Error: Textual no está instalado")
        print("Instale Textual con: pip install textual")
    except Exception as e:
        print(f"[ERROR] al iniciar la interfaz TUI: {e}")

def ejecutar_desktop():
    """ Ejecuta la interfaz Desktop """
    try:
        from interfaces.desktop_app import main as desktop_main
        desktop_main()
    except ImportError as e:
        print("[ERROR] Error: Dependencias desktop no disponibles: {e}")
        print("Instale dependencias con: pip install -r requirements.txt")
    except Exception as e:
        print(f"[ERROR] al iniciar la interfaz Desktop: {e}")

def ejecutar_web():
    """ Ejecuta la interfaz Web """
    try:
        import subprocess
        import sys

        print("Iniciando servidor web en http://localhost:8501")
        print("Para salir, presione Ctrl+C")
        subprocess.run([
            sys.executable,
            "-m", "streamlit", "run", "interfaces/web_app.py"
        ])
    
    except ImportError:
        print("[ERROR] Error: Streamlit no está instalado")
        print("Instale Streamlit con: pip install streamlit")
    except KeyboardInterrupt:
        print("\nServidor web detenido")
    except Exception as e:
        print(f"[ERROR] al iniciar el servidor web: {e}")

def main():
    """ Función principal de Away """
    try:
        while True:
            mostrar_menu_interfaces()
            opcion = input("Seleccione una opción (1-4, 0 para salir):").strip()

            if opcion == "1":
                print("\nIniciando interfaz de consola...")
                ejecutar_constal()
            elif opcion == "2":
                print("\nIniciando interfaz TUI...")
                ejecutar_tui()
            elif opcion == "3":
                print("\nIniciando interfaz Desktop...")
                ejecutar_desktop()
            elif opcion == "4":
                print("\nIniciando interfaz Web...")
                ejecutar_web()
            elif opcion == "0":
                print("\nGracias por usar Away - Sistema de Gestión de Laboratorios!")                
                break
            else:
                print("[ERROR] Opción no válida.")
                input("Presione Enter para volver al menú...")
    except KeyboardInterrupt:
        print("\nGracias por usar Away - Sistema de Gestión de Laboratorios!")
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        print("Por favor, verifique que todas las dependencias estén instaladas.")

if __name__ == "__main__":
    main()

