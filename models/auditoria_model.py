from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from config.db import Base

class MovimientoAuditoria(Base):
    __tablename__ = "MovimientosAuditoria"

    id_movimiento = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(String(150), nullable=False)

    auditorias = relationship("Auditoria", back_populates="movimiento")


class Auditoria(Base):
    __tablename__ = "Auditoria"

    id_auditoria = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("Usuarios.id_usuario"), nullable=False)
    id_movimiento = Column(Integer, ForeignKey("MovimientosAuditoria.id_movimiento"), nullable=False)
    fecha = Column(DateTime, nullable=False, server_default=func.getdate())

    usuario = relationship("Usuario", back_populates="auditorias")
    movimiento = relationship("MovimientoAuditoria", back_populates="auditorias")
