from app import create_app
from app.extensions import db
from app import models # Es vital importar los modelos para que SQLAlchemy los detecte

app = create_app()

with app.app_context():
    db.create_all()
    print("¡Las tablas se crearon exitosamente en la base de datos!")