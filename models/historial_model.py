from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from config.db import Base

class MovimientoHistorial(Base):
    __tablename__ = "Tipo_Movimiento"

    id_tipo_movimiento = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(20), unique=True, nullable=False)
    descripcion = Column(String(150), nullable=False)

    estado = Column(String(20), nullable=False)
