# Sistema de Restaurante

## Requisitos Previos
1. Python 3.8 o superior
   - Descargar de: https://www.python.org/downloads/
   - **IMPORTANTE**: Durante la instalación, marcar la opción "Add Python to PATH"
2. Git
   - Descargar de: https://git-scm.com/downloads
   - Necesario para las actualizaciones automáticas

## Configuración Inicial (Solo para el desarrollador)
1. Crear un repositorio en GitHub
2. Modificar el archivo `iniciar_sistema.bat` y reemplazar `TU_USUARIO` con tu nombre de usuario de GitHub
3. Subir el código inicial:
   ```bash
   git init
   git add .
   git commit -m "Versión inicial"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/sistema-restaurante.git
   git push -u origin main
   ```

## Instrucciones de Instalación

### Método Simple (Recomendado)
1. Simplemente haga doble clic en el archivo `iniciar_sistema.bat`
2. El script se encargará de:
   - Verificar que Python y Git estén instalados
   - Descargar la última versión del código desde GitHub
   - Crear un entorno virtual
   - Instalar todas las dependencias necesarias
   - Iniciar el sistema

### Método Manual
Si prefiere instalar manualmente:
1. Abra una terminal en esta carpeta
2. Clone el repositorio: `git clone https://github.com/TU_USUARIO/sistema-restaurante.git`
3. Cree un entorno virtual: `python -m venv venv`
4. Active el entorno virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
5. Instale las dependencias: `pip install -r requirements.txt`
6. Inicie el sistema: `python app.py`

## Actualizaciones
- El sistema verificará automáticamente si hay actualizaciones cada vez que se inicie
- Para actualizar manualmente en cualquier momento:
  1. Cierre el sistema si está en ejecución
  2. Vuelva a ejecutar `iniciar_sistema.bat`

## Desarrollo y Modificaciones
Para hacer cambios en el sistema:
1. Realice sus modificaciones en la PC principal
2. Suba los cambios a GitHub:
   ```bash
   git add .
   git commit -m "Descripción de los cambios"
   git push origin main
   ```
3. En las PCs que ejecuten el sistema, los cambios se descargarán automáticamente al iniciar

## Uso del Sistema
1. Una vez iniciado, abra su navegador web
2. Vaya a: http://localhost:5000
3. El sistema estará listo para usar

## Solución de Problemas
- Si recibe un error de Python no encontrado, asegúrese de que Python esté instalado y agregado al PATH
- Si recibe un error de Git no encontrado, asegúrese de que Git esté instalado
- Si hay problemas con los permisos, intente ejecutar el script como administrador
- Para problemas con las actualizaciones, verifique su conexión a internet
- Para cualquier otro error, verifique que todos los archivos estén en su lugar

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

