from app import create_app
from app.extensions import db
from app import models 

app = create_app()

with app.app_context():
    print("Eliminando tablas antiguas...")
    db.drop_all()
    print("Creando nuevas tablas con la estructura de la planilla...")
    db.create_all()
    print("¡Base de datos actualizada con éxito!")