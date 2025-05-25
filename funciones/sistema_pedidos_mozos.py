from datetime import datetime
import os
import json
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
            mesas_ocupadas = []
            
            for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
                mesa = mesa_data[0]
                estado = "🟢 Libre" if mesa['estado'] == 'libre' else "🟠 Ocupada"
                print(f"\n{mesa['nombre']} [{estado}]")
                
                if mesa['estado'] == 'ocupada':
                    self._mostrar_detalles_mesa(mesa_id, mesa)
                    mesas_ocupadas.append((mesa_id, mesa))

            print("\n0. Volver al menú principal")
            
            try:
                opcion = int(input("\nSeleccione una mesa para gestionar: "))
                if opcion == 0:
                    return
                
                if 1 <= opcion <= len(mesas_ocupadas):
                    mesa_id, mesa = mesas_ocupadas[opcion - 1]
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
        """Envía los pedidos pendientes a cocina."""
        cliente_key = 'cliente_1'
        pedidos = mesa[cliente_key].get('pedidos', [])
        
        if not pedidos:
            print("\nℹ️ No hay pedidos para enviar a cocina")
            return

        pedidos_pendientes = [p for p in pedidos if p['estado_cocina'] == self.estados_pedido['pendiente']]
        if not pedidos_pendientes:
            print("\nℹ️ No hay pedidos pendientes para enviar a cocina")
            return

        print("\n=== ENVIAR A COCINA ===")
        for idx, pedido in enumerate(pedidos_pendientes, 1):
            print(f"{idx}. {pedido['cantidad']}x {pedido['nombre']}")

        print("\n1. Enviar todos los pedidos")
        print("2. Seleccionar pedidos específicos")
        print("0. Volver")

        opcion = input("\nSeleccione una opción: ")
        if opcion == "1":
            for pedido in pedidos_pendientes:
                self._actualizar_estado_pedido(mesa_id, pedido['id'], 'en_preparacion')
            print("\n✅ Todos los pedidos enviados a cocina")
        elif opcion == "2":
            seleccion = input("\nIngrese los números de los pedidos (separados por coma): ")
            try:
                indices = [int(i.strip()) - 1 for i in seleccion.split(',')]
                for idx in indices:
                    if 0 <= idx < len(pedidos_pendientes):
                        self._actualizar_estado_pedido(mesa_id, pedidos_pendientes[idx]['id'], 'en_preparacion')
                print("\n✅ Pedidos seleccionados enviados a cocina")
            except ValueError:
                print("\n⚠️ Formato inválido")

    def _gestionar_pago_mesa(self, mesa_id, mesa):
        """Gestiona el pago de una mesa."""
        cliente_key = 'cliente_1'
        pedidos = mesa[cliente_key].get('pedidos', [])
        
        if not pedidos:
            print("\n⚠️ No hay pedidos para pagar")
            return

        # Filtrar solo pedidos entregados y no cancelados
        pedidos_pagables = [p for p in pedidos if p['estado_cocina'] == self.estados_pedido['entregado'] 
                          and p['estado_cocina'] != self.estados_pedido['cancelado']]
        
        if not pedidos_pagables:
            print("\n⚠️ No hay pedidos entregados para pagar")
            return

        print("\n=== GESTIONAR PAGO ===")
        total = 0
        for idx, pedido in enumerate(pedidos_pagables, 1):
            subtotal = pedido['precio'] * pedido['cantidad']
            total += subtotal
            print(f"{idx}. {pedido['cantidad']}x {pedido['nombre']} - ${subtotal}")
            if 'notas' in pedido and pedido['notas']:
                for nota in pedido['notas']:
                    print(f"   • {nota['texto']}")

        print(f"\n💵 TOTAL: ${total}")
        
        print("\n1. Pagar todos los pedidos")
        print("2. Seleccionar pedidos específicos")
        print("0. Volver")

        opcion = input("\nSeleccione una opción: ")
        if opcion in ["1", "2"]:
            if opcion == "1":
                self._procesar_pago(mesa_id, mesa, pedidos_pagables, total)
            else:
                seleccion = input("\nIngrese los números de los pedidos (separados por coma): ")
                try:
                    indices = [int(i.strip()) - 1 for i in seleccion.split(',')]
                    pedidos_seleccionados = []
                    subtotal = 0
                    for idx in indices:
                        if 0 <= idx < len(pedidos_pagables):
                            pedido = pedidos_pagables[idx]
                            pedidos_seleccionados.append(pedido)
                            subtotal += pedido['precio'] * pedido['cantidad']
                    if subtotal > 0:
                        self._procesar_pago(mesa_id, mesa, pedidos_seleccionados, subtotal)
                except ValueError:
                    print("\n⚠️ Formato inválido")

    def _procesar_pago(self, mesa_id, mesa, pedidos_a_pagar, total):
        """Procesa el pago de una mesa."""
        print("\n1. Pagar con efectivo")
        print("2. Pagar con tarjeta")
        print("0. Volver")
        
        opcion = input("\nSeleccione el método de pago: ")
        if opcion in ["1", "2"]:
            metodo_pago = "Efectivo" if opcion == "1" else "Tarjeta"
            self._registrar_pago(mesa_id, mesa, pedidos_a_pagar, total, metodo_pago)
            print("\n✅ Pago procesado exitosamente")
            
            # Verificar si quedan pedidos por pagar
            pedidos_restantes = [p for p in mesa['cliente_1']['pedidos'] 
                               if p['estado_cocina'] == self.estados_pedido['entregado'] 
                               and p['estado_cocina'] != self.estados_pedido['cancelado']
                               and p not in pedidos_a_pagar]
            
            if not pedidos_restantes:
                print("\nℹ️ No quedan pedidos por pagar. La mesa será liberada.")
                self.sistema_mesas.reiniciar_mesa(mesa_id)
        elif opcion == "0":
            return
        else:
            print("\n⚠️ Opción inválida")

    def _registrar_pago(self, mesa_id, mesa, pedidos_pagados, total, metodo_pago):
        """Registra el pago y genera el ticket."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fecha = datetime.now().strftime("%Y-%m-%d")
        
        # Crear directorios si no existen
        historial_fecha_dir = os.path.join(self.historial_dir, fecha)
        tickets_fecha_dir = os.path.join("data", "tickets", fecha)
        os.makedirs(historial_fecha_dir, exist_ok=True)
        os.makedirs(tickets_fecha_dir, exist_ok=True)
        
        # Guardar historial
        historial = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M hs"),
            "mesa_id": mesa_id,
            "mesa_nombre": mesa['nombre'],
            "mozo": self.mozo_actual,
            "pedidos_pagados": pedidos_pagados,
            "total": total,
            "metodo_pago": metodo_pago
        }
        
        archivo_historial = os.path.join(historial_fecha_dir, f"ticket_mesa{mesa_id}_{timestamp}.json")
        with open(archivo_historial, 'w', encoding='utf-8') as f:
            json.dump(historial, f, ensure_ascii=False, indent=4)
        
        # Generar ticket
        self._generar_ticket(mesa_id, mesa, pedidos_pagados, total, metodo_pago, timestamp, tickets_fecha_dir)
        
        # Marcar pedidos como pagados
        for pedido in pedidos_pagados:
            pedido['estado_cocina'] = '💰 Pagado'

    def _generar_ticket(self, mesa_id, mesa, pedidos_pagados, total, metodo_pago, timestamp, tickets_fecha_dir):
        """Genera el ticket de pago."""
        archivo_ticket = os.path.join(tickets_fecha_dir, f"ticket_{mesa_id}_{timestamp}.txt")
        os.makedirs(os.path.dirname(archivo_ticket), exist_ok=True)
        
        with open(archivo_ticket, 'w', encoding='utf-8') as f:
            f.write("=" * 40 + "\n")
            f.write("           TICKET DE PAGO\n")
            f.write("=" * 40 + "\n\n")
            
            f.write(f"Mesa: {mesa['nombre']}\n")
            f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write(f"Mozo: {self.mozo_actual}\n")
            f.write("-" * 40 + "\n\n")
            
            f.write("DETALLE DE PEDIDOS PAGADOS:\n")
            f.write("-" * 40 + "\n")
            for pedido in pedidos_pagados:
                subtotal = pedido['precio'] * pedido['cantidad']
                f.write(f"{pedido['cantidad']}x {pedido['nombre']}\n")
                f.write(f"   Precio unitario: ${pedido['precio']}\n")
                if 'notas' in pedido and pedido['notas']:
                    for nota in pedido['notas']:
                        f.write(f"   • {nota['texto']}\n")
                f.write(f"   Subtotal: ${subtotal}\n\n")
            
            f.write("-" * 40 + "\n")
            f.write(f"TOTAL A PAGAR: ${total}\n")
            f.write(f"Método de pago: {metodo_pago}\n")
            f.write("=" * 40 + "\n")
            f.write("¡Gracias por su visita!\n")
            f.write("=" * 40 + "\n")

    def _seleccionar_plato_del_menu(self, todos_platos):
        """Permite seleccionar un plato del menú completo."""
        while True:
            try:
                print("\n--- SELECCIÓN ---")
                print("Ingrese el número del plato que desea (0 para volver)")
                seleccion = int(input("> "))

                if seleccion == 0:
                    return None
                elif 1 <= seleccion <= len(todos_platos):
                    plato_seleccionado = todos_platos[seleccion - 1]['plato']
                    print(f"\nSeleccionaste: {plato_seleccionado['nombre']} - ${plato_seleccionado['precio']}")
                    return plato_seleccionado
                else:
                    print("⚠️ Número inválido. Intente nuevamente.")
            except ValueError:
                print("⚠️ Por favor ingrese un número.")

    def _pedir_cantidad(self):
        """Solicita la cantidad de un plato."""
        while True:
            try:
                cantidad = int(input("\nIngrese la cantidad: "))
                if cantidad > 0:
                    return cantidad
                else:
                    print("⚠️ La cantidad debe ser mayor a 0")
            except ValueError:
                print("⚠️ Por favor ingrese un número válido")

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

    def _finalizar_pedido(self, mesa_id):
        """Finaliza el pedido de una mesa."""
        mesa_data = self.sistema_mesas.obtener_mesa(mesa_id)
        if not mesa_data:
            return

        mesa = mesa_data[0]
        cliente_key = 'cliente_1'
        
        if not mesa[cliente_key].get('pedidos'):
            print("\n⚠️ No hay pedidos para finalizar")
            return
            
        print("\n=== RESUMEN DEL PEDIDO ===")
        total = 0
        for pedido in mesa[cliente_key]['pedidos']:
            subtotal = pedido['precio'] * pedido['cantidad']
            total += subtotal
            print(f"{pedido['cantidad']}x {pedido['nombre']} - ${subtotal}")
        
        print(f"\n💵 TOTAL: ${total}")
        print("\n✅ Pedido finalizado exitosamente")

    def gestionar_pedidos_activos(self):
        """Gestiona los pedidos activos."""
        pedidos_activos = self._obtener_pedidos_activos()
        if not pedidos_activos:
            print("\n⚠️ No hay pedidos activos para gestionar")
            return

        print("\n=== PEDIDOS ACTIVOS ===")
        for idx, pedido in enumerate(pedidos_activos, 1):
            print(f"\n{idx}. Mesa: {pedido['mesa_nombre']}")
            print(f"   - {pedido['cantidad']}x {pedido['nombre']} [{pedido['estado_cocina']}]")
            print(f"   - Mozo: {pedido['mozo']}")

        print("\n0. Volver")
        try:
            opcion = int(input("\nSeleccione un pedido para gestionar: "))
            if opcion == 0:
                return
            if 1 <= opcion <= len(pedidos_activos):
                pedido = pedidos_activos[opcion - 1]
                self._gestionar_pedido(pedido)
            else:
                print("\n⚠️ Opción inválida")
        except ValueError:
            print("\n⚠️ Por favor ingrese un número válido")

    def _obtener_pedidos_activos(self):
        """Obtiene todos los pedidos activos."""
        pedidos_activos = []
        for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
            mesa = mesa_data[0]
            if mesa['estado'] == 'ocupada':
                cliente_key = 'cliente_1'
                for pedido in mesa[cliente_key].get('pedidos', []):
                    if pedido['estado_cocina'] in [self.estados_pedido['pendiente'], self.estados_pedido['en_preparacion']]:
                        pedido_info = {
                            'id': pedido['id'],
                            'mesa_id': mesa_id,
                            'mesa_nombre': mesa['nombre'],
                            'nombre': pedido['nombre'],
                            'cantidad': pedido['cantidad'],
                            'estado_cocina': pedido['estado_cocina'],
                            'mozo': pedido.get('mozo', 'No asignado')
                        }
                        pedidos_activos.append(pedido_info)
        return pedidos_activos

    def _gestionar_pedido(self, pedido):
        """Gestiona un pedido específico."""
        print(f"\n=== GESTIONANDO PEDIDO ===")
        print(f"Mesa: {pedido['mesa_nombre']}")
        print(f"Pedido: {pedido['cantidad']}x {pedido['nombre']}")
        print(f"Estado actual: {pedido['estado_cocina']}")

        if pedido['estado_cocina'] == self.estados_pedido['pendiente']:
            print("\n1. Marcar como EN PREPARACIÓN")
            print("2. Cancelar pedido")
            print("0. Volver")
            
            opcion = input("\nSeleccione una opción: ")
            if opcion == "1":
                self._actualizar_estado_pedido(pedido['mesa_id'], pedido['id'], 'en_preparacion')
            elif opcion == "2":
                self._actualizar_estado_pedido(pedido['mesa_id'], pedido['id'], 'cancelado')
            elif opcion == "0":
                return
            else:
                print("\n⚠️ Opción inválida")
        elif pedido['estado_cocina'] == self.estados_pedido['en_preparacion']:
            print("\n1. Marcar como ENTREGADO")
            print("2. Cancelar pedido")
            print("0. Volver")
            
            opcion = input("\nSeleccione una opción: ")
            if opcion == "1":
                self._actualizar_estado_pedido(pedido['mesa_id'], pedido['id'], 'entregado')
            elif opcion == "2":
                self._actualizar_estado_pedido(pedido['mesa_id'], pedido['id'], 'cancelado')
            elif opcion == "0":
                return
            else:
                print("\n⚠️ Opción inválida")

    def _actualizar_estado_pedido(self, mesa_id, pedido_id, nuevo_estado):
        """Actualiza el estado de un pedido."""
        mesa_data = self.sistema_mesas.obtener_mesa(mesa_id)
        if not mesa_data:
            return False

        mesa = mesa_data[0]
        cliente_key = 'cliente_1'
        
        for pedido in mesa[cliente_key].get('pedidos', []):
            if pedido['id'] == pedido_id:
                pedido['estado_cocina'] = self.estados_pedido[nuevo_estado]
                self.sistema_mesas.guardar_mesas()
                print(f"\n✅ Pedido actualizado a {self.estados_pedido[nuevo_estado]}")
                return True
        return False

    def marcar_pedido_entregado(self):
        """Marca un pedido como entregado."""
        pedidos_en_preparacion = self._obtener_pedidos_en_preparacion()
        if not pedidos_en_preparacion:
            print("\n⚠️ No hay pedidos en preparación")
            return

        print("\n=== PEDIDOS EN PREPARACIÓN ===")
        for idx, pedido in enumerate(pedidos_en_preparacion, 1):
            print(f"\n{idx}. Mesa: {pedido['mesa_nombre']}")
            print(f"   - {pedido['cantidad']}x {pedido['nombre']}")
            print(f"   - Mozo: {pedido['mozo']}")

        print("\n0. Volver")
        try:
            opcion = int(input("\nSeleccione un pedido para marcar como entregado: "))
            if opcion == 0:
                return
            if 1 <= opcion <= len(pedidos_en_preparacion):
                pedido = pedidos_en_preparacion[opcion - 1]
                self._actualizar_estado_pedido(pedido['mesa_id'], pedido['id'], 'entregado')
            else:
                print("\n⚠️ Opción inválida")
        except ValueError:
            print("\n⚠️ Por favor ingrese un número válido")

    def _obtener_pedidos_en_preparacion(self):
        """Obtiene los pedidos en preparación."""
        pedidos_en_preparacion = []
        for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
            mesa = mesa_data[0]
            if mesa['estado'] == 'ocupada':
                cliente_key = 'cliente_1'
                for pedido in mesa[cliente_key].get('pedidos', []):
                    if pedido['estado_cocina'] == self.estados_pedido['en_preparacion']:
                        pedido_info = {
                            'id': pedido['id'],
                            'mesa_id': mesa_id,
                            'mesa_nombre': mesa['nombre'],
                            'nombre': pedido['nombre'],
                            'cantidad': pedido['cantidad'],
                            'mozo': pedido.get('mozo', 'No asignado')
                        }
                        pedidos_en_preparacion.append(pedido_info)
        return pedidos_en_preparacion

    def mostrar_resumen_mesas(self):
        """Muestra el resumen de todas las mesas."""
        print("\n=== RESUMEN DE MESAS ===")
        
        for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
            mesa = mesa_data[0]
            estado = "🟢 Libre" if mesa['estado'] == 'libre' else "🟠 Ocupada"
            print(f"\n{mesa['nombre']} [{estado}]")
            
            if mesa['estado'] == 'ocupada':
                self._mostrar_detalles_mesa(mesa_id, mesa)

    def reiniciar_mesa(self):
        """Reinicia una mesa específica."""
        mesas_ocupadas = [(mid, m[0]) for mid, m in self.sistema_mesas.mesas.items() if m[0]['estado'] == 'ocupada']
        if not mesas_ocupadas:
            print("\n⚠️ No hay mesas ocupadas para reiniciar")
            return

        print("\n=== REINICIAR MESA ===")
        for idx, (mid, mesa) in enumerate(mesas_ocupadas, 1):
            print(f"{idx}. {mesa['nombre']}")
        print("0. Volver")

        try:
            opcion = int(input("\nSeleccione la mesa a reiniciar: "))
            if opcion == 0:
                return
            if 1 <= opcion <= len(mesas_ocupadas):
                mesa_id, mesa = mesas_ocupadas[opcion - 1]
                print(f"\n⚠️ ¿Está seguro que desea reiniciar la {mesa['nombre']}?")
                print("1. Sí, reiniciar mesa")
                print("2. No, volver")
                confirmacion = input("\nSeleccione una opción: ")
                if confirmacion == "1":
                    if self.sistema_mesas.reiniciar_mesa(mesa_id):
                        print("\n✅ Mesa reiniciada exitosamente")
                else:
                    print("\n❌ Operación cancelada")
            else:
                print("\n⚠️ Opción inválida")
        except ValueError:
            print("\n⚠️ Por favor ingrese un número válido")

    def enviar_pedidos_cocina(self, mesa_id, pedidos, mozo):
        """Envía los pedidos pendientes a cocina."""
        try:
            mesa_data = self.sistema_mesas.obtener_mesa(mesa_id)
            if not mesa_data:
                raise Exception(f"Mesa {mesa_id} no encontrada")

            mesa = mesa_data[0]  # Obtener el primer elemento del array

            # Si la mesa está libre, ocuparla
            if mesa['estado'] == 'libre':
                if not self.sistema_mesas.ocupar_mesa(mesa_id):
                    raise Exception("Error al ocupar la mesa")

            # Inicializar contador de pedidos si no existe
            if 'cliente_1' not in mesa:
                mesa['cliente_1'] = {'pedidos': [], 'contador_pedidos': 0}
            elif 'contador_pedidos' not in mesa['cliente_1']:
                mesa['cliente_1']['contador_pedidos'] = 0

            # Procesar cada pedido
            for pedido in pedidos:
                # Incrementar contador y generar ID único
                mesa['cliente_1']['contador_pedidos'] += 1
                pedido_id = f"{int(datetime.now().timestamp() * 1000)}_{mesa['cliente_1']['contador_pedidos']}"
                
                # Crear nuevo pedido
                nuevo_pedido = {
                    'id': pedido_id,
                    'nombre': pedido['nombre'],
                    'cantidad': pedido['cantidad'],
                    'precio': pedido['precio'],
                    'hora': datetime.now().strftime('%H:%M'),
                    'estado_cocina': self.estados_pedido['en_preparacion'],
                    'mozo': mozo
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
            print(f"Error al enviar pedidos a cocina: {str(e)}")
            return False 