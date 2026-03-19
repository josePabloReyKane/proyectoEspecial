from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from config.db import Base

class Programa(Base):
    __tablename__ = "Programa"

    id_programa = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(20), unique=True, nullable=False)
    descripcion = Column(String(150), nullable=False)
    precio_matricula = Column(DECIMAL(10,2), nullable=False)
    estado = Column(String(20), nullable=False)

    materias = relationship("Materia", back_populates="programa")
    docentes = relationship("DocentePrograma", back_populates="programa")
    matriculas = relationship("Matricula", back_populates="programa")


class Materia(Base):
    __tablename__ = "Materia"

    id_materia = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(20), nullable=False)
    descripcion = Column(String(150), nullable=False)
    id_programa = Column(Integer, ForeignKey("Programas.id_programa"), nullable=False)
    precio_cuatrimestre = Column(DECIMAL(10,2), nullable=False)
    estado = Column(String(20), nullable=False)

    programa = relationship("Programa", back_populates="materias")
