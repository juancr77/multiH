from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, Text, DECIMAL
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Configuración de la base de datos
class DatabaseSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DatabaseSingleton, cls).__new__(cls, *args, **kwargs)
            cls._instance._engine = None
            cls._instance._Session = None
        return cls._instance

    def __init__(self):
        if not self._engine:
            DATABASE_URL = "mysql+pymysql://root:@localhost:3306/multihome"
            self._engine = create_engine(DATABASE_URL, echo=False)
            self._Session = sessionmaker(bind=self._engine)

    def get_session(self):
        if not self._Session:
            raise Exception("Database connection not initialized.")
        return self._Session()

Base = declarative_base()

# Tablas ORM
class Administrador(Base):
    __tablename__ = 'Administrador'
    idAdmin = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    telefono = Column(String(15))
    email = Column(String(100), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

class Propietario(Base):
    __tablename__ = 'Propietario'
    idPropietario = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    telefono = Column(String(15))
    email = Column(String(100))
    direccion = Column(String(255))
    fecha_registro = Column(Date, nullable=False)

class Seguro(Base):
    __tablename__ = 'Seguro'
    idS = Column(Integer, primary_key=True, autoincrement=True)
    detalle = Column(String(255))

class Estatus(Base):
    __tablename__ = 'Estatus'
    idEstatus = Column(Integer, primary_key=True, autoincrement=True)
    detalle = Column(String(255))

class Propiedad(Base):
    __tablename__ = 'Propiedad'
    idPro = Column(Integer, primary_key=True, autoincrement=True)
    ciudad = Column(String(100), nullable=False)
    estado = Column(String(100), nullable=False)
    codigo_postal = Column(String(10), nullable=False)
    precio = Column(DECIMAL(10, 2), nullable=False)
    num_recamaras = Column(Integer, nullable=False)
    num_banos = Column(Integer, nullable=False)
    idSeguro = Column(Integer, ForeignKey('Seguro.idS'))
    imagen = Column(String(10000), nullable=True)  # Ahora guarda la ruta como texto

    seguro = relationship('Seguro')

class Construccion(Base):
    __tablename__ = 'Construccion'
    idCons = Column(Integer, primary_key=True, autoincrement=True)
    idSfK1 = Column(Integer, ForeignKey('Seguro.idS'))
    idPropietario = Column(Integer, ForeignKey('Propietario.idPropietario'), nullable=False)
    materiales_usados = Column(String(255))
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date)
    estado_construccion = Column(String(50))

    seguro = relationship('Seguro')
    propietario = relationship('Propietario')

class Mudanza(Base):
    __tablename__ = 'Mudanza'
    idMud = Column(Integer, primary_key=True, autoincrement=True)
    idSfK2 = Column(Integer, ForeignKey('Seguro.idS'))
    idPropietario = Column(Integer, ForeignKey('Propietario.idPropietario'), nullable=False)
    empresa_mudanza = Column(String(100))
    fecha_mudanza = Column(Date, nullable=False)
    costo = Column(DECIMAL(10, 2))
    comentarios = Column(Text)

    seguro = relationship('Seguro')
    propietario = relationship('Propietario')

class Venta(Base):
    __tablename__ = 'Venta'
    idVenta = Column(Integer, primary_key=True, autoincrement=True)
    idProfk = Column(Integer, ForeignKey('Propiedad.idPro'))
    idEstatusfk = Column(Integer, ForeignKey('Estatus.idEstatus'))
    idPropietario = Column(Integer, ForeignKey('Propietario.idPropietario'), nullable=False)
    fecha_venta = Column(Date, nullable=False)

    propiedad = relationship('Propiedad')
    estatus = relationship('Estatus')
    propietario = relationship('Propietario')

# Inicialización de la base de datos
if __name__ == "__main__":
    db_singleton = DatabaseSingleton()
    engine = db_singleton._engine
    Base.metadata.create_all(engine)  # Crear tablas si no existen

    print("Tablas creadas exitosamente.")
