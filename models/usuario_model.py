from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from config.db import Base

class TipoUsuario(Base):
    __tablename__ = "TiposUsuario"

    id_tipo_usuario = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(20), unique=True, nullable=False)
    descripcion = Column(String(100), nullable=False)
    estado = Column(String(20), nullable=False)

    usuarios = relationship("Usuario", back_populates="tipo_usuario")


class Usuario(Base):
    __tablename__ = "Usuarios"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    usuario_sql = Column(String(50), unique=True, nullable=False)
    nombre_completo = Column(String(150), nullable=False)
    id_tipo_usuario = Column(Integer, ForeignKey("TiposUsuario.id_tipo_usuario"), nullable=False)
    estado = Column(String(20), nullable=False)

    tipo_usuario = relationship("TipoUsuario", back_populates="usuarios")
    auditorias = relationship("Auditoria", back_populates="usuario")
