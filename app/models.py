from app.extensions import db
from datetime import datetime

class Obra(db.Model):
    __tablename__ = 'obras'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    presupuesto_inicial = db.Column(db.Numeric(12, 2), nullable=False)
    estado = db.Column(db.String(50), default='En curso') # Opciones: En curso, Finalizada, Pausada
    activo = db.Column(db.Boolean, default=True) # Para borrado lógico
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación: Una obra puede tener muchos materiales asociados
    materiales_obra = db.relationship('ObraMaterial', backref='obra', lazy=True)

class Material(db.Model):
    __tablename__ = 'materiales'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    unidad_medida = db.Column(db.String(50), nullable=False)
    precio_referencia = db.Column(db.Numeric(12, 2), nullable=False)
    activo = db.Column(db.Boolean, default=True)

class ObraMaterial(db.Model):
    __tablename__ = 'obra_material'
    
    id = db.Column(db.Integer, primary_key=True)
    obra_id = db.Column(db.Integer, db.ForeignKey('obras.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('materiales.id'), nullable=False)
    
    precio_congelado = db.Column(db.Numeric(12, 2), nullable=False)
    cantidad_presupuestada = db.Column(db.Float, nullable=False)
    cantidad_disponible = db.Column(db.Float, nullable=False)

    # Relaciones
    material = db.relationship('Material', backref='usos_en_obras')
    registros_uso = db.relationship('RegistroUso', backref='obra_material', lazy=True)

class RegistroUso(db.Model):
    __tablename__ = 'registro_uso'
    
    id = db.Column(db.Integer, primary_key=True)
    obra_material_id = db.Column(db.Integer, db.ForeignKey('obra_material.id'), nullable=False)
    cantidad_usada = db.Column(db.Float, nullable=False)
    costo_total = db.Column(db.Numeric(12, 2), nullable=False)
    fecha_uso = db.Column(db.DateTime, default=datetime.utcnow)
    notas = db.Column(db.Text, nullable=True)