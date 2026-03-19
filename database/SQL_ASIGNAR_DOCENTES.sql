USE Universidad
GO

-- Asigna todos los docentes existentes a todos los programas sin generar duplicados

INSERT INTO DocentePrograma (id_docente, id_programa)
SELECT d.id_docente, p.id_programa
FROM Docente d
CROSS JOIN Programa p
WHERE NOT EXISTS (
	SELECT 1 FROM DocentePrograma dp
	WHERE dp.id_docente = d.id_docente AND dp.id_programa = p.id_programa
);