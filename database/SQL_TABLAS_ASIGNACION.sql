USE Universidad
GO

--- TABLA MAESTRA DE PERIODOS

CREATE TABLE Periodo (
    id_periodo    INT PRIMARY KEY IDENTITY(1,1),
    codigo        VARCHAR(20)  UNIQUE NOT NULL,  -- 2026-I, 2026-II, 2026-III
    descripcion   VARCHAR(100) NOT NULL,
    fecha_inicio  DATE         NOT NULL,
    fecha_fin     DATE         NOT NULL,
    estado        VARCHAR(20)  NOT NULL DEFAULT 'Activo',

    CONSTRAINT CK_Periodo_Fechas CHECK (fecha_fin > fecha_inicio)
);
GO

--- TABLA DE ESTADOS DE ASIGNACION

CREATE TABLE EstadoAsignacion (
    id_estado   INT PRIMARY KEY IDENTITY(1,1),
    codigo      VARCHAR(20)  UNIQUE NOT NULL,
    descripcion VARCHAR(100) NOT NULL,
    estado      VARCHAR(20)  NOT NULL DEFAULT 'Activo'
);
GO


-- TABLA DE ASIGNACION DOCENTE (nueva, reemplaza DocentePrograma para el Entregable 4)

CREATE TABLE AsignacionDocente (
    id_asignacion  INT PRIMARY KEY IDENTITY(1,1),
    id_docente     INT NOT NULL,
    id_programa    INT NOT NULL,
    id_periodo     INT NOT NULL,
    fecha_inicio   DATE NOT NULL,
    fecha_fin      DATE NOT NULL,
    id_estado      INT NOT NULL,

    CONSTRAINT FK_AD_Docente  FOREIGN KEY (id_docente)  REFERENCES Docente(id_docente),
    CONSTRAINT FK_AD_Programa FOREIGN KEY (id_programa) REFERENCES Programa(id_programa),
    CONSTRAINT FK_AD_Periodo  FOREIGN KEY (id_periodo)  REFERENCES Periodo(id_periodo),
    CONSTRAINT FK_AD_Estado   FOREIGN KEY (id_estado)   REFERENCES EstadoAsignacion(id_estado),
    CONSTRAINT UQ_Asignacion  UNIQUE (id_docente, id_programa, id_periodo)
);
GO


--- DATOS DE PRUEBA — PERIODOS 2026

INSERT INTO Periodo (codigo, descripcion, fecha_inicio, fecha_fin) VALUES
('2026-I',   'Primer Cuatrimestre 2026',   '2026-01-01', '2026-04-30'),
('2026-II',  'Segundo Cuatrimestre 2026',  '2026-05-01', '2026-08-10'),
('2026-III', 'Tercer Cuatrimestre 2026',   '2026-08-20', '2026-12-20');
GO


--- DATOS DE PRUEBA — ESTADOS DE ASIGNACION

INSERT INTO EstadoAsignacion (codigo, descripcion) VALUES
('ACTIVO',      'Activo'),
('INACTIVO',    'Inactivo'),
('SUSPENDIDO',  'Suspendido'),
('VACACIONES',  'Vacaciones');
GO


--- VERIFICACION

SELECT * FROM Periodo;
SELECT * FROM EstadoAsignacion;
GO