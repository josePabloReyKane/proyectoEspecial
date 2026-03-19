from sqlalchemy import Column, Integer, Date, String, ForeignKey
from sqlalchemy.orm import relationship
from config.db import Base

class DocentePrograma(Base):
    __tablename__ = "DocentePrograma"

    id_docente = Column(Integer, ForeignKey("Docentes.id_docente"), primary_key=True)
    id_programa = Column(Integer, ForeignKey("Programas.id_programa"), primary_key=True)

    docente = relationship("Docente", back_populates="programas")
    programa = relationship("Programa", back_populates="docentes")


class Matricula(Base):
    __tablename__ = "Matriculas"

    id_matricula = Column(Integer, primary_key=True, autoincrement=True)
    id_estudiante = Column(Integer, ForeignKey("Estudiantes.id_estudiante"), nullable=False)
    id_programa = Column(Integer, ForeignKey("Programas.id_programa"), nullable=False)
    id_docente = Column(Integer, ForeignKey("Docentes.id_docente"), nullable=False)
    fecha = Column(Date, nullable=False)
    estado = Column(String(20), nullable=False)

    estudiante = relationship("Estudiante", back_populates="matriculas")
    programa = relationship("Programa", back_populates="matriculas")
    docente = relationship("Docente", back_populates="matriculas")
