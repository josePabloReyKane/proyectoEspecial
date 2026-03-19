CREATE DATABASE Universidad;
GO
 
USE Universidad;
GO
 

-- TABLAS DE SEGURIDAD Y USUARIOS
 
-- Tabla de Roles
CREATE TABLE Rol (
    id_rol INT PRIMARY KEY IDENTITY(1,1),
    codigo VARCHAR(20) UNIQUE NOT NULL,  -- ADMIN, AUDITOR, OPERADOR, DOCENTE, ESTUDIANTE
    descripcion VARCHAR(100) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo'
);
GO
 
-- Tabla de Persona (datos personales de cualquier usuario del sistema)
CREATE TABLE Persona (
    id_persona INT PRIMARY KEY IDENTITY(1,1),
    identificacion VARCHAR(20) UNIQUE NOT NULL,
    nombre_completo VARCHAR(150) NOT NULL,
    email VARCHAR(100) UNIQUE,
    telefono VARCHAR(20),
    direccion VARCHAR(200),
    fecha_registro DATETIME DEFAULT GETDATE(),
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo'  -- Activo, Inactivo, Suspendido
);
GO
 
-- Tabla de Usuarios (autenticación - FK a Persona)
CREATE TABLE Usuario (
    id_usuario INT PRIMARY KEY IDENTITY(1,1),
    usuario VARCHAR(50) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    id_persona INT NOT NULL UNIQUE,  -- Relación 1:1 con Persona
    id_rol INT NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo',
    ultimo_acceso DATETIME NULL,
    
    CONSTRAINT FK_Usuario_Persona FOREIGN KEY (id_persona) REFERENCES Persona(id_persona),
    CONSTRAINT FK_Usuario_Rol FOREIGN KEY (id_rol) REFERENCES Rol(id_rol)
);
GO
 

-- TABLAS ESPECÍFICAS POR TIPO DE PERSONA

 
-- Tabla de Profesiones
CREATE TABLE Profesion (
    id_profesion INT PRIMARY KEY IDENTITY(1,1),
    codigo VARCHAR(20) UNIQUE NOT NULL,
    descripcion VARCHAR(100) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo'
);
GO
 
-- Tabla de Administradores (hereda de Persona vía Usuario)
CREATE TABLE Admin (
    id_admin INT PRIMARY KEY IDENTITY(1,1),
    id_persona INT NOT NULL UNIQUE,
    cargo VARCHAR(100),
    fecha_contratacion DATE DEFAULT GETDATE(),
    
    CONSTRAINT FK_Admin_Persona FOREIGN KEY (id_persona) REFERENCES Persona(id_persona)
);
GO
 
-- Tabla de Docentes (hereda de Persona)
CREATE TABLE Docente (
    id_docente INT PRIMARY KEY IDENTITY(1,1),
    id_persona INT NOT NULL UNIQUE,
    id_profesion INT NOT NULL,
    especialidad VARCHAR(100),
    
    CONSTRAINT FK_Docente_Persona FOREIGN KEY (id_persona) REFERENCES Persona(id_persona),
    CONSTRAINT FK_Docente_Profesion FOREIGN KEY (id_profesion) REFERENCES Profesion(id_profesion)
);
GO
 
-- Tabla de Estudiantes (hereda de Persona)
CREATE TABLE Estudiante (
    id_estudiante INT PRIMARY KEY IDENTITY(1,1),
    id_persona INT NOT NULL UNIQUE,
    carnet VARCHAR(20) UNIQUE NOT NULL,
    fecha_nacimiento DATE,
    
    CONSTRAINT FK_Estudiante_Persona FOREIGN KEY (id_persona) REFERENCES Persona(id_persona)
);
GO
 

-- TABLAS ACADÉMICAS
 
-- Tabla de Programas/Cursos
CREATE TABLE Programa (
    id_programa INT PRIMARY KEY IDENTITY(1,1),
    codigo VARCHAR(20) UNIQUE NOT NULL,
    descripcion VARCHAR(150) NOT NULL,
    horario VARCHAR(100),
    precio_matricula DECIMAL(10,2) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo'
);
GO
 
