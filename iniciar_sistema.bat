@echo off
setlocal enabledelayedexpansion

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado.
    echo Por favor, instale Python 3.8 o superior desde https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Verificar si git está instalado
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git no está instalado.
    echo Por favor, instale Git desde https://git-scm.com/downloads
    pause
    exit /b 1
)

REM Crear entorno virtual si no existe
if not exist venv (
    echo Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
call venv\Scripts\activate

REM Instalar/actualizar dependencias
pip install -r requirements.txt

REM Intentar actualizar desde GitHub
echo.
echo Buscando actualizaciones...
git fetch origin main
git rev-parse HEAD >temp1
git rev-parse origin/main >temp2
fc temp1 temp2 >nul
if errorlevel 1 (
    echo Se encontraron actualizaciones disponibles.
    
    REM Verificar contraseña si es necesario
    python actualizar_sistema.py
    if errorlevel 1 (
        echo.
        echo No se pudo verificar la identidad. La actualización ha sido cancelada.
        del temp1 temp2
        pause
        exit /b 1
    )
    
    REM Proceder con la actualización
    git pull origin main
    if errorlevel 1 (
        echo.
        echo Error al actualizar. Por favor, contacte al administrador.
        del temp1 temp2
        pause
        exit /b 1
    )
    echo.
    echo Sistema actualizado exitosamente.
) else (
    echo El sistema está actualizado.
)

del temp1 temp2

REM Mostrar la IP del servidor
echo.
echo Direcciones IP disponibles:
ipconfig | findstr "IPv4"
echo.
echo El servidor estará disponible en: http://[TU-IP]:5000
echo Para acceder desde otros dispositivos en la red, usa la dirección IP de esta computadora

REM Iniciar el sistema
echo.
echo Iniciando sistema...
start /B python app.py

REM Esperar 2 segundos
timeout /t 2 /nobreak >nul

REM Abrir el navegador en localhost
start http://localhost:5000

echo.
echo Sistema iniciado correctamente.
echo Para acceder desde otros dispositivos en la red LAN, usa http://[TU-IP]:5000
echo Para cerrar, presione Ctrl+C en esta ventana.

REM Mantener la ventana abierta
cmd /k 