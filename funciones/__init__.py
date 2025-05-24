import os
import sys
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .sistema_mesas import SistemaMesas
from .sistema_pedidos_mozos import SistemaPedidosMozos

def exportar_datos(sistema):
    """Exporta los datos del sistema a un archivo JSON"""
    try:
        if not os.path.exists('datos'):
            os.makedirs('datos')
            
        datos = {
            'mesas': sistema.mesas,
            'fecha_exportacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open('datos/sistema_restaurante.json', 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
            
        print("\n✅ Datos exportados exitosamente a 'datos/sistema_restaurante.json'")
        return True
    except Exception as e:
        print(f"\n❌ Error al exportar datos: {str(e)}")
        return False

def importar_datos(sistema):
    """Importa los datos del sistema desde un archivo JSON"""
    try:
        archivo = 'datos/sistema_restaurante.json'
        if not os.path.exists(archivo):
            print("\n❌ No se encontró el archivo de datos")
            return False
            
        with open(archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            
        sistema.mesas = datos['mesas']
        print("\n✅ Datos importados exitosamente")
        return True
    except Exception as e:
        print(f"\n❌ Error al importar datos: {str(e)}")
        return False

def iniciar_sistema():
    sistema = SistemaMesas()
    sistema_pedidos_mozos = SistemaPedidosMozos(sistema)
    
    while True:
        try:
            print("\n=== SISTEMA RESTAURANTE ===")
            print("1. Acceso Mozo")
            print("2. Resumen de Mesas")
            print("0. Salir")
            
            opcion = input("Seleccione una opción: ")
            
            if opcion == "1":
                interfaz_mozo(sistema_pedidos_mozos)
            elif opcion == "2":
                sistema_pedidos_mozos.mostrar_resumen_mesas()
            elif opcion == "0":
                break
            else:
                print("Opción inválida \n")
        except ValueError:
            print()

def interfaz_mozo(sistema_pedidos_mozos):
    print("\n=== ACCESO MOZO ===")
    nombre_mozo = input("Ingrese su nombre: ").strip()
    
    if not nombre_mozo:
        print("\n⚠️ Error: No puede dejar el nombre vacío.")
        return
        
    sistema_pedidos_mozos.mozo_actual = nombre_mozo
    
    while True:
        try:
            print(f"\n--- MENÚ MOZO: {nombre_mozo} ---")
            print("1. Ver menú y hacer pedido")
            print("2. Gestionar pedidos activos")
            print("3. Marcar pedido como entregado")
            print("4. Gestionar pagos")
            print("5. Reiniciar mesa")
            print("0. Volver")

            opcion = input("Seleccione una opción: ")

            if opcion == "0":
                return
            elif opcion == "1":
                sistema_pedidos_mozos.hacer_pedido()
            elif opcion == "2":
                sistema_pedidos_mozos.gestionar_pedidos_activos()
            elif opcion == "3":
                sistema_pedidos_mozos.marcar_pedido_entregado()
            elif opcion == "4":
                sistema_pedidos_mozos.gestionar_pagos()
            elif opcion == "5":
                sistema_pedidos_mozos.reiniciar_mesa()
            else:
                print("Opción no válida")
        except ValueError:
            print("Entrada inválida")

if __name__ == "__main__":
    iniciar_sistema() 