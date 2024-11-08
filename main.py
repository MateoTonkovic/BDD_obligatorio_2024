from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error

app = FastAPI()

class Instructor(BaseModel):
    ci: int
    nombre: str
    apellido: str

class Alumno(BaseModel):
    ci: int
    nombre: str
    apellido: str
    fecha_nacimiento: str 
    telefono: str
    correo_electronico: str

class Turno(BaseModel):
    hora_inicio: str  
    hora_fin: str

class Actividad(BaseModel):
    descripcion: str
    costo: float

class Equipamiento(BaseModel):
    id_actividad: int
    descripcion: str
    costo: float

class Clase(BaseModel):
    ci_instructor: int
    id_actividad: int
    id_turno: int
    dictada: bool

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            database="bdd_obligatorio",
            user="root",
            password="root"
        )
        if connection.is_connected():
            print("Conexión a la base de datos establecida")
        return connection
    except Error as e:
        print("Error al conectar con la base de datos", e)
        raise HTTPException(status_code=500, detail="Error en la conexión a la base de datos")

def close_db_connection(connection):
    if connection.is_connected():
        connection.close()
        print("Conexión a la base de datos cerrada")

# Endpoints with the updated Pydantic models

@app.post("/instructores/")
def crear_instructor(instructor: Instructor):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO instructores (ci, nombre, apellido) VALUES (%s, %s, %s)", 
                       (instructor.ci, instructor.nombre, instructor.apellido))
        connection.commit()
        return {"mensaje": "Instructor creado exitosamente"}
    finally:
        cursor.close()
        close_db_connection(connection)

@app.post("/alumnos/")
def crear_alumno(alumno: Alumno):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO alumnos (ci, nombre, apellido, fecha_nacimiento, telefono, correo_electronico) VALUES (%s, %s, %s, %s, %s, %s)", 
                       (alumno.ci, alumno.nombre, alumno.apellido, alumno.fecha_nacimiento, alumno.telefono, alumno.correo_electronico))
        connection.commit()
        return {"mensaje": "Alumno creado exitosamente"}
    finally:
        cursor.close()
        close_db_connection(connection)

@app.post("/turnos/")
def crear_turno(turno: Turno):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO turnos (hora_inicio, hora_fin) VALUES (%s, %s)", 
                       (turno.hora_inicio, turno.hora_fin))
        connection.commit()
        return {"mensaje": "Turno creado exitosamente"}
    finally:
        cursor.close()
        close_db_connection(connection)

@app.post("/actividades/")
def crear_actividad(actividad: Actividad):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO actividades (descripcion, costo) VALUES (%s, %s)", 
                       (actividad.descripcion, actividad.costo))
        connection.commit()
        return {"mensaje": "Actividad creada exitosamente"}
    finally:
        cursor.close()
        close_db_connection(connection)

@app.post("/equipamiento/")
def crear_equipamiento(equipamiento: Equipamiento):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO equipamiento (id_actividad, descripcion, costo) VALUES (%s, %s, %s)", 
                       (equipamiento.id_actividad, equipamiento.descripcion, equipamiento.costo))
        connection.commit()
        return {"mensaje": "Equipamiento creado exitosamente"}
    finally:
        cursor.close()
        close_db_connection(connection)

@app.post("/clases/")
def crear_clase(clase: Clase):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO clase (ci_instructor, id_actividad, id_turno, dictada) VALUES (%s, %s, %s, %s)", 
                       (clase.ci_instructor, clase.id_actividad, clase.id_turno, clase.dictada))
        connection.commit()
        return {"mensaje": "Clase creada exitosamente"}
    finally:
        cursor.close()
        close_db_connection(connection)
