import os
import sys
import json
import hashlib
import getpass
from pathlib import Path
import subprocess
import base64

def cargar_config():
    config_path = Path('config/config.json')
    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config = {
            'password_hash': None,
            'pc_registrada': None
        }
        guardar_config(config)
        return config
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def guardar_config(config):
    config_path = Path('config/config.json')
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

def get_pc_id():
    """Genera un ID único para la PC basado en características del sistema"""
    try:
        # En Windows
        if os.name == 'nt':
            output = subprocess.check_output('wmic csproduct get uuid').decode()
            return output.split('\n')[1].strip()
    except:
        pass
    
    # Fallback: usar nombre de la máquina
    return os.uname().nodename if hasattr(os, 'uname') else os.environ.get('COMPUTERNAME', 'unknown')

def hash_password(password):
    """Genera un hash seguro de la contraseña"""
    salt = b'restaurante_positivo'  # Salt fijo para este caso
    return base64.b64encode(hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000  # Número de iteraciones
    )).decode('utf-8')

def verificar_password(password, stored_hash):
    """Verifica si la contraseña coincide con el hash almacenado"""
    return hash_password(password) == stored_hash

def configurar_primera_vez():
    """Configura la contraseña por primera vez"""
    print("\n=== Configuración inicial del sistema ===")
    while True:
        password = getpass.getpass("Crear contraseña de administrador: ")
        if len(password) < 4:
            print("La contraseña debe tener al menos 4 caracteres.")
            continue
            
        confirm = getpass.getpass("Confirmar contraseña: ")
        if password != confirm:
            print("Las contraseñas no coinciden. Intente nuevamente.")
            continue
            
        break
    
    config = cargar_config()
    config['password_hash'] = hash_password(password)
    config['pc_registrada'] = get_pc_id()
    guardar_config(config)
    print("\n✅ Configuración completada exitosamente.")

def actualizar_sistema():
    """Maneja el proceso de actualización del sistema"""
    config = cargar_config()
    pc_actual = get_pc_id()
    
    # Si es la primera vez, configurar
    if not config['password_hash']:
        configurar_primera_vez()
        return True
    
    # Si es una PC diferente, pedir contraseña
    if pc_actual != config['pc_registrada']:
        print("\n⚠️ Nueva PC detectada - Se requiere verificación")
        intentos = 3
        while intentos > 0:
            password = getpass.getpass("Ingrese la contraseña de administrador: ")
            if verificar_password(password, config['password_hash']):
                # Actualizar PC registrada
                config['pc_registrada'] = pc_actual
                guardar_config(config)
                print("\n✅ Verificación exitosa - PC registrada")
                return True
            else:
                intentos -= 1
                if intentos > 0:
                    print(f"❌ Contraseña incorrecta. {intentos} intentos restantes.")
                else:
                    print("\n❌ Demasiados intentos fallidos. Contacte al administrador.")
                    return False
    
    return True

if __name__ == '__main__':
    if actualizar_sistema():
        print("\n🔄 Procediendo con la actualización del sistema...")
        # Aquí iría el código de actualización
        sys.exit(0)
    else:
        sys.exit(1) 