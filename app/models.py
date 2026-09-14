from datetime import datetime
from app.extensions import db

class Obra(db.Model):
    __tablename__ = 'obras'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    presupuesto_inicial = db.Column(db.Numeric(12, 2), default=0.0)
    estado = db.Column(db.String(50), default='En curso')
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    materiales = db.relationship('ObraMaterial', backref='obra', cascade='all, delete-orphan', lazy=True)

    # --- PROPIEDADES DE FINANZAS DE LA OBRA ---
    @property
    def total_gastado(self):
        """Suma de lo efectivamente gastado en compras reales."""
        return sum(m.gasto_real for m in self.materiales)

    @property
    def total_estimado(self):
        """Suma del costo total estimado si se comprara el 100% de lo presupuestado."""
        return sum(m.costo_estimado_total for m in self.materiales)

    @property
    def saldo_disponible(self):
        """Presupuesto inicial menos lo gastado en compras reales."""
        presupuesto = float(self.presupuesto_inicial or 0.0)
        return presupuesto - self.total_gastado

    def __repr__(self):
        return f"<Obra {self.nombre}>"


class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False, unique=True)
    telefono = db.Column(db.String(50), nullable=True)
    activo = db.Column(db.Boolean, default=True)
    
    cotizaciones = db.relationship('CotizacionProveedor', backref='proveedor', lazy=True)

    def __repr__(self):
        return f"<Proveedor {self.nombre}>"


class ObraMaterial(db.Model):
    __tablename__ = 'obra_material'
    id = db.Column(db.Integer, primary_key=True)
    obra_id = db.Column(db.Integer, db.ForeignKey('obras.id'), nullable=False)
    codigo = db.Column(db.String(50), nullable=True)           
    articulo = db.Column(db.String(150), nullable=False)       
    marca = db.Column(db.String(100), nullable=True)            
    cantidad_presupuestada = db.Column(db.Float, nullable=False, default=0.0) 
    unidad_medida = db.Column(db.String(50), nullable=False, default='Unidades')    
    etapa = db.Column(db.String(100), nullable=True)            
    activo = db.Column(db.Boolean, default=True)

    # --- CONTROL DE COMPRAS ---
    cantidad_comprada = db.Column(db.Float, default=0.0)
    estado_compra = db.Column(db.String(20), default="Pendiente")

    # Relaciones
    cotizaciones = db.relationship('CotizacionProveedor', backref='obra_material', cascade='all, delete-orphan', lazy=True)
    registros_uso = db.relationship('RegistroUso', backref='obra_material', cascade='all, delete-orphan', lazy=True)

    # --- LÓGICA DE ESTADO Y COTIZACIONES ---
    def actualizar_estado_compra(self):
        """Actualiza el estado según lo comprado vs presupuestado."""
        comprado = self.cantidad_comprada or 0.0
        presupuestado = self.cantidad_presupuestada or 0.0

        if comprado <= 0:
            self.estado_compra = "Pendiente"
        elif comprado < presupuestado:
            self.estado_compra = "Parcial"
        else:
            self.estado_compra = "Completado"

    def cotizacion_mas_barata(self):
        """Devuelve la cotización con el menor precio unitario o None si no hay cotizaciones."""
        if not self.cotizaciones:
            return None
        return min(self.cotizaciones, key=lambda c: c.precio_unitario)

    # --- PROPIEDADES CALCULADAS DE COSTO ---
    @property
    def gasto_real(self):
        """Monto gastado en compras reales (cantidad_comprada * precio_unitario)."""
        mejor = self.cotizacion_mas_barata()
        if mejor and self.cantidad_comprada:
            return float(mejor.precio_unitario) * float(self.cantidad_comprada)
        return 0.0

    @property
    def costo_estimado_total(self):
        """Monto estimado completo (cantidad_presupuestada * precio_unitario)."""
        mejor = self.cotizacion_mas_barata()
        if mejor:
            return float(mejor.precio_total)
        return 0.0

    @property
    def total_usado(self):
        return sum(reg.cantidad_usada for reg in self.registros_uso if reg.cantidad_usada)

    @property
    def cantidad_disponible(self):
        """Stock real: Lo que se compró menos lo que se usó."""
        comprado = self.cantidad_comprada or 0.0
        return max(0.0, comprado - self.total_usado)

    @property
    def falta_comprar(self):
        presupuestado = self.cantidad_presupuestada or 0.0
        comprado = self.cantidad_comprada or 0.0
        return max(0.0, presupuestado - comprado)


class CotizacionProveedor(db.Model):
    __tablename__ = 'cotizacion_proveedor'
    id = db.Column(db.Integer, primary_key=True)
    obra_material_id = db.Column(db.Integer, db.ForeignKey('obra_material.id'), nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=False)
    precio_unitario = db.Column(db.Numeric(12, 2), nullable=False)
    precio_total = db.Column(db.Numeric(12, 2), nullable=False) 
    es_seleccionado = db.Column(db.Boolean, default=False)      

    def __repr__(self):
        return f"<CotizacionProveedor Mat:{self.obra_material_id} Prov:{self.proveedor_id}>"


class RegistroUso(db.Model):
    __tablename__ = 'registro_uso'
    id = db.Column(db.Integer, primary_key=True)
    obra_material_id = db.Column(db.Integer, db.ForeignKey('obra_material.id'), nullable=False)
    cantidad_usada = db.Column(db.Float, nullable=False)
    costo_total = db.Column(db.Numeric(12, 2), nullable=False, default=0.0)
    fecha_uso = db.Column(db.DateTime, default=datetime.utcnow)
    notas = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<RegistroUso Mat:{self.obra_material_id} Cant:{self.cantidad_usada}>"