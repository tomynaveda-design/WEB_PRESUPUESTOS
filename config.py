import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class Config:
    # Clave de seguridad para formularios y sesiones
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave_por_defecto'
    
    # URL de conexión a la base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Desactivamos una característica de SQLAlchemy que consume mucha memoria
    SQLALCHEMY_TRACK_MODIFICATIONS = False