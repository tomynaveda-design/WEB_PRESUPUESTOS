import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Clave de seguridad para formularios y sesiones
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave_por_defecto'
    
    # Obtener URL de base de datos directamente del .env (o usar SQLite por defecto)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///gestion_obras.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False