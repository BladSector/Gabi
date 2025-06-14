# Sistema de Gestión de Restaurante

## Descripción
Sistema de gestión para restaurante que permite el manejo de pedidos, mesas y generación de informes de ventas.

## Características Principales

### Gestión de Pedidos y Mesas
- Control de estado de mesas
- Registro de pedidos por mesa
- Gestión de pagos en efectivo y tarjeta

### Informe de Ventas
El sistema incluye un panel de resumen de ventas con las siguientes características:
- Separación de fecha y hora en columnas independientes
- Formato de fecha mejorado (DD-MM-YYYY)
- Formato de hora simplificado (HH:MM)
- Precio unitario visible solo para pedidos con cantidad > 1
- Actualización en tiempo real (cada 2 segundos)
- Mejoras en la visualización de totales y porcentajes

### Estructura de Archivos
```
/data
  /tickets
    /{YYYY-MM-DD}/
      - historial_diario.json
      - ticket_mesaX_HHMMSS.json
```

## Tecnologías Utilizadas
- Backend: Python con Flask
- Frontend: HTML, JavaScript, Bootstrap
- Almacenamiento: Sistema de archivos JSON

## Uso
1. Acceder a la vista principal de mozos (/)
2. Para ver el resumen de ventas, acceder a (/resumen-diario)
3. Utilizar los filtros para visualizar diferentes períodos
4. Los datos se actualizarán automáticamente cada 2 segundos

## Próximas Mejoras Planificadas
- Exportación de informes a PDF/Excel
- Filtros adicionales por producto
- Gráficos estadísticos de ventas

# Sistema de Restaurante

## Requisitos Previos
1. Python 3.8 o superior
   - Descargar de: https://www.python.org/downloads/
   - **IMPORTANTE**: Durante la instalación, marcar la opción "Add Python to PATH"
2. Git
   - Descargar de: https://git-scm.com/downloads
   - Necesario para las actualizaciones automáticas

## Instrucciones de Instalación

### Método Simple (Recomendado)
1. Simplemente haga doble clic en el archivo `iniciar_sistema.bat`
2. El script se encargará de:
   - Verificar que Python y Git estén instalados
   - Descargar la última versión del código desde GitHub
   - Crear un entorno virtual (falta configurar)
   - Instalar todas las dependencias necesarias
   - Iniciar el sistema

### Método Manual
Si prefiere instalar manualmente:
1. Abra una terminal en esta carpeta
2. Clone el repositorio: `git clone https://github.com/BladSector/Gabi.git`
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
   ```git bash
   git add .
   git commit -m "Descripción de los cambios"
   git push (origin main)
   ```
3. En las PCs que ejecuten el sistema, los cambios se descargarán automáticamente al iniciar

## Solución de Problemas
- Si recibe un error de Python no encontrado, asegúrese de que Python esté instalado y agregado al PATH
- Si recibe un error de Git no encontrado, asegúrese de que Git esté instalado
- Si hay problemas con los permisos, intente ejecutar el script como administrador
- Para problemas con las actualizaciones, verifique su conexión a internet
- Para cualquier otro error, verifique que todos los archivos estén en su lugar

# Sistema de Restaurante - Guía de Uso

## Uso del Sistema
1. Una vez iniciado (iniciar_sistema.bat), abra su navegador web
2. Vaya a: http://localhost:5000
3. El sistema estará listo para usar

## 🪑 Gestión de Mesas

### Ver Estado de Mesas
- Las mesas se muestran en el mapa principal
- 🟢 Verde: Mesa libre
- 🟠 Naranja: Mesa ocupada

### Ocupar una Mesa
1. Haz clic en una mesa libre (verde)
2. Se abrirá el menú de pedidos
3. La mesa cambiará a ocupada si se agrega algín pedido (naranja)

## 🍽️ Gestión de Pedidos

### Agregar Pedidos
1. Selecciona una mesa ocupada
2. Haz clic en "Agregar Pedido"
3. Selecciona los platos del menú
4. Especifica la cantidad
5. Agrega notas de qué tipo de café si es necesario
6. Confirma el pedido

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

## ⚙️ Funciones Adicionales

### Cancelar Pedidos (como admin)
1. Selecciona una mesa
2. Encuentra el pedido a cancelar
3. Haz clic en "Cancelar"
4. Confirma la cancelación

### Liberar Mesa (como admin)
1. Selecciona una mesa ocupada
2. Haz clic en "Reiniciar Mesa"
3. Confirma la acción
4. La mesa volverá a estado libre (verde)


## 🔧 Solución de Problemas
Si encuentras algún error:
1. Verifica la conexión a internet 
2. Asegúrate de que la mesa no esté bloqueada
3. Intenta recargar la página 
4. Si el problema persiste, contacta al administrador (Santiago lópez)

## 📋 Flujo de Trabajo Recomendado
1. Tomar pedidos sobre una mesa
3. Marcar pedidos
4. Gestionar el pago cuando los clientes terminen
5. Liberar la mesa después del pago (automático)

## 📞 Soporte
Si necesitas ayuda adicional:
- Contacta al administrador del sistema (Santiago López)

---
STL developer - Santiago Tadeo López 
*Última actualización: [10/12/2025]*

