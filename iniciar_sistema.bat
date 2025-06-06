@echo off
echo ===================================
echo Iniciando Sistema de Restaurante
echo ===================================

REM Verificar si Python está instalado
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado.
    echo Por favor, instale Python 3.8 o superior desde https://www.python.org/downloads/
    echo Asegúrese de marcar la opción "Add Python to PATH" durante la instalación.
    pause
    exit /b 1
)

REM Verificar si Git está instalado
git --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Git no está instalado.
    echo Por favor, instale Git desde https://git-scm.com/downloads
    pause
    exit /b 1
)

REM Verificar si es la primera ejecución (si no existe la carpeta .git)
if not exist ".git" (
    echo Primera ejecución detectada. Configurando repositorio Git...
    git init
    git remote add origin https://github.com/BladSector/Gabi.git
    git fetch
    git checkout -b main
    git pull origin main
)

REM Verificar actualizaciones
echo Verificando actualizaciones...
git fetch origin
git status | findstr "behind" > nul
if not errorlevel 1 (
    echo Se encontraron actualizaciones. Descargando...
    git pull origin main
    echo Actualizaciones instaladas correctamente.
) else (
    echo El sistema está actualizado.
)

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
call venv\Scripts\activate

REM Instalar/Actualizar dependencias
echo Instalando/Actualizando dependencias...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Iniciar el sistema
echo.
echo ===================================
echo Iniciando el servidor...
echo ===================================
echo.
echo El sistema estará disponible en: http://localhost:5000
echo.
echo Para cerrar el sistema, presione Ctrl+C
echo.
python app.py

pause 