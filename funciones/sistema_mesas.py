import json
import os
from datetime import datetime

# Configuración de rutas
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '../data')
HISTORIAL_DIR = os.path.join(DATA_DIR, 'historial_pagos')
MESAS_JSON = os.path.join(DATA_DIR, 'mesas.json')
MESAS_TEMP_JSON = MESAS_JSON + ".temp" # Archivo temporal
MENU_JSON = os.path.join(DATA_DIR, 'menu.json')

class SistemaMesas:
    def __init__(self):
        self.mesas = {}
        self.menu = {}
        self.cargar_mesas()
        self.cargar_menu()
        
    def cargar_mesas(self):
        """Carga las mesas desde el archivo JSON"""
        try:
            if os.path.exists(MESAS_JSON):
                with open(MESAS_JSON, 'r', encoding='utf-8') as f:
                    self.mesas = json.load(f)
            else:
                self.inicializar_mesas()
        except Exception as e:
            print(f"Error al cargar mesas: {str(e)}")
            self.inicializar_mesas()

    def cargar_menu(self):
        """Carga el menú desde el archivo JSON"""
        try:
            if os.path.exists(MENU_JSON):
                with open(MENU_JSON, 'r', encoding='utf-8') as f:
                    self.menu = json.load(f)
            else:
                self.inicializar_menu()
        except Exception as e:
            print(f"Error al cargar menú: {str(e)}")
            self.inicializar_menu()

    def inicializar_mesas(self):
        """Inicializa las mesas con valores predeterminados"""
        self.mesas = {
            '1': [{
                'nombre': 'Mesa 1',
                'estado': 'libre',
                'cliente_1': {
                    'pedidos': [],
                    'contador_pedidos': 0
                }
            }],
            '2': [{
                'nombre': 'Mesa 2',
                'estado': 'libre',
                'cliente_1': {
                    'pedidos': [],
                    'contador_pedidos': 0
                }
            }],
            '3': [{
                'nombre': 'Mesa 3',
                'estado': 'libre',
                'cliente_1': {
                    'pedidos': [],
                    'contador_pedidos': 0
                }
            }],
            '4': [{
                'nombre': 'Mesa 4',
                'estado': 'libre',
                'cliente_1': {
                    'pedidos': [],
                    'contador_pedidos': 0
                }
            }],
            '5': [{
                'nombre': 'Mesa 5',
                'estado': 'libre',
                'cliente_1': {
                    'pedidos': [],
                    'contador_pedidos': 0
                }
            }],
            '6': [{
                'nombre': 'Barra interior',
                'estado': 'libre',
                'cliente_1': {
                    'pedidos': [],
                    'contador_pedidos': 0
                }
            }],
            '7': [{
                'nombre': 'Barra exterior',
                'estado': 'libre',
                'cliente_1': {
                    'pedidos': [],
                    'contador_pedidos': 0
                }
            }]
        }
        self.guardar_mesas()
        
    def guardar_mesas(self):
        """Guarda las mesas en el archivo JSON"""
        try:
            with open(MESAS_TEMP_JSON, 'w', encoding='utf-8') as f_temp:
                json.dump(self.mesas, f_temp, indent=2, ensure_ascii=False)
            os.replace(MESAS_TEMP_JSON, MESAS_JSON)
        except Exception as e:
            print(f"⚠️ Error al guardar mesas (escritura atómica): {e}")
            if os.path.exists(MESAS_TEMP_JSON):
                try:
                    os.remove(MESAS_TEMP_JSON)
                except OSError as e_remove:
                    print(f"⚠️ Error al eliminar archivo temporal fallido: {e_remove}")
            return False
        return True

    def inicializar_menu(self):
        """Inicializa el menú con valores predeterminados"""
        self.menu = {
            'platos': {
                'entrada': {
                    'entradas': [
                        {
                            'id': 'entrada_1',
                            'nombre': 'Ensalada César',
                            'descripcion': 'Lechuga romana, pollo a la parrilla, crutones, queso parmesano y aderezo césar',
                            'precio': 1200,
                            'dietas': ['vegetariano', 'sin gluten']
                        }
                    ]
                },
                'principal': {
                    'carnes': [
                        {
                            'id': 'carne_1',
                            'nombre': 'Bife de Chorizo',
                            'descripcion': '300g con papas fritas y ensalada',
                            'precio': 2500,
                            'dietas': []
                        }
                    ]
                },
                'postre': {
                    'postres': [
                        {
                            'id': 'postre_1',
                            'nombre': 'Tiramisú',
                            'descripcion': 'Clásico postre italiano con café y mascarpone',
                            'precio': 800,
                            'dietas': ['vegetariano']
                        }
                    ]
                }
            }
        }
        self.guardar_menu()

    def guardar_menu(self):
        """Guarda el menú en el archivo JSON"""
        try:
            with open(MENU_JSON, 'w', encoding='utf-8') as f:
                json.dump(self.menu, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Error al guardar menú: {e}")
            return False
        return True

    def obtener_mesa(self, mesa_id):
        """Obtiene la información de una mesa por su ID."""
        try:
            mesa_id = str(mesa_id)
            mesa_data = self.mesas.get(mesa_id)
            if not mesa_data:
                print(f"⚠️ Error: Mesa {mesa_id} no encontrada")
                return None
            return mesa_data
        except Exception as e:
            print(f"⚠️ Error al obtener mesa {mesa_id}: {str(e)}")
            return None

    def mostrar_menu_completo(self):
        """Muestra el menú completo y devuelve la lista de todos los platos."""
        etapas = sorted(self.menu['platos'].keys())
        todos_platos = []
        contador_global = 1

        print("\n=== MENÚ COMPLETO ===")

        for etapa in etapas:
            print(f"\n--- {etapa.upper()} ---")
            for categoria, platos in sorted(self.menu['platos'][etapa].items()):
                print(f"\n  {categoria.capitalize()}:")
                for plato in platos:
                    todos_platos.append({'etapa': etapa, 'categoria': categoria, 'plato': plato, 'index': contador_global})
                    dietas = ", ".join(plato.get('dietas', []))
                    print(f"  {contador_global}. {plato['nombre']} - ${plato['precio']}")
                    print(f"      {plato.get('descripcion', '')}")
                    if dietas:
                        print(f"      🏷️ {dietas}")
                    contador_global += 1
        return todos_platos


    def obtener_mesas(self):
        """Obtiene todas las mesas disponibles."""
        return {mesa_id: mesa_data[0] for mesa_id, mesa_data in self.mesas.items()}

    def ocupar_mesa(self, mesa_id):
        """Ocupa una mesa."""
        if mesa_id not in self.mesas:
            print(f"⚠️ Error: Mesa {mesa_id} no encontrada")
            return False

        mesa = self.mesas[mesa_id][0]
        
        # Verificar si la mesa está libre
        if mesa['estado'] != 'libre':
            print(f"⚠️ Error: Mesa {mesa_id} ya está ocupada")
            return False

        # Marcar la mesa como ocupada
        mesa['estado'] = 'ocupada'
        mesa['comentarios_camarero'] = []
        mesa['notificaciones'] = []

        # Guardar los cambios
        return self.guardar_mesas()

    def reiniciar_mesa(self, mesa_id):
        """Reinicia una mesa a su estado inicial"""
        if mesa_id not in self.mesas:
            return False
        mesa = self.mesas[mesa_id][0]
        mesa['estado'] = 'libre'
        # Limpiar pedidos y contador de cliente_1
        if 'cliente_1' in mesa:
            mesa['cliente_1']['pedidos'] = []
            mesa['cliente_1']['contador_pedidos'] = 0
        self.guardar_mesas()
        return True

    def obtener_mapa_mesas(self):
        """Obtiene el mapa completo de mesas con su estado y pedidos."""
        mesas_info = []
        for mesa_id, mesa_data in self.mesas.items():
            mesa = mesa_data[0]
            pedidos_en_cocina = []
            pedidos_entregados = []
            
            # Procesar pedidos del cliente_1
            for pedido in mesa.get('cliente_1', {}).get('pedidos', []):
                pedido_info = {
                    'id': pedido['id'],
                    'nombre': pedido['nombre'],
                    'cantidad': pedido['cantidad'],
                    'cliente': 'Cliente 1',
                    'estado_cocina': pedido['estado_cocina'],
                    'hora_envio': pedido['hora'],
                    'notas': pedido.get('notas', []),
                    'mozo': pedido.get('mozo', 'Sin asignar')
                }
                
                if pedido['estado_cocina'] == '👨‍🍳 En preparación':
                    pedidos_en_cocina.append(pedido_info)
                elif pedido['estado_cocina'] == '✅ Entregado':
                    pedidos_entregados.append(pedido_info)
            
            mesas_info.append({
                'id': mesa_id,
                'nombre': mesa['nombre'],
                'estado': mesa['estado'],
                'pedidos_en_cocina': pedidos_en_cocina,
                'pedidos_entregados': pedidos_entregados
            })
        
        return mesas_info 