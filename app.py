from flask import Flask, render_template, jsonify, request
from funciones.sistema_mesas import SistemaMesas
from funciones.sistema_pedidos_mozos import SistemaPedidosMozos
import json
import os
from datetime import datetime, timedelta
import shutil

app = Flask(__name__)
sistema_mesas = SistemaMesas()
sistema_pedidos = SistemaPedidosMozos(sistema_mesas)

def obtener_carpeta_fecha():
    """Obtiene la carpeta para la fecha actual o la crea si no existe"""
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    carpeta_fecha = os.path.join('data', 'historial', fecha_actual)
    
    # Crear estructura de carpetas si no existe
    if not os.path.exists(carpeta_fecha):
        os.makedirs(carpeta_fecha)
    
    return carpeta_fecha

def guardar_ticket(mesa_id, pedidos, total, metodo_pago):
    """Guarda un ticket en la carpeta de la fecha actual"""
    carpeta_fecha = obtener_carpeta_fecha()
    fecha_hora = datetime.now().strftime('%Y-%m-%d_%H-%M')
    
    # Crear contenido del ticket
    ticket = {
        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'mesa_id': mesa_id,
        'pedidos': pedidos,
        'total': total,
        'metodo_pago': metodo_pago
    }
    
    # Guardar ticket individual
    nombre_archivo = f'ticket_mesa{mesa_id}_{fecha_hora}.json'
    ruta_ticket = os.path.join(carpeta_fecha, nombre_archivo)
    with open(ruta_ticket, 'w', encoding='utf-8') as f:
        json.dump(ticket, f, ensure_ascii=False, indent=2)
    
    # Actualizar historial
    ruta_historial = os.path.join(carpeta_fecha, 'historial.json')
    try:
        with open(ruta_historial, 'r', encoding='utf-8') as f:
            historial = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        historial = []
    
    historial.append(ticket)
    
    with open(ruta_historial, 'w', encoding='utf-8') as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)
    
    return ruta_ticket

@app.route('/')
def index():
    return render_template('mozos.html')

