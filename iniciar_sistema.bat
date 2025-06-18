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
    echo Git es necesario para las actualizaciones automáticas del sistema.
    pause
    exit /b 1
)

REM Variable para controlar si se convirtió de ZIP
set "converted_from_zip=false"

REM Detectar si es una descarga ZIP (sin carpeta .git) y convertirla en repositorio Git
if not exist .git (
    echo.
    echo DETECTADO: Descarga ZIP - Convirtiendo a repositorio Git para actualizaciones
    echo.
    echo Inicializando repositorio Git local...
    git init
    if errorlevel 1 (
        echo ERROR: No se pudo inicializar el repositorio Git.
        pause
        exit /b 1
    )
    
    echo Agregando repositorio remoto...
    git remote add origin https://github.com/BladSector/Gabi.git
    if errorlevel 1 (
        echo ERROR: No se pudo agregar el repositorio remoto.
        pause
        exit /b 1
    )
    
    echo Configurando rama principal...
    git branch -M main
    if errorlevel 1 (
        echo ERROR: No se pudo configurar la rama principal.
        pause
        exit /b 1
    )
    
    echo Agregando archivos al repositorio...
    git add .
    if errorlevel 1 (
        echo ERROR: No se pudieron agregar los archivos al repositorio.
        pause
        exit /b 1
    )
    
    echo Configurando identidad Git temporal...
    git config user.email "sistema@restaurante.local"
    git config user.name "Sistema Restaurante"
    if errorlevel 1 (
        echo ERROR: No se pudo configurar la identidad Git.
        pause
        exit /b 1
    )
    
    echo Creando commit inicial...
    git commit -m "Instalación inicial desde ZIP"
    if errorlevel 1 (
        echo ERROR: No se pudo crear el commit inicial.
        pause
        exit /b 1
    )
    
    echo Descargando última versión desde GitHub...
    git fetch origin main
    if errorlevel 1 (
        echo ERROR: No se pudo conectar con GitHub.
        echo Verifique su conexión a internet.
        pause
        exit /b 1
    )
    
    echo Actualizando a la última versión...
    git reset --hard origin/main
    if errorlevel 1 (
        echo ERROR: No se pudo actualizar a la última versión.
        pause
        exit /b 1
    )
    
    echo.
    echo ¡Conversión exitosa! Ahora puede recibir actualizaciones automáticas.
    echo.
    set "converted_from_zip=true"
)

REM Crear entorno virtual si no existe
if not exist venv (
    echo Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo Entorno virtual creado exitosamente.
)

REM Verificar que el entorno virtual existe
if not exist venv\Scripts\activate.bat (
    echo ERROR: El entorno virtual no se creó correctamente.
    echo Eliminando entorno virtual corrupto...
    rmdir /s /q venv
    echo Creando nuevo entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
)

REM Activar entorno virtual con mejor manejo de errores
echo Activando entorno virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual.
    echo Verificando permisos y estructura...
    if not exist venv\Scripts\python.exe (
        echo ERROR: Python no está disponible en el entorno virtual.
        echo Recreando entorno virtual...
        rmdir /s /q venv
        python -m venv venv
        call venv\Scripts\activate.bat
    )
)

REM Verificar que la activación fue exitosa
venv\Scripts\python.exe --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: El entorno virtual no está funcionando correctamente.
    pause
    exit /b 1
)

echo Entorno virtual activado correctamente.

REM Instalar/actualizar dependencias
echo Instalando dependencias...
venv\Scripts\pip.exe install -r requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias.
    pause
    exit /b 1
)

REM Buscar actualizaciones solo si no se acaba de convertir de ZIP
if "%converted_from_zip%"=="false" (
    echo.
    echo Buscando actualizaciones...
    git fetch origin main >nul 2>&1
    if errorlevel 1 (
        echo ERROR: No se pudo conectar con GitHub para buscar actualizaciones.
        echo Continuando sin verificar actualizaciones...
    ) else (
        git rev-parse HEAD >temp1 2>&1
        git rev-parse origin/main >temp2 2>&1
        fc temp1 temp2 >nul 2>&1
        if errorlevel 1 (
            echo Se encontraron actualizaciones disponibles.
            
            REM Verificar contraseña si es necesario
            venv\Scripts\python.exe actualizar_sistema.py
            if errorlevel 1 (
                echo.
                echo No se pudo verificar la identidad. La actualización ha sido cancelada.
                del temp1 temp2 2>&1
                pause
                exit /b 1
            )
            
            REM Proceder con la actualización forzada
            echo Descartando cambios locales y actualizando...
            git reset --hard
            git clean -fd
            git pull origin main --force
            if errorlevel 1 (
                echo.
                echo Error al actualizar. Por favor, contacte al administrador.
                del temp1 temp2 2>&1
                pause
                exit /b 1
            )
            echo.
            echo Sistema actualizado exitosamente.
        ) else (
            echo El sistema está actualizado.
        )
        
        del temp1 temp2 2>&1
    )
) else (
    echo.
    echo Sistema recién convertido desde ZIP - ya está actualizado.
)

REM Mostrar la IP del servidor
echo.
echo Direcciones IP disponibles:
ipconfig | findstr "IPv4"

REM Detectar la IP principal (la primera que no sea 127.0.0.1)
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr "IPv4"') do (
    set "ip=%%i"
    set "ip=!ip: =!"
    if not "!ip!"=="127.0.0.1" (
        if not defined main_ip (
            set "main_ip=!ip!"
        )
    )
)

echo.
echo ========================================
echo    SISTEMA INICIADO CORRECTAMENTE
echo ========================================
echo.
echo Para acceder desde esta computadora:
echo    http://localhost:5000
echo.
echo Para acceder desde otros dispositivos (celulares, tablets, otras PCs):
echo    http://!main_ip!:5000
echo.
echo ========================================

REM Iniciar el sistema
echo.
echo Iniciando sistema...
start /B venv\Scripts\python.exe app.py

REM Esperar 2 segundos
timeout /t 2 /nobreak >nul

REM Abrir el navegador en localhost
start http://localhost:5000

echo.
echo Sistema iniciado correctamente.
echo Para cerrar, presione Ctrl+C en esta ventana.

REM Mantener la ventana abierta
cmd /k 