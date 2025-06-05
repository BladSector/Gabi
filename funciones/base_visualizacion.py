from datetime import datetime

class BaseVisualizador:
    """Clase base para la visualización común de mesas y pedidos"""

    def __init__(self, sistema_mesas):
        self.sistema_mesas = sistema_mesas
        self.estados_pedido = {
            'pendiente': '🟡 Pendiente',
            'pagado': '�� Pagado'
        }

    def mostrar_mapa_mesas(self):
        """Muestra un mapa completo de todas las mesas con su estado"""
        while True:
            print("\n=== MAPA DEL RESTAURANTE ===")
            print("\nMesas disponibles:")
            
            mesas_ocupadas = []
            todas_mesas = []
            for mesa_id, mesa_data in self.sistema_mesas.mesas.items():
                mesa = mesa_data[0]
                estado = "🟢 Libre" if mesa['estado'] == 'libre' else "🟠 Ocupada"
                todas_mesas.append((mesa_id, mesa))
                print(f"{len(todas_mesas)}. {mesa['nombre']} [{estado}]")
                if mesa['estado'] == 'ocupada':
                    mesas_ocupadas.append((mesa_id, mesa))

            print("\n0. Volver al menú principal")

            try:
                opcion = int(input("\nSeleccione una mesa para ver detalles (número): "))
                if opcion == 0:
                    return
                
                if 1 <= opcion <= len(todas_mesas):
                    mesa_id, mesa = todas_mesas[opcion - 1]
                    self._mostrar_detalles_mesa(mesa_id, mesa)
                else:
                    print("ℹ️   Opción inválida")
            except ValueError:
                print("Por favor ingrese un número válido")

    def _mostrar_detalles_mesa(self, mesa_id, mesa):
        """Muestra los detalles de una mesa específica."""
        print(f"\n=== DETALLES DE {mesa['nombre']} ===")
        print(f"Estado: {'🟢 Libre' if mesa['estado'] == 'libre' else '🟠 Ocupada'}")
        
        if mesa['estado'] == 'ocupada':
            # Mostrar pedidos por cliente
            for cliente_key, cliente in mesa.items():
                if not isinstance(cliente, dict) or 'pedidos' not in cliente:
                    continue
                    
                nombre_cliente = cliente.get('nombre', cliente_key)
                pedidos = cliente['pedidos']
                
                if not pedidos:
                    continue
                
                print(f"\nPedidos de {nombre_cliente}:")
                
                # Pedidos en preparación
                print("\n--- PEDIDOS EN PREPARACIÓN ---")
                hay_en_preparacion = False
                clientes_en_preparacion = {}
                
                for pedido in pedidos:
                    if pedido.get('estado_cocina') == self.estados_pedido['en_preparacion']:
                        if nombre_cliente not in clientes_en_preparacion:
                            clientes_en_preparacion[nombre_cliente] = []
                        clientes_en_preparacion[nombre_cliente].append(pedido)
                        hay_en_preparacion = True
                
                if hay_en_preparacion:
                    for nombre_cliente, pedidos in clientes_en_preparacion.items():
                        for pedido in pedidos:
                            print(f"• {pedido['cantidad']}x {pedido['nombre']}")
                            print(f"  Hora: {pedido['hora']}")
                            if 'notas' in pedido and pedido['notas']:
                                print(f"  Notas: {', '.join(pedido['notas'])}")
                else:
                    print("(No hay pedidos en preparación)")
                
                # Pedidos pendientes
                print("\n--- PEDIDOS PENDIENTES ---")
                hay_pendientes = False
                clientes_pendientes = {}
                
                for pedido in pedidos:
                    if pedido.get('estado_cocina') == self.estados_pedido['pendiente']:
                        if nombre_cliente not in clientes_pendientes:
                            clientes_pendientes[nombre_cliente] = []
                        clientes_pendientes[nombre_cliente].append(pedido)
                        hay_pendientes = True
                
                if hay_pendientes:
                    for nombre_cliente, pedidos in clientes_pendientes.items():
                        for pedido in pedidos:
                            print(f"• {pedido['cantidad']}x {pedido['nombre']}")
                            if 'notas' in pedido and pedido['notas']:
                                print(f"  Notas: {', '.join(pedido['notas'])}")
                else:
                    print("(No hay pedidos pendientes)")

    def obtener_detalles_mesa(self, mesa_id):
        """Obtiene los detalles de una mesa específica."""
        mesa_data = self.sistema_mesas.obtener_mesa(mesa_id)
        if not mesa_data:
            return None

        mesa = mesa_data[0]
        pedidos = []
        
        # Obtener pedidos del cliente_1
        if 'cliente_1' in mesa and 'pedidos' in mesa['cliente_1']:
            for pedido in mesa['cliente_1']['pedidos']:
                pedido_info = {
                    'id': pedido['id'],
                    'nombre': pedido['nombre'],
                    'cantidad': pedido['cantidad'],
                    'precio': pedido['precio'],
                    'estado_cocina': pedido['estado_cocina'],
                    'hora': pedido.get('hora', ''),
                    'notas': pedido.get('notas', []),
                    'mozo': pedido.get('mozo', 'Sin asignar'),
                    'pagado': pedido.get('pagado', False)
                }
                pedidos.append(pedido_info)
        
        return {
            'id': mesa_id,
            'nombre': mesa['nombre'],
            'estado': mesa['estado'],
            'pedidos': pedidos
        }

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