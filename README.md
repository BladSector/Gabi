# Sistema de Restaurante

Sistema de gestión para restaurantes que permite manejar pedidos, mesas y pagos.

## Características

### Vista Mozos
- Gestión de mesas con estado en tiempo real
- Visualización de pedidos en cocina y entregados
- Sistema de pagos con selección individual de pedidos
- Cálculo automático del total a pagar
- Registro de tickets por fecha
- Gestión de pedidos con notas y cantidades
- Cancelación de pedidos
- Reinicio de mesas

### Vista Cocina
- Visualización de pedidos pendientes
- Marcado de pedidos como entregados
- Gestión de pedidos por mesa
- Visualización de notas especiales

## Estructura de Archivos

```
data/
  historial/           # Historial de tickets por fecha
    2024-03-21/       # Carpeta para cada día
      ticket_mesa1_2024-03-21_14-30-45.json
      ticket_mesa2_2024-03-21_15-15-30.json
    2024-03-22/       # Nueva carpeta para el siguiente día
      ticket_mesa1_2024-03-22_10-20-15.json
  menu.json           # Menú del restaurante
  mesas.json          # Estado de las mesas
```

## Funcionalidades Principales

### Gestión de Pedidos
- Agregar pedidos con notas especiales
- Modificar cantidades
- Cancelar pedidos
- Enviar pedidos a cocina
- Marcar pedidos como entregados

### Sistema de Pagos
- Selección individual de pedidos a pagar
- Cálculo automático del total
- Múltiples métodos de pago (efectivo/tarjeta)
- Registro de tickets por fecha
- Limpieza automática de mesa al pagar todo

### Gestión de Mesas
- Estado en tiempo real (libre/ocupada)
- Visualización de pedidos en cocina y entregados
- Reinicio de mesas
- Comentarios del camarero
- Notificaciones

## Tecnologías Utilizadas

- Backend: Python con Flask
- Frontend: HTML, CSS, JavaScript
- Base de datos: JSON
- UI: Bootstrap 5
- Notificaciones: SweetAlert2

## Instalación

1. Clonar el repositorio
2. Instalar dependencias:
```bash
pip install -r requirements.txt
```
3. Ejecutar la aplicación:
```bash
python app.py
```

## Uso

### Vista Mozos
1. Ingresar nombre del mozo
2. Gestionar pedidos de las mesas
3. Marcar pedidos como entregados
4. Procesar pagos
5. Reiniciar mesas cuando sea necesario

### Vista Cocina
1. Ver pedidos pendientes
2. Marcar pedidos como entregados
3. Gestionar pedidos por mesa

## Notas
- Los tickets se guardan automáticamente en carpetas por fecha
- Cada ticket contiene información detallada del pago
- El sistema mantiene un historial organizado por fecha
- Los pedidos pueden ser pagados parcialmente
- El sistema calcula automáticamente los totales