@app.route('/api/menu')
def obtener_menu():
    try:
        with open('data/menu.json', 'r', encoding='utf-8') as f:
            menu_data = json.load(f)
            
        return jsonify({
            'success': True,
            'menu': menu_data['menu']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/mozos/mapa-mesas')
def obtener_mapa_mesas():
    try:
        mesas = sistema_mesas.obtener_mapa_mesas()
        return jsonify({
            'success': True,
            'data': mesas
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/mozos/mesas/<mesa_id>')
def obtener_detalles_mesa(mesa_id):
    try:
        detalles = sistema_pedidos.obtener_detalles_mesa(mesa_id)
        return jsonify({
            'success': True,
            'data': detalles
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/mozos/pedidos/<pedido_id>/cancelar', methods=['PUT'])
def cancelar_pedido(pedido_id):
    try:
        data = request.get_json()
        mesa_id = data.get('mesa_id')
        if not mesa_id:
            return jsonify({'success': False, 'error': 'Falta el id de la mesa'}), 400
        
        mesa_data = sistema_mesas.obtener_mesa(mesa_id)
        if not mesa_data:
            return jsonify({'success': False, 'error': 'Mesa no encontrada'}), 404
        
        mesa = mesa_data[0]
        pedidos = mesa.get('cliente_1', {}).get('pedidos', [])
        
        # Encontrar y eliminar el pedido
        mesa['cliente_1']['pedidos'] = [p for p in pedidos if p['id'] != pedido_id]
        
        # Si no quedan pedidos, liberar la mesa
        if not mesa['cliente_1']['pedidos']:
            mesa['estado'] = 'libre'
            mesa['cliente_1'] = {
                'pedidos': [],
                'contador_pedidos': 0
            }
            mesa['comentarios_camarero'] = []
            mesa['notificaciones'] = []
        
        sistema_mesas.guardar_mesas()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mesas/<mesa_id>/enviar-cocina', methods=['POST'])
def enviar_pedidos_cocina(mesa_id):
    try:
        data = request.get_json()
        pedidos = data.get('pedidos', [])
        mozo = data.get('mozo')
        
        sistema_pedidos.enviar_pedidos_cocina(mesa_id, pedidos, mozo)
        return jsonify({
            'success': True
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/mozos/mesas/<mesa_id>/reiniciar', methods=['PUT'])
def reiniciar_mesa(mesa_id):
    try:
        if sistema_mesas.reiniciar_mesa(mesa_id):
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'No se pudo reiniciar la mesa'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mozos/mesas/<mesa_id>/pedidos', methods=['GET'])
def obtener_pedidos_mesa(mesa_id):
    try:
        mesa_data = sistema_mesas.obtener_mesa(mesa_id)
        if not mesa_data:
            return jsonify({'success': False, 'error': 'Mesa no encontrada'}), 404

        mesa = mesa_data[0]
        if 'cliente_1' not in mesa or 'pedidos' not in mesa['cliente_1']:
            return jsonify({'success': True, 'pedidos': []})

        return jsonify({
            'success': True,
            'pedidos': mesa['cliente_1']['pedidos']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mozos/mesas/<mesa_id>/pagar', methods=['PUT'])
def pagar_mesa(mesa_id):
    try:
        data = request.get_json()
        print("\n=== INICIO PROCESO DE PAGO ===")
        print("Datos recibidos del cliente:", data)
        
        if not data:
            print("Error: No se recibieron datos")
            return jsonify({'success': False, 'error': 'No se proporcionaron datos'}), 400

        # Extraer y validar datos
        mesa_id_body = data.get('mesa_id')
        mozo = data.get('mozo')
        pedidos_info = data.get('pedidos_ids', [])  # Lista de {id, cantidad}
        metodo_pago = data.get('metodo_pago', 'efectivo')

        print(f"Mesa ID (URL): {mesa_id}")
        print(f"Mesa ID (Body): {mesa_id_body}")
        print(f"Mozo: {mozo}")
        print(f"Pedidos Info: {pedidos_info}")
        print(f"Método de pago: {metodo_pago}")

        if not mesa_id or not mozo:
            print("Error: Faltan datos requeridos")
            return jsonify({'success': False, 'error': 'Faltan datos requeridos'}), 400

        # Obtener datos de la mesa
        mesa_data = sistema_mesas.obtener_mesa(mesa_id)
        if not mesa_data:
            print(f"Error: Mesa {mesa_id} no encontrada")
            return jsonify({'success': False, 'error': 'Mesa no encontrada'}), 404

        mesa = mesa_data[0]
        print("\nDatos de la mesa:")
        print(f"Estado: {mesa['estado']}")
        print(f"Pedidos actuales: {mesa.get('cliente_1', {}).get('pedidos', [])}")
        
        if 'cliente_1' not in mesa or 'pedidos' not in mesa['cliente_1']:
            print("Error: No hay pedidos en la mesa")
            return jsonify({'success': False, 'error': 'No hay pedidos en la mesa'}), 400

        # Procesar pedidos seleccionados
        pedidos_a_pagar = []
        total = 0

        # Crear un diccionario para acceso rápido a la información de cantidad a pagar
        cantidades_a_pagar = {p['id']: p['cantidad'] for p in pedidos_info}

        # Lista para mantener los pedidos actualizados
        pedidos_actualizados = []

        # Procesar cada pedido original
        for pedido in mesa['cliente_1']['pedidos']:
            print(f"\nProcesando pedido: {pedido['id']}")
            print(f"Estado actual: {pedido['estado_cocina']}")
            
            pedido_actualizado = pedido.copy()
            
            if pedido['id'] in cantidades_a_pagar and pedido['estado_cocina'] == '🟡 Pendiente':
                cantidad_a_pagar = cantidades_a_pagar[pedido['id']]
                cantidad_original = pedido['cantidad']
                precio_unitario = pedido['precio']
                
                print(f"Cantidad a pagar: {cantidad_a_pagar}")
                print(f"Cantidad original: {cantidad_original}")
                print(f"Precio unitario: ${precio_unitario}")
                
                if cantidad_a_pagar > 0 and cantidad_a_pagar <= cantidad_original:
                    # Calcular precio total para la cantidad a pagar
                    precio_total = precio_unitario * cantidad_a_pagar
                    
                    # Crear pedido para el pago
                    pedido_pago = pedido.copy()
                    pedido_pago['cantidad'] = cantidad_a_pagar
                    pedido_pago['precio'] = precio_unitario
                    pedidos_a_pagar.append(pedido_pago)
                    total += precio_total
                    
                    # Actualizar la cantidad restante
                    cantidad_restante = cantidad_original - cantidad_a_pagar
                    if cantidad_restante > 0:
                        pedido_actualizado['cantidad'] = cantidad_restante
                        print(f"Quedan {cantidad_restante} unidades pendientes")
                        pedidos_actualizados.append(pedido_actualizado)
                    else:
                        pedido_actualizado['estado_cocina'] = '💰 Pagado'
                        pedidos_actualizados.append(pedido_actualizado)
                        print("Pedido completamente pagado")
            else:
                # Mantener pedidos que no se están pagando
                pedidos_actualizados.append(pedido_actualizado)

            print(f"Pedido procesado - Nuevo estado: {pedido_actualizado['estado_cocina']}")

        print("\nResumen de pago:")
        print(f"Pedidos a pagar: {len(pedidos_a_pagar)}")
        print(f"Total: ${total}")

        if not pedidos_a_pagar:
            print("Error: No hay pedidos válidos para pagar")
            return jsonify({'success': False, 'error': 'No hay pedidos válidos para pagar'}), 400

        # Registrar el pago en el sistema
        print("\nRegistrando pago en el sistema...")
        sistema_pedidos._registrar_pago(mesa_id, mesa, pedidos_a_pagar, total, metodo_pago)

        # Actualizar los pedidos de la mesa
        mesa['cliente_1']['pedidos'] = pedidos_actualizados

        # Verificar si quedan pedidos pendientes
        pedidos_pendientes = [p for p in pedidos_actualizados 
                            if p['estado_cocina'] == '🟡 Pendiente']

        print(f"\nPedidos pendientes restantes: {len(pedidos_pendientes)}")

        # Solo liberar la mesa si no quedan pedidos pendientes
        if not pedidos_pendientes:
            print("No quedan pedidos pendientes - Liberando mesa")
            mesa['estado'] = 'libre'
            mesa['cliente_1'] = {
                'pedidos': [],
                'contador_pedidos': 0
            }
            mesa['comentarios_camarero'] = []
            mesa['notificaciones'] = []

        # Guardar cambios
        print("\nGuardando cambios...")
        if not sistema_mesas.guardar_mesas():
            print("Error: No se pudieron guardar los cambios")
            return jsonify({'success': False, 'error': 'Error al guardar los cambios'}), 500

        print("\n=== FIN PROCESO DE PAGO ===")
        return jsonify({
            'success': True,
            'message': 'Pago procesado exitosamente',
            'total': total,
            'pedidos_pagados': len(pedidos_a_pagar)
        })

    except Exception as e:
        print("\n=== ERROR EN PROCESO DE PAGO ===")
        print(f"Error: {str(e)}")
        import traceback
        print("Traceback completo:")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/historial/diario')
def obtener_historial_diario():
    try:
        # Obtener parámetros de fecha
        fecha = request.args.get('fecha')
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        # Si no hay parámetros, usar fecha actual
        if not fecha and not fecha_inicio and not fecha_fin:
            fecha = datetime.now().strftime('%Y-%m-%d')
        
        historial = []
        
        # Función para procesar archivos de una fecha específica
        def procesar_fecha(fecha_str):
            carpeta_fecha = os.path.join('data', 'tickets', fecha_str)
            archivo_historial = os.path.join(carpeta_fecha, 'historial_diario.json')
            
            if os.path.exists(archivo_historial):
                with open(archivo_historial, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    # Agregar fecha a cada ticket
                    for ticket in datos:
                        ticket['fecha'] = fecha_str
                    return datos
            return []
        
        # Procesar según el tipo de filtro
        if fecha:
            # Filtro por día específico
            historial.extend(procesar_fecha(fecha))
        elif fecha_inicio and fecha_fin:
            # Filtro por rango de fechas
            fecha_actual = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fecha_final = datetime.strptime(fecha_fin, '%Y-%m-%d')
            
            while fecha_actual <= fecha_final:
                fecha_str = fecha_actual.strftime('%Y-%m-%d')
                historial.extend(procesar_fecha(fecha_str))
                fecha_actual += timedelta(days=1)
        
        return jsonify({
            'success': True,
            'historial': historial
        })
    except Exception as e:
        print(f"Error al obtener historial: {str(e)}")  # Agregamos log para debug
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/resumen-diario')
def resumen_diario():
    return render_template('resumen_diario.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 