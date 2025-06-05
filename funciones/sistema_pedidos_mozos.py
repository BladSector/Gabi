from datetime import datetime
import os
import json
import shutil
from .base_visualizacion import BaseVisualizador

HISTORIAL_DIR = os.path.join("data", "historial_pagos")

class SistemaPedidosMozos(BaseVisualizador):
    """Sistema de gestión de pedidos para los mozos del restaurante."""

    def __init__(self, sistema_mesas):
        """Inicializa el sistema con dependencias necesarias."""
        super().__init__(sistema_mesas)
        self.mozo_actual = None
        self.historial_dir = HISTORIAL_DIR
        if not os.path.exists(self.historial_dir):
            os.makedirs(self.historial_dir)

    def mostrar_mapa_mesas(self):
        """Muestra el mapa de mesas y permite seleccionar una para gestionar."""
        while True:
            print("\n=== MAPA DE MESAS ===")
            todas_mesas = []
            
            for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
                mesa = mesa_data[0]
                estado = "🟢 Libre" if mesa['estado'] == 'libre' else "🟠 Ocupada"
                todas_mesas.append((mesa_id, mesa))
                print(f"\n{len(todas_mesas)}. {mesa['nombre']} [{estado}]")
                
                if mesa['estado'] == 'ocupada':
                    self._mostrar_detalles_mesa(mesa_id, mesa)

            print("\n0. Volver al menú principal")
            
            try:
                opcion = int(input("\nSeleccione una mesa para gestionar: "))
                if opcion == 0:
                    return
                
                if 1 <= opcion <= len(todas_mesas):
                    mesa_id, mesa = todas_mesas[opcion - 1]
                    self._gestionar_mesa(mesa_id, mesa)
                else:
                    print("\n⚠️ Opción inválida")
            except ValueError:
                print("\n⚠️ Por favor ingrese un número válido")

    def _gestionar_mesa(self, mesa_id, mesa):
        """Gestiona una mesa específica."""
        while True:
            print(f"\n=== GESTIONANDO {mesa['nombre']} ===")
            print("1. Agregar pedido")
            print("2. Ver pedidos pendientes")
            print("3. Enviar pedidos a cocina")
            print("4. Gestionar pago")
            print("0. Volver")

            try:
                opcion = int(input("\nSeleccione una opción: "))
                
                if opcion == 0:
                    return
                elif opcion == 1:
                    self._agregar_pedido_mesa(mesa_id, mesa)
                elif opcion == 2:
                    self._mostrar_pedidos_pendientes(mesa)
                elif opcion == 3:
                    self._enviar_pedidos_cocina(mesa_id, mesa)
                elif opcion == 4:
                    self._gestionar_pago_mesa(mesa_id, mesa)
                else:
                    print("\n⚠️ Opción inválida")
            except ValueError:
                print("\n⚠️ Por favor ingrese un número válido")

    def _agregar_pedido_mesa(self, mesa_id, mesa):
        """Agrega un pedido a la mesa."""
        if mesa['estado'] == 'libre':
            if not self.sistema_mesas.ocupar_mesa(mesa_id):
                return

        # Si es la mesa de Pedidos, solicitar el nombre del cliente
        if mesa['nombre'] == 'Pedidos' and not mesa['cliente_1'].get('nombre'):
            nombre_cliente = input("\nIngrese el nombre del cliente: ").strip()
            if not nombre_cliente:
                print("\n⚠️ El nombre del cliente es obligatorio")
                return
            mesa['cliente_1']['nombre'] = nombre_cliente
            self.sistema_mesas.guardar_mesas()

        todos_platos = self.sistema_mesas.mostrar_menu_completo()
        plato = self._seleccionar_plato_del_menu(todos_platos)
        
        if plato:
            cantidad = self._pedir_cantidad()
            if cantidad > 0:
                self._agregar_pedido(mesa_id, plato, cantidad)
                print(f"\n✅ {cantidad} x {plato['nombre']} agregado(s) al pedido")

    def _mostrar_pedidos_pendientes(self, mesa):
        """Muestra los pedidos pendientes de una mesa."""
        cliente_key = 'cliente_1'
        pedidos = mesa[cliente_key].get('pedidos', [])
        
        if not pedidos:
            print("\nℹ️ No hay pedidos pendientes")
            return

        print("\n=== PEDIDOS PENDIENTES ===")
        for idx, pedido in enumerate(pedidos, 1):
            if pedido['estado_cocina'] == self.estados_pedido['pendiente']:
                print(f"{idx}. {pedido['cantidad']}x {pedido['nombre']} - ${pedido['precio'] * pedido['cantidad']}")

    def _enviar_pedidos_cocina(self, mesa_id, mesa):
        """Envía pedidos a la cocina"""
        try:
            mesa_data = self.sistema_mesas.obtener_mesa(mesa_id)
            if not mesa_data:
                return False

            mesa = mesa_data[0]
            
            # Verificar si la mesa está libre
            if mesa['estado'] == 'libre':
                mesa['estado'] = 'ocupada'
            
            # Inicializar cliente_1 si no existe
            if 'cliente_1' not in mesa:
                mesa['cliente_1'] = {
                    'pedidos': [],
                    'contador_pedidos': 0
                }
            
            # Procesar cada pedido
            for pedido in mesa['cliente_1']['pedidos']:
                pedido_procesado = {
                    'id': pedido['id'],
                    'plato_id': pedido.get('plato_id'),
                    'nombre': pedido['nombre'],
                    'precio': pedido['precio'],
                    'cantidad': pedido['cantidad'],
                    'estado_cocina': '🟡 Pendiente',
                    'hora': datetime.now().strftime('%H:%M:%S'),
                    'mozo': self.mozo_actual,
                    'cliente': pedido.get('cliente', 'Mesa General')  # Agregar nombre del cliente
                }
                
                # Agregar notas si existen
                if 'notas' in pedido:
                    pedido_procesado['notas'] = pedido['notas']
                
                mesa['cliente_1']['pedidos'].append(pedido_procesado)
                mesa['cliente_1']['contador_pedidos'] += 1

            return self.sistema_mesas.guardar_mesas()
            
        except Exception as e:
            print(f"Error al enviar pedidos a cocina: {str(e)}")
            return False

    def _gestionar_pago_mesa(self, mesa_id, mesa):
        """Gestiona el pago de una mesa."""
        cliente_key = 'cliente_1'
        pedidos = mesa[cliente_key].get('pedidos', [])
        
        # Filtrar solo pedidos en preparación y no cancelados
        pedidos_pagables = [p for p in pedidos if p['estado_cocina'] == self.estados_pedido['en_preparacion']
                          and p['estado_cocina'] != self.estados_pedido['cancelado']]
        
        if not pedidos_pagables:
            print("\n⚠️ No hay pedidos en preparación para pagar")
            return

        print("\n=== PEDIDOS PARA PAGAR ===")
        total = 0
        for idx, pedido in enumerate(pedidos_pagables, 1):
            subtotal = pedido['precio'] * pedido['cantidad']
            total += subtotal
            print(f"{idx}. {pedido['cantidad']}x {pedido['nombre']} - ${subtotal}")

        print(f"\n💵 TOTAL: ${total}")
        
        confirmacion = input("\n¿Desea proceder con el pago? (s/n): ")
        if confirmacion.lower() == 's':
            metodo_pago = self._seleccionar_metodo_pago()
            if metodo_pago:
                self._registrar_pago(mesa_id, mesa, pedidos_pagables, total, metodo_pago)
                print("\n✅ Pago registrado exitosamente")

    def _seleccionar_metodo_pago(self):
        """Permite seleccionar el método de pago."""
        print("\n=== MÉTODO DE PAGO ===")
        print("1. Efectivo")
        print("2. Tarjeta de débito")
        print("3. Tarjeta de crédito")
        print("4. Transferencia")
        print("0. Cancelar")
        
        try:
            opcion = int(input("\nSeleccione el método de pago: "))
            if opcion == 0:
                return None
            elif opcion == 1:
                return "efectivo"
            elif opcion == 2:
                return "debito"
            elif opcion == 3:
                return "credito"
            elif opcion == 4:
                return "transferencia"
            else:
                print("\n⚠️ Opción inválida")
                return None
        except ValueError:
            print("\n⚠️ Por favor ingrese un número válido")
            return None

    def _registrar_pago(self, mesa_id, mesa, pedidos_pagados, total, metodo_pago):
        """Registra el pago de los pedidos"""
        try:
            # Obtener los IDs de los pedidos pagados
            ids_pagados = [p['id'] for p in pedidos_pagados]
            
            # Actualizar estado de los pedidos
            pedidos_actualizados = []
            for pedido in mesa['cliente_1']['pedidos']:
                if pedido['id'] in ids_pagados:
                    pedido['estado_cocina'] = '💰 Pagado'
                pedidos_actualizados.append(pedido)
            
            mesa['cliente_1']['pedidos'] = pedidos_actualizados
            
            # Guardar ticket
            self._guardar_ticket(mesa_id, pedidos_pagados, total, metodo_pago)
            
            return True
        except Exception as e:
            print(f"Error al registrar pago: {str(e)}")
            return False

    def _guardar_ticket(self, mesa_id, pedidos, total, metodo_pago):
        """Guarda el ticket de los pedidos pagados"""
        try:
            fecha_actual = datetime.now().strftime('%Y-%m-%d')
            hora_actual = datetime.now().strftime('%H:%M:%S')
            timestamp = datetime.now().timestamp()
            
            # Agrupar pedidos por cliente y calcular subtotales
            pedidos_por_cliente = {}
            for pedido in pedidos:
                cliente = pedido.get('cliente', 'Mesa General')
                if cliente not in pedidos_por_cliente:
                    pedidos_por_cliente[cliente] = {
                        'pedidos': [],
                        'subtotal': 0
                    }
                
                # Asegurar que usamos el precio unitario correcto
                precio_unitario = pedido.get('precio_unitario', pedido['precio'])
                cantidad = pedido['cantidad']
                precio_total_item = precio_unitario * cantidad
                
                # Crear copia del pedido con información detallada
                pedido_detallado = {
                    'id': pedido['id'],
                    'nombre': pedido['nombre'],
                    'cantidad': cantidad,
                    'precio_unitario': precio_unitario,
                    'precio_total': precio_total_item,
                    'hora': pedido.get('hora', datetime.now().strftime('%H:%M')),
                    'estado_cocina': pedido.get('estado_cocina', '💰 Pagado'),
                    'mozo': pedido.get('mozo', self.mozo_actual or 'No especificado'),
                    'cliente': cliente
                }
                
                # Agregar notas si existen
                if 'notas' in pedido and pedido['notas']:
                    pedido_detallado['notas'] = pedido['notas']
                
                pedidos_por_cliente[cliente]['pedidos'].append(pedido_detallado)
                pedidos_por_cliente[cliente]['subtotal'] += precio_total_item
            
            # Recalcular el total general
            total_general = sum(info['subtotal'] for info in pedidos_por_cliente.values())
            
            # Crear el ticket con información detallada
            ticket = {
                'ticket_id': f"{int(timestamp * 1000)}_{mesa_id}",
                'fecha': fecha_actual,
                'hora': hora_actual,
                'mesa_id': mesa_id,
                'mesa_nombre': self.sistema_mesas.obtener_mesa(mesa_id)[0]['nombre'],
                'pedidos_por_cliente': pedidos_por_cliente,
                'total': total_general,  # Usar el total recalculado
                'metodo_pago': metodo_pago,
                'mozo': self.mozo_actual or 'No especificado',
                'detalles_pago': {
                    'timestamp': timestamp,
                    'fecha_hora_completa': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                }
            }
            
            # Crear estructura de directorios
            directorio_base = os.path.join('data', 'tickets')
            directorio_fecha = os.path.join(directorio_base, fecha_actual)
            
            for dir in [directorio_base, directorio_fecha]:
                os.makedirs(dir, exist_ok=True)
            
            # Guardar ticket principal
            nombre_archivo = f'ticket_mesa{mesa_id}_{datetime.now().strftime("%H%M%S")}.json'
            ruta_archivo = os.path.join(directorio_fecha, nombre_archivo)
            
            # Guardar usando escritura segura
            ruta_temporal = ruta_archivo + '.tmp'
            with open(ruta_temporal, 'w', encoding='utf-8') as f:
                json.dump(ticket, f, ensure_ascii=False, indent=2)
            os.replace(ruta_temporal, ruta_archivo)
            
            # Actualizar historial diario
            historial_path = os.path.join(directorio_fecha, 'historial_diario.json')
            try:
                if os.path.exists(historial_path):
                    with open(historial_path, 'r', encoding='utf-8') as f:
                        historial = json.load(f)
                else:
                    historial = []
                
                historial.append(ticket)
                
                # Guardar historial usando escritura segura
                historial_temp = historial_path + '.tmp'
                with open(historial_temp, 'w', encoding='utf-8') as f:
                    json.dump(historial, f, ensure_ascii=False, indent=2)
                os.replace(historial_temp, historial_path)
                
            except Exception as e:
                print(f"⚠️ Error al actualizar historial diario: {str(e)}")
                # Continuar a pesar del error en el historial
            
            print(f"✅ Ticket guardado exitosamente: {ruta_archivo}")
            return True
            
        except Exception as e:
            print(f"❌ Error al guardar ticket: {str(e)}")
            import traceback
            print("Traceback completo:")
            print(traceback.format_exc())
            return False

    def _seleccionar_plato_del_menu(self, todos_platos):
        """Permite seleccionar un plato del menú."""
        try:
            opcion = int(input("\nSeleccione un plato (número): "))
            if 1 <= opcion <= len(todos_platos):
                return todos_platos[opcion - 1]['plato']
            else:
                print("\n⚠️ Opción inválida")
                return None
        except ValueError:
            print("\n⚠️ Por favor ingrese un número válido")
            return None

    def _pedir_cantidad(self):
        """Solicita la cantidad del plato."""
        try:
            cantidad = int(input("\nIngrese la cantidad: "))
            if cantidad > 0:
                return cantidad
            else:
                print("\n⚠️ La cantidad debe ser mayor a 0")
                return 0
        except ValueError:
            print("\n⚠️ Por favor ingrese un número válido")
            return 0

    def _agregar_pedido(self, mesa_id, plato, cantidad):
        """Agrega un pedido a la mesa."""
        mesa_data = self.sistema_mesas.obtener_mesa(mesa_id)
        if not mesa_data:
            return

        mesa = mesa_data[0]
        cliente_key = 'cliente_1'  # Siempre usamos cliente_1 para los pedidos del mozo
        
        if 'contador_pedidos' not in mesa[cliente_key]:
            mesa[cliente_key]['contador_pedidos'] = 0
        mesa[cliente_key]['contador_pedidos'] += 1
        
        pedido_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{mesa[cliente_key]['contador_pedidos']}"
        
        nuevo_pedido = {
            'id': pedido_id,
            'plato_id': plato['id'],
            'nombre': plato['nombre'],
            'cantidad': cantidad,
            'precio': plato['precio'],
            'hora': datetime.now().strftime("%H:%M hs"),
            'estado_cocina': self.estados_pedido['pendiente'],
            'mozo': self.mozo_actual
        }
        
        if 'pedidos' not in mesa[cliente_key]:
            mesa[cliente_key]['pedidos'] = []
        mesa[cliente_key]['pedidos'].append(nuevo_pedido)
        
        self.sistema_mesas.guardar_mesas()

    def enviar_pedidos_cocina(self, mesa_id, pedidos, mozo):
        """Envía los pedidos a cocina."""
        try:
            mesa_data = self.sistema_mesas.obtener_mesa(mesa_id)
            if not mesa_data:
                raise Exception(f"Mesa {mesa_id} no encontrada")

            mesa = mesa_data[0]  # Obtener el primer elemento del array

            # Si la mesa está libre, ocuparla
            if mesa['estado'] == 'libre':
                if not self.sistema_mesas.ocupar_mesa(mesa_id):
                    raise Exception("Error al ocupar la mesa")

            # Inicializar cliente_1 si no existe
            if 'cliente_1' not in mesa:
                mesa['cliente_1'] = {'pedidos': [], 'contador_pedidos': 0}
            elif 'contador_pedidos' not in mesa['cliente_1']:
                mesa['cliente_1']['contador_pedidos'] = 0

            # Validar que los pedidos de Take Away tengan nombre de cliente
            es_take_away = mesa['nombre'] == 'Take Away Barra'
            if es_take_away:
                for pedido in pedidos:
                    if not pedido.get('cliente') or pedido['cliente'] == 'Mesa General':
                        raise Exception("El nombre del cliente es obligatorio para Take Away")

            # Procesar cada pedido
            for pedido in pedidos:
                # Incrementar contador y generar ID único
                mesa['cliente_1']['contador_pedidos'] += 1
                pedido_id = f"{int(datetime.now().timestamp() * 1000)}_{mesa['cliente_1']['contador_pedidos']}"
                
                # Asegurar que usamos el precio unitario correcto
                precio_unitario = pedido.get('precio_unitario', pedido['precio'])
                cantidad = pedido['cantidad']
                
                # Crear nuevo pedido
                nuevo_pedido = {
                    'id': pedido_id,
                    'nombre': pedido['nombre'],
                    'cantidad': cantidad,
                    'precio': precio_unitario,  # Guardar el precio unitario
                    'precio_total': precio_unitario * cantidad,  # Calcular y guardar el precio total
                    'hora': datetime.now().strftime('%H:%M'),
                    'estado_cocina': '🟡 Pendiente',
                    'mozo': mozo,
                    'cliente': pedido.get('cliente', 'Mesa General')  # Asegurar que siempre haya un valor
                }

                # Agregar notas si existen
                if 'notas' in pedido and pedido['notas']:
                    nuevo_pedido['notas'] = pedido['notas']

                # Agregar el pedido a la mesa
                mesa['cliente_1']['pedidos'].append(nuevo_pedido)

            # Guardar cambios
            if not self.sistema_mesas.guardar_mesas():
                raise Exception("Error al guardar los cambios")

            return True
        except Exception as e:
            print(f"⚠️ Error al enviar pedidos: {str(e)}")
            return False 