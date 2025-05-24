from datetime import datetime

class BaseVisualizador:
    """Clase base para la visualización común de mesas y pedidos"""

    def __init__(self, sistema_mesas):
        self.sistema_mesas = sistema_mesas
        self.estados_pedido = {
            'pendiente': '🟡 Pendiente',
            'en_preparacion': '👨‍🍳 En preparación',
            'entregado': '✅ Entregado',
            'cancelado': '🔴 Cancelado'
        }

    def mostrar_mapa_mesas(self):
        """Muestra un mapa completo de todas las mesas con su estado"""
        while True:
            print("\n=== MAPA DEL RESTAURANTE ===")
            print("\nMesas disponibles:")
            
            mesas_ocupadas = []
            for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
                mesa = mesa_data[0]
                estado = "🟢 Libre" if mesa['estado'] == 'libre' else "🟠 Ocupada"
                print(f"{len(mesas_ocupadas) + 1}. {mesa['nombre']} [{estado}]")
                if mesa['estado'] == 'ocupada':
                    mesas_ocupadas.append((mesa_id, mesa))

            print("\n0. Volver al menú principal")

            try:
                opcion = int(input("\nSeleccione una mesa para ver detalles (número): "))
                if opcion == 0:
                    return
                
                if 1 <= opcion <= len(mesas_ocupadas):
                    mesa_id, mesa = mesas_ocupadas[opcion - 1]
                    self._mostrar_detalles_mesa(mesa_id, mesa)
                else:
                    print("ℹ️   Mesa libre. Seleccione una mesa ocupada.")
            except ValueError:
                print("Por favor ingrese un número válido")

    def _mostrar_detalles_mesa(self, mesa_id, mesa):
        """Muestra los detalles de una mesa específica"""
        print(f"\n=== {mesa['nombre']} ===")
        
        # Pedidos pendientes
        print("\n--- PEDIDOS PENDIENTES ---")
        hay_pendientes = False
        clientes_pendientes = {}
        
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                pedidos_pendientes = []
                for pedido in cliente.get('pedidos', []):
                    if pedido.get('estado_cocina') == self.estados_pedido['pendiente']:
                        pedidos_pendientes.append(pedido)
                if pedidos_pendientes:
                    clientes_pendientes[cliente['nombre']] = pedidos_pendientes
                    hay_pendientes = True

        if hay_pendientes:
            for nombre_cliente, pedidos in clientes_pendientes.items():
                print(f"\n👤 {nombre_cliente}:")
                for pedido in pedidos:
                    print(f"  - {pedido.get('cantidad', 1)}x {pedido.get('nombre', 'Desconocido')} {pedido.get('estado_cocina')}")
                    if 'notas' in pedido and pedido['notas']:
                        for nota in pedido['notas']:
                            print(f"      • {nota['texto']}")
        else:
            print("(No hay pedidos pendientes)")

        # Pedidos en preparación
        print("\n--- PEDIDOS EN PREPARACIÓN ---")
        hay_en_preparacion = False
        clientes_en_preparacion = {}
        
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                pedidos_preparacion = []
                for pedido in cliente.get('pedidos', []):
                    if pedido.get('estado_cocina') == self.estados_pedido['en_preparacion']:
                        pedidos_preparacion.append(pedido)
                if pedidos_preparacion:
                    clientes_en_preparacion[cliente['nombre']] = pedidos_preparacion
                    hay_en_preparacion = True

        if hay_en_preparacion:
            for nombre_cliente, pedidos in clientes_en_preparacion.items():
                print(f"\n👤 {nombre_cliente}:")
                for pedido in pedidos:
                    print(f"  - {pedido.get('cantidad', 1)}x {pedido.get('nombre', 'Desconocido')} {pedido.get('estado_cocina')}")
                    if 'notas' in pedido and pedido['notas']:
                        for nota in pedido['notas']:
                            print(f"      • {nota['texto']}")
        else:
            print("(No hay pedidos en preparación)")

        # Pedidos entregados
        print("\n--- PEDIDOS ENTREGADOS ---")
        hay_entregados = False
        clientes_entregados = {}
        
        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                pedidos_entregados = []
                for pedido in cliente.get('pedidos', []):
                    if pedido.get('estado_cocina') == self.estados_pedido['entregado']:
                        pedidos_entregados.append(pedido)
                if pedidos_entregados:
                    clientes_entregados[cliente['nombre']] = pedidos_entregados
                    hay_entregados = True

        if hay_entregados:
            for nombre_cliente, pedidos in clientes_entregados.items():
                print(f"\n👤 {nombre_cliente}:")
                for pedido in pedidos:
                    print(f"  - {pedido.get('cantidad', 1)}x {pedido.get('nombre', 'Desconocido')} {pedido.get('estado_cocina')}")
                    if 'notas' in pedido and pedido['notas']:
                        for nota in pedido['notas']:
                            print(f"      • {nota['texto']}")
        else:
            print("(No hay pedidos entregados)")

        input("\nPresione Enter para volver al mapa de mesas...")

    def _mostrar_detalle_pedido(self, pedido):
        """Muestra los detalles de un pedido individual"""
        nota_texto = ""
        if 'notas' in pedido and pedido['notas']:
            nota_texto = f" (Nota: {pedido['notas'][-1]['texto']})"
        
        estado_pedido = self.estados_pedido.get(pedido.get('estado_cocina'), '🟡 Pendiente')
        
        print(f"  - {pedido['cantidad']}x {pedido['nombre']} [{estado_pedido}]{nota_texto}")

    def _validar_mesa(self, mesa_id):
        """Valida que la mesa exista y devuelve la lista asociada"""
        if mesa_id not in self.sistema_mesas.mesas:
            print(f"⚠️ Error: Mesa {mesa_id} no encontrada")
            return None
        return self.sistema_mesas.mesas[mesa_id]

    def procesar_pedidos_mesa(self, mesa_id):
        """Procesa los pedidos de una mesa específica"""
        mesa_data = self._validar_mesa(mesa_id)
        if not mesa_data:
            return []

        mesa = mesa_data[0]
        pedidos_procesados = []

        for i in range(1, mesa.get('capacidad', 0) + 1):
            cliente_key = f"cliente_{i}"
            cliente = mesa.get(cliente_key)
            if cliente and cliente.get('nombre'):
                for pedido in cliente.get('pedidos', []):
                    pedido_info = {
                        'id': pedido.get('id'),
                        'nombre': pedido.get('nombre', 'Desconocido'),
                        'cantidad': pedido.get('cantidad', 1),
                        'cliente': cliente['nombre'],
                        'mesa_id': mesa_id,
                        'mesa_nombre': mesa['nombre'],
                        'hora': pedido.get('hora', 'No registrada'),
                        'notas': pedido.get('notas', []),
                        'estado_cocina': pedido.get('estado_cocina'),
                        'entregado': pedido.get('entregado', False)
                    }
                    pedidos_procesados.append(pedido_info)
        return pedidos_procesados 