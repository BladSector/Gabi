from flask import Flask, render_template, jsonify, request
from funciones.sistema_mesas import SistemaMesas
from funciones.sistema_pedidos_mozos import SistemaPedidosMozos
import json
import os
from datetime import datetime
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

def guardar_ticket(mesa_id, pedidos, total, metodo_pago, mozo):
    """Guarda un ticket en la carpeta de la fecha actual"""
    carpeta_fecha = obtener_carpeta_fecha()
    fecha_hora = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    # Crear contenido del ticket
    ticket = {
        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'mesa_id': mesa_id,
        'mozo': mozo,
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

@app.route('/api/mozos/pedidos/<pedido_id>/entregar', methods=['PUT'])
def marcar_pedido_entregado(pedido_id):
    try:
        data = request.get_json()
        mesa_id = data.get('mesa_id')
        if not mesa_id:
            return jsonify({'success': False, 'error': 'Falta el id de la mesa'}), 400
        mesa = sistema_mesas.obtener_mesa(mesa_id)
        if not mesa:
            return jsonify({'success': False, 'error': 'Mesa no encontrada'}), 404
        mesa_obj = mesa[0]
        pedidos = mesa_obj.get('cliente_1', {}).get('pedidos', [])
        encontrado = False
        for pedido in pedidos:
            if pedido['id'] == pedido_id:
                pedido['estado_cocina'] = '✅ Entregado'
                pedido['hora_entregado'] = datetime.now().strftime('%H:%M')
                encontrado = True
                break
        if not encontrado:
            return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404
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

@app.route('/api/mozos/pedidos/<pedido_id>/cancelar', methods=['PUT'])
def cancelar_pedido(pedido_id):
    try:
        data = request.get_json()
        mesa_id = data.get('mesa_id')
        if not mesa_id:
            return jsonify({'success': False, 'error': 'Falta el id de la mesa'}), 400
        mesa = sistema_mesas.obtener_mesa(mesa_id)
        if not mesa:
            return jsonify({'success': False, 'error': 'Mesa no encontrada'}), 404
        mesa_obj = mesa[0]
        pedidos = mesa_obj.get('cliente_1', {}).get('pedidos', [])
        encontrado = False
        for pedido in pedidos:
            if pedido['id'] == pedido_id:
                pedido['estado_cocina'] = '🔴 Cancelado'
                encontrado = True
                break
        if not encontrado:
            return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404
        sistema_mesas.guardar_mesas()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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
        print("Datos recibidos:", data)
        
        if not data:
            return jsonify({'success': False, 'error': 'No se proporcionaron datos'}), 400

        mesa_id = data.get('mesa_id')
        mozo = data.get('mozo')
        pedidos_ids = data.get('pedidos_ids', [])
        metodo_pago = data.get('metodo_pago', 'efectivo')

        print("Mesa ID:", mesa_id)
        print("Mozo:", mozo)
        print("Pedidos IDs:", pedidos_ids)

        if not mesa_id or not mozo:
            return jsonify({'success': False, 'error': 'Faltan datos requeridos'}), 400

        # Obtener datos de la mesa
        mesa_data = sistema_mesas.obtener_mesa(mesa_id)
        if not mesa_data:
            return jsonify({'success': False, 'error': 'Mesa no encontrada'}), 404

        mesa = mesa_data[0]
        print("Datos de la mesa:", mesa)
        
        if 'cliente_1' not in mesa or 'pedidos' not in mesa['cliente_1']:
            return jsonify({'success': False, 'error': 'No hay pedidos en la mesa'}), 400

        # Filtrar pedidos seleccionados
        pedidos_a_pagar = []
        total = 0

        # Agrupar pedidos por ID para manejar cantidades
        pedidos_por_id = {}
        for pedido_id in pedidos_ids:
            if pedido_id not in pedidos_por_id:
                pedidos_por_id[pedido_id] = 0
            pedidos_por_id[pedido_id] += 1

        print("Pedidos agrupados por ID:", pedidos_por_id)

        # Procesar cada pedido original
        for pedido in mesa['cliente_1']['pedidos']:
            print("Procesando pedido:", pedido)
            if pedido['id'] in pedidos_por_id and pedido['estado_cocina'] == '✅ Entregado':
                cantidad_a_pagar = pedidos_por_id[pedido['id']]
                cantidad_original = pedido['cantidad']
                
                # Si se paga la cantidad total
                if cantidad_a_pagar == cantidad_original:
                    pedido['estado_cocina'] = '💰 Pagado'
                    pedidos_a_pagar.append(pedido.copy())
                    total += pedido['precio'] * cantidad_a_pagar
                # Si se paga parcialmente
                else:
                    # Crear una copia del pedido para el pago
                    pedido_pago = pedido.copy()
                    pedido_pago['cantidad'] = cantidad_a_pagar
                    pedidos_a_pagar.append(pedido_pago)
                    total += pedido['precio'] * cantidad_a_pagar
                    
                    # Actualizar el pedido original
                    pedido['cantidad'] = cantidad_original - cantidad_a_pagar
                    # Si quedan unidades, mantener el estado como entregado
                    if pedido['cantidad'] > 0:
                        pedido['estado_cocina'] = '✅ Entregado'
                    else:
                        pedido['estado_cocina'] = '💰 Pagado'

                print("Pedido procesado:", pedido)
                print("Pedido a pagar:", pedidos_a_pagar[-1])

        print("Pedidos a pagar:", pedidos_a_pagar)
        print("Total:", total)

        if not pedidos_a_pagar:
            return jsonify({'success': False, 'error': 'No hay pedidos válidos para pagar'}), 400

        # Registrar el pago en el sistema original
        sistema_pedidos._registrar_pago(mesa_id, mesa, pedidos_a_pagar, total, metodo_pago)

        # Verificar si quedan pedidos por pagar
        pedidos_restantes = [p for p in mesa['cliente_1']['pedidos'] 
                           if p['estado_cocina'] == '✅ Entregado' 
                           and p['estado_cocina'] != '🔴 Cancelado'
                           and p['estado_cocina'] != '💰 Pagado']

        # Si no quedan pedidos por pagar, limpiar la mesa
        if not pedidos_restantes:
            mesa['estado'] = 'libre'
            # Limpiar los datos de la mesa
            mesa['cliente_1'] = {
                'pedidos': [],
                'contador_pedidos': 0
            }
            mesa['comentarios_camarero'] = []
            mesa['notificaciones'] = []

        # Guardar cambios
        if not sistema_mesas.guardar_mesas():
            return jsonify({'success': False, 'error': 'Error al guardar los cambios'}), 500

        return jsonify({
            'success': True,
            'message': 'Pago procesado exitosamente',
            'total': total,
            'pedidos_pagados': len(pedidos_a_pagar)
        })

    except Exception as e:
        print("Error en pagar_mesa:", str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 