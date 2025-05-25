# Sistema de Restaurante - Guía de Uso

## 📱 Acceso a la Aplicación
1. Abre tu navegador web
2. Ingresa la dirección: `https://tu-app.onrender.com`
3. Verás la pantalla principal donde se ingresa el nombre del mozo o "admin" para poder cancelar y reinciar mesas con el mapa de mesas

## 🪑 Gestión de Mesas

### Ver Estado de Mesas
- Las mesas se muestran en el mapa principal
- 🟢 Verde: Mesa libre
- 🟠 Naranja: Mesa ocupada

### Ocupar una Mesa
1. Haz clic en una mesa libre (verde)
2. Se abrirá el menú de pedidos
3. La mesa cambiará a ocupada (naranja)

## 🍽️ Gestión de Pedidos

### Agregar Pedidos
1. Selecciona una mesa ocupada
2. Haz clic en "Agregar Pedido"
3. Selecciona los platos del menú
4. Especifica la cantidad
5. Agrega notas de qué tipo de café si es necesario
6. Confirma el pedido

### Enviar a Cocina
1. Selecciona una mesa
2. Verás los pedidos pendientes
3. Marca los pedidos que quieres enviar
4. Haz clic en "Enviar a Cocina"

### Seguimiento de Pedidos
Los pedidos tienen diferentes estados:
- ⏳ Pendiente: Recién creado
- 👨‍🍳 En Preparación: Enviado a cocina
- ✅ Entregado: Listo y servido
- 💰 Pagado: Ya se realizó el pago (servidor)
- 🔴 Cancelado: Pedido anulado (servidor)

## 💰 Gestión de Pagos

### Realizar un Pago
1. Selecciona una mesa con pedidos entregados
2. Haz clic en "Gestionar Pago"
3. Selecciona los pedidos a pagar
4. Elige el método de pago:
   - Efectivo
   - Tarjeta
5. Confirma el pago

### Ver Tickets
- Los tickets se guardan automáticamente
- Se pueden encontrar en:
  - `data/tickets/[fecha]/` - Tickets en formato texto
  - `data/historial/[fecha]/` - Registro de pagos en JSON

## ⚙️ Funciones Adicionales

### Cancelar Pedidos (entrando como admin)
1. Selecciona una mesa
2. Encuentra el pedido a cancelar
3. Haz clic en "Cancelar"
4. Confirma la cancelación

### Liberar Mesa (entrando como admin)
1. Selecciona una mesa ocupada
2. Haz clic en "Reiniciar Mesa"
3. Confirma la acción
4. La mesa volverá a estado libre (verde)

## 💡 Consejos de Uso
- Siempre verifica el estado de los pedidos antes de enviarlos a cocina
- Asegúrate de marcar los pedidos como entregados cuando los sirvas
- Revisa los tickets generados para confirmar que los pagos se registraron correctamente (servidor)
- Mantén las mesas actualizadas para evitar confusiones

## 🔧 Solución de Problemas
Si encuentras algún error:
1. Verifica la conexión a internet 
2. Asegúrate de que la mesa no esté bloqueada
3. Intenta recargar la página 
4. Si el problema persiste, contacta al administrador (BS developers)

## 📋 Flujo de Trabajo Recomendado
1. Ocupar mesa cuando llegan los clientes
2. Tomar pedidos y enviarlos a cocina
3. Marcar pedidos como entregados al servirlos
4. Gestionar el pago cuando los clientes terminen
5. Liberar la mesa después del pago (automático)

## 📞 Soporte
Si necesitas ayuda adicional:
- Contacta al administrador del sistema (BS developers)
- Revisa la documentación técnica 
- Consulta con el equipo de soporte (BS developers)

---
BS developers - Santiago Tadeo López 
*Última actualización: [Fecha actual]*

