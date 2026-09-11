import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class Config:
    # Clave de seguridad para formularios y sesiones
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave_por_defecto'
    
    # Obtener URL de base de datos
    db_url = os.environ.get('DATABASE_URL')
    
    # Si DATABASE_URL no está configurada o si apunta a localhost, usará SQLite por defecto
    if not db_url or 'localhost' in db_url or '127.0.0.1' in db_url:
        db_url = 'sqlite:///gestion_obras.db'

    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False