-- Tabla de Materias por Programa
CREATE TABLE Materia (
    id_materia INT PRIMARY KEY IDENTITY(1,1),
    codigo VARCHAR(20) NOT NULL,
    descripcion VARCHAR(150) NOT NULL,
    id_programa INT NOT NULL,
    cuatrimestre INT,
    precio DECIMAL(10,2) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo',
    
    CONSTRAINT FK_Materia_Programa FOREIGN KEY (id_programa) REFERENCES Programa(id_programa),
    CONSTRAINT UQ_Materia_Codigo_Programa UNIQUE (codigo, id_programa)
);
GO
 
-- Tabla de Asignación Docente a Programas
CREATE TABLE DocentePrograma (
    id_docente INT NOT NULL,
    id_programa INT NOT NULL,
    fecha_asignacion DATE DEFAULT GETDATE(),
    
    PRIMARY KEY (id_docente, id_programa),
    CONSTRAINT FK_DP_Docente FOREIGN KEY (id_docente) REFERENCES Docente(id_docente),
    CONSTRAINT FK_DP_Programa FOREIGN KEY (id_programa) REFERENCES Programa(id_programa)
);
GO
 
-- Tabla de Matrículas
CREATE TABLE Matricula (
    id_matricula INT PRIMARY KEY IDENTITY(1,1),
    id_estudiante INT NOT NULL,
    id_programa INT NOT NULL,
    id_docente INT NOT NULL,
    fecha_matricula DATE NOT NULL DEFAULT GETDATE(),
    periodo VARCHAR(20) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Activo',
    
    CONSTRAINT FK_Matricula_Estudiante FOREIGN KEY (id_estudiante) REFERENCES Estudiante(id_estudiante),
    CONSTRAINT FK_Matricula_Programa FOREIGN KEY (id_programa) REFERENCES Programa(id_programa),
    CONSTRAINT FK_Matricula_Docente FOREIGN KEY (id_docente) REFERENCES Docente(id_docente),
    CONSTRAINT UQ_Matricula UNIQUE (id_estudiante, id_programa, periodo)
);
GO
 
-- Tabla de Detalle de Matrícula por Materias
CREATE TABLE MatriculaMateria (
    id_matricula_materia INT PRIMARY KEY IDENTITY(1,1),
    id_matricula INT NOT NULL,
    id_materia INT NOT NULL,
    estado VARCHAR(20) DEFAULT 'Activo',
    
    CONSTRAINT FK_MM_Matricula FOREIGN KEY (id_matricula) REFERENCES Matricula(id_matricula),
    CONSTRAINT FK_MM_Materia FOREIGN KEY (id_materia) REFERENCES Materia(id_materia),
    CONSTRAINT UQ_MatriculaMateria UNIQUE (id_matricula, id_materia)
);
GO
 

-- TABLAS DE FACTURACIÓN

 
-- Tabla de Formas de Pago
CREATE TABLE FormaPago (
    id_forma_pago INT PRIMARY KEY IDENTITY(1,1),
    codigo VARCHAR(20) UNIQUE NOT NULL,
    descripcion VARCHAR(100) NOT NULL,
    estado VARCHAR(20) DEFAULT 'Activo'
);
GO
 
-- Tabla de Facturación
CREATE TABLE Facturacion (
    id_factura INT PRIMARY KEY IDENTITY(1,1),
    id_matricula INT NOT NULL,
    id_forma_pago INT NOT NULL,
    monto_total DECIMAL(10,2) NOT NULL,
    fecha_factura DATETIME DEFAULT GETDATE(),
    estado VARCHAR(20) DEFAULT 'Activo',
    
    CONSTRAINT FK_Factura_Matricula FOREIGN KEY (id_matricula) REFERENCES Matricula(id_matricula),
    CONSTRAINT FK_Factura_FormaPago FOREIGN KEY (id_forma_pago) REFERENCES FormaPago(id_forma_pago)
);
GO


-- TABLAS DE AUDITORÍA

 
-- Tabla de Tipos de Movimiento para Auditoría
CREATE TABLE TipoMovimiento (
    id_tipo_movimiento INT PRIMARY KEY IDENTITY(1,1),
    codigo VARCHAR(20) UNIQUE NOT NULL,
    descripcion VARCHAR(150) NOT NULL,
    estado VARCHAR(20) DEFAULT 'Activo'
);
GO
 
