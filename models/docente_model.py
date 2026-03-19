from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from config.db import Base

class Profesion(Base):
    __tablename__ = "Profesiones"

    id_profesion = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(String(100), nullable=False)
    estado = Column(String(20), nullable=False)

    docentes = relationship("Docente", back_populates="profesion")


class Docente(Base):
    __tablename__ = "Docentes"

    id_docente = Column(Integer, primary_key=True, autoincrement=True)
    identificacion = Column(String(20), unique=True, nullable=False)
    nombre_completo = Column(String(150), nullable=False)
    id_profesion = Column(Integer, ForeignKey("Profesiones.id_profesion"), nullable=False)
    estado = Column(String(20), nullable=False)

    profesion = relationship("Profesion", back_populates="docentes")
    programas = relationship("DocentePrograma", back_populates="docente")
    matriculas = relationship("Matricula", back_populates="docente")
