## Instalacion

pip install fastapi uvicorn
pip install mysql-connector-python

python-dotenv lo quisimos instalar para manejar varialbes de entorno pero no lo logramos, por lo que no se usa en el proyecto.

pip install python-dotenv

## Ejcución

uvicorn main:app --reload

## Scirpt de creación de tablas:

CREATE DATABASE IF NOT EXISTS bdd_obligatorio;
USE bdd_obligatorio;

CREATE TABLE login (
correo VARCHAR(255) PRIMARY KEY,
contraseña VARCHAR(255) NOT NULL
);

CREATE TABLE actividades (
id INT AUTO_INCREMENT PRIMARY KEY,
descripcion VARCHAR(255) NOT NULL,
costo DECIMAL(10, 2) NOT NULL
);

CREATE TABLE equipamiento (
id INT AUTO_INCREMENT PRIMARY KEY,
id_actividad INT NOT NULL,
descripcion VARCHAR(255) NOT NULL,
costo DECIMAL(10, 2) NOT NULL,
FOREIGN KEY (id_actividad) REFERENCES actividades(id)
);

CREATE TABLE instructores (
ci INT PRIMARY KEY,
nombre VARCHAR(50) NOT NULL,
apellido VARCHAR(50) NOT NULL
);

CREATE TABLE turnos (
id INT AUTO_INCREMENT PRIMARY KEY,
hora_inicio TIME NOT NULL,
hora_fin TIME NOT NULL
);

CREATE TABLE alumnos (
ci INT PRIMARY KEY,
nombre VARCHAR(50) NOT NULL,
apellido VARCHAR(50) NOT NULL,
fecha_nacimiento DATE NOT NULL,
telefono VARCHAR(20),
correo_electronico VARCHAR(255)
);

CREATE TABLE clase (
id INT AUTO_INCREMENT PRIMARY KEY,
ci_instructor INT NOT NULL,
id_actividad INT NOT NULL,
id_turno INT NOT NULL,
dictada BOOLEAN DEFAULT FALSE,
FOREIGN KEY (ci_instructor) REFERENCES instructores(ci),
FOREIGN KEY (id_actividad) REFERENCES actividades(id),
FOREIGN KEY (id_turno) REFERENCES turnos(id),
UNIQUE (ci_instructor, id_turno)
);

CREATE TABLE alumno_clase (
id_clase INT NOT NULL,
ci_alumno INT NOT NULL,
id_equipamiento INT,
FOREIGN KEY (id_clase) REFERENCES clase(id),
FOREIGN KEY (ci_alumno) REFERENCES alumnos(ci),
FOREIGN KEY (id_equipamiento) REFERENCES equipamiento(id),
UNIQUE (ci_alumno, id_clase)
);


tabla nueva creada:

CREATE TABLE tokens (
token VARCHAR(255) PRIMARY KEY,
correo VARCHAR(255),
FOREIGN KEY (correo) REFERENCES login(correo) ON DELETE CASCADE
);


## Inserts de datos maestros

INSERT INTO login (correo, contraseña) VALUES
('admin@admin.com', 'admin');

INSERT INTO actividades (descripcion, costo) VALUES
('Snowboard', 1500),
('Ski', 1200),
('Moto de nieve', 1800);

INSERT INTO equipamiento (id_actividad, descripcion, costo) VALUES
(1, 'Tabla de Snowboard', 500),
(1, 'Botas de Snowboard', 300),
(2, 'Esquíes', 400),
(2, 'Botas de Ski', 250),
(3, 'Casco', 100),
(3, 'Moto de nieve', 1000);

INSERT INTO instructores (ci, nombre, apellido) VALUES
(12345678, 'Juan', 'Sosa'),
(87654321, 'Ramiro', 'da Silva'),
(12348765, 'Mateo', 'Tonkovic');

INSERT INTO turnos (hora_inicio, hora_fin) VALUES
('09:00:00', '11:00:00'),
('12:00:00', '14:00:00'),
('16:00:00', '18:00:00');

INSERT INTO alumnos (ci, nombre, apellido, fecha_nacimiento, telefono, correo_electronico) VALUES
(11111111, 'Carlos', 'Pepe', '2000-05-15', '099111111', 'carlos@carlos.com'),
(22222222, 'Marta', 'Stuart', '1998-10-20', '099222222', 'marta@marta.com');

INSERT INTO clase (ci_instructor, id_actividad, id_turno, dictada) VALUES
(12345678, 1, 1, FALSE),
(87654321, 2, 2, FALSE);

INSERT INTO alumno_clase (id_clase, ci_alumno, id_equipamiento) VALUES
(1, 11111111, 1),
(2, 22222222, 3);