-- Tabla de Auditoría
CREATE TABLE Auditoria (
    id_auditoria INT PRIMARY KEY IDENTITY(1,1),
    id_usuario INT NOT NULL,
    id_tipo_movimiento INT NOT NULL,
    fecha DATETIME NOT NULL DEFAULT GETDATE(),
    tabla_afectada VARCHAR(50),
    registro_id INT,
    detalles VARCHAR(500),
    
    CONSTRAINT FK_Auditoria_Usuario FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario),
    CONSTRAINT FK_Auditoria_TipoMovimiento FOREIGN KEY (id_tipo_movimiento) REFERENCES TipoMovimiento(id_tipo_movimiento)
);
GO
 

-- INSERTS DE DATOS DE PRUEBA

 
-- Roles
INSERT INTO Rol (codigo, descripcion) VALUES
('ADMIN', 'Administrador del sistema'),
('AUDITOR', 'Auditor'),
('OPERADOR', 'Operador'),
('DOCENTE', 'Profesor'),
('ESTUDIANTE', 'Alumno');
GO
 
-- Personas (datos personales)
INSERT INTO Persona (identificacion, nombre_completo, email, telefono, direccion) VALUES
('111111111', 'Carlos Admin Pérez', 'carlos.admin@universidad.cr', '8888-1111', 'San José, Centro'),
('222222222', 'María Auditora Rojas', 'maria.auditora@universidad.cr', '8888-2222', 'Heredia, Santo Domingo'),
('333333333', 'Juan Operador Mora', 'juan.operador@universidad.cr', '8888-3333', 'Alajuela, San Ramón'),
('444444444', 'Roberto Méndez Pérez', 'roberto.mendez@universidad.cr', '8888-4444', 'Cartago, Paraíso'),
('555555555', 'Ana María Solano', 'ana.solano@email.com', '8888-5555', 'San José, Hatillo'),
('666666666', 'Pedro Ramírez Mora', 'pedro.ramirez@email.com', '8888-6666', 'Alajuela, San Rafael');
GO
 
-- Usuarios (contraseña: '123456')
INSERT INTO Usuario (usuario, contrasena, id_persona, id_rol) VALUES
('carlos', '123456', 1, 1),  -- Admin
('maria', '123456', 2, 2),   -- Auditora
('juan', '123456', 3, 3),    -- Operador
('roberto', '123456', 4, 4), -- Docente
('ana', '123456', 5, 5),     -- Estudiante
('pedro', '123456', 6, 5);   -- Estudiante
GO
 
-- Admins
INSERT INTO Admin (id_persona, cargo) VALUES
(1, 'Administrador General');
GO
 
-- Profesiones
INSERT INTO Profesion (codigo, descripcion) VALUES
('ING-SIS', 'Ingeniería en Sistemas'),
('LIC-ADM', 'Administración'),
('LIC-CONT', 'Contaduría');
GO
 
-- Docentes
INSERT INTO Docente (id_persona, id_profesion, especialidad) VALUES
(4, 1, 'Bases de Datos');
GO
 
-- Estudiantes
INSERT INTO Estudiante (id_persona, carnet, fecha_nacimiento) VALUES
(5, '2024001', '2000-05-15'),
(6, '2024002', '2001-08-22');
GO
 
-- Programas
INSERT INTO Programa (codigo, descripcion, horario, precio_matricula) VALUES
('DIP-SIS', 'Diplomado en Sistemas', 'Nocturno', 150000),
('DIP-ADM', 'Diplomado en Administración', 'Nocturno', 145000);
GO
 
-- Materias
INSERT INTO Materia (codigo, descripcion, id_programa, cuatrimestre, precio) VALUES
('PROG-I', 'Programación I', 1, 1, 85000),
('BD-I', 'Bases de Datos I', 1, 1, 85000);
GO
 
-- DocentePrograma
INSERT INTO DocentePrograma (id_docente, id_programa) VALUES
(1, 1);
GO