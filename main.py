from fastapi import FastAPI, HTTPException
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from pydantic import BaseModel
import os

app = FastAPI()

class Alumno(BaseModel):
    ci: int
    nombre: str
    apellido: str
    fecha_nacimiento: str 
    telefono: str
    correo_electronico: str

class Instructor(BaseModel):
    ci: int
    nombre: str
    apellido: str

class Turno(BaseModel):
    hora_inicio: str
    hora_fin: str

class Actividad(BaseModel):
    descripcion: str
    costo: float

class Clase(BaseModel):
    ci_instructor: int
    id_actividad: int
    id_turno: int
    dictada: bool

class AlumnoClase(BaseModel):
    ci_alumno: int
    id_equipamiento: int

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
            
@app.get("/instructores/")
def obtener_instructores():
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM instructores")
            instructores = cursor.fetchall()
            return instructores
        finally:
            cursor.close()
            close_db_connection(connection)

@app.get("/instructores/{ci}")
def obtener_instructor(ci):
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM instructores WHERE ci = %s", (int(ci),))
            instructor = cursor.fetchone()
            if not instructor:
                raise HTTPException(status_code=404, detail="Instructor no encontrado")
            return instructor
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

@app.get("/alumnos/")
def obtener_alumnos():
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM alumnos")
            alumnos = cursor.fetchall()
            return alumnos
        finally:
            cursor.close()
            close_db_connection(connection)
            
@app.get("/alumnos/{alumno_id}")
async def obtener_alumno(alumno_id):
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM alumnos WHERE ci = %s", (int(alumno_id),))
            alumno = cursor.fetchone()
            
            if not alumno:
                raise HTTPException(status_code=404, detail="Alumno no encontrado")
            
            return alumno
        finally:
            cursor.close()
            close_db_connection(connection)



@app.get("/turnos/")
def obtener_turnos():
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM turnos")
            turnos = cursor.fetchall()
            return turnos
        finally:
            cursor.close()
            close_db_connection(connection)


@app.get("/actividades/")
def obtener_actividades():
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM actividades")
            actividades = cursor.fetchall()
            return actividades
        finally:
            cursor.close()
            close_db_connection(connection)

            
@app.get("/reportes/actividades-mas-ingresos")
def actividades_mas_ingresos():
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT a.descripcion, SUM(a.costo + IFNULL(e.costo, 0)) AS total_ingresos
                FROM actividades a
                LEFT JOIN alumno_clase ac ON a.id = ac.id_actividad
                LEFT JOIN equipamiento e ON e.id = ac.id_equipamiento
                GROUP BY a.id
                ORDER BY total_ingresos DESC
            """)
            return cursor.fetchall()
        finally:
            cursor.close()
            close_db_connection(connection)

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

@app.post("/clases/{id_clase}/alumnos/")
def agregar_alumno_a_clase(id_clase: int, alumno_clase: AlumnoClase):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO alumno_clase (id_clase, ci_alumno, id_equipamiento) VALUES (%s, %s, %s)", 
                       (id_clase, alumno_clase.ci_alumno, alumno_clase.id_equipamiento))
        connection.commit()
        return {"mensaje": "Alumno agregado a la clase"}
    finally:
        cursor.close()
        close_db_connection(connection)