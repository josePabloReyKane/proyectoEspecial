from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from config.db import Base

class Estudiante(Base):
    __tablename__ = "Estudiantes"

    id_estudiante = Column(Integer, primary_key=True, autoincrement=True)
    carnet = Column(String(20), unique=True, nullable=False)
    identificacion = Column(String(20), unique=True, nullable=False)
    nombre_completo = Column(String(150), nullable=False)
    direccion = Column(String(200))
    telefono = Column(String(20))
    estado = Column(String(20), nullable=False)

    matriculas = relationship("Matricula", back_populates="estudiante")
