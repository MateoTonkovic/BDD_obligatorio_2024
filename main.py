import mysql
from mysql.connector import Error
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets

from fastapi import Request
from fastapi.responses import JSONResponse      

security = HTTPBearer()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,                  
    allow_methods=["*"],                     
    allow_headers=["*"],  
)

class LoginRequest(BaseModel):
    correo: str
    contraseña: str

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
    
class InstructorUpdate(BaseModel):
    nombre: str
    apellido: str


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


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Allow login and OPTIONS requests without authentication
    if request.url.path in ["/login/"] or request.method == "OPTIONS":
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"detail": "Authorization header missing or invalid"})

    token = auth_header.split(" ")[1]  

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM tokens WHERE token = %s", (token,))
        valid_token = cursor.fetchone()
        if not valid_token:
            return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})
    finally:
        cursor.close()
        close_db_connection(connection)

    return await call_next(request)


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
 
            return instructor
        finally:
            cursor.close()
            close_db_connection(connection)
            
@app.put("/instructores/{ci}")
def actualizar_instructor(ci: int, instructor: InstructorUpdate):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            UPDATE instructores 
            SET 
                nombre = %s,
                apellido = %s
            WHERE ci = %s
        """, (
            instructor.nombre,
            instructor.apellido,
            ci
        ))
        connection.commit()
        
        return {"mensaje": "Instructor actualizado exitosamente"}
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
            
@app.put("/alumnos/{ci}")
def actualizar_alumno(ci: int, alumno: Alumno):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            UPDATE alumnos 
            SET 
                nombre = %s,
                apellido = %s,
                fecha_nacimiento = %s,
                telefono = %s,
                correo_electronico = %s
            WHERE ci = %s
        """, (
            alumno.nombre,
            alumno.apellido,
            alumno.fecha_nacimiento,
            alumno.telefono,
            alumno.correo_electronico,
            ci
        ))
        connection.commit()
                
        return {"mensaje": "Alumno actualizado exitosamente"}
    finally:
        cursor.close()
        close_db_connection(connection)




@app.get("/turnos/")
def obtener_turnos():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, SEC_TO_TIME(hora_inicio) AS hora_inicio, SEC_TO_TIME(hora_fin) AS hora_fin FROM turnos")
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
            SELECT 
                a.descripcion, 
                SUM(a.costo + IFNULL(e.costo, 0)) AS total_ingresos
            FROM actividades a
            LEFT JOIN clase c ON a.id = c.id_actividad
            LEFT JOIN alumno_clase ac ON c.id = ac.id_clase
            LEFT JOIN equipamiento e ON e.id = ac.id_equipamiento
            GROUP BY a.id
            ORDER BY total_ingresos DESC
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        close_db_connection(connection)

@app.get("/reportes/actividades-mas-alumnos")
def actividades_mas_alumnos():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                a.descripcion AS actividad,
                COUNT(ac.ci_alumno) AS total_alumnos
            FROM actividades a
            LEFT JOIN clase c ON a.id = c.id_actividad
            LEFT JOIN alumno_clase ac ON c.id = ac.id_clase
            GROUP BY a.id
            ORDER BY total_alumnos DESC
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
        close_db_connection(connection)

@app.get("/reportes/turnos-mas-clases")
def turnos_mas_clases():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                t.hora_inicio,
                t.hora_fin,
                COUNT(c.id) AS total_clases
            FROM turnos t
            LEFT JOIN clase c ON t.id = c.id_turno
            GROUP BY t.id
            ORDER BY total_clases DESC
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
        
@app.put("/actividades/{id}")
def actualizar_actividad(id: int, actividad: Actividad):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            UPDATE actividades 
            SET descripcion = %s, costo = %s
            WHERE id = %s
        """, (actividad.descripcion, actividad.costo, id))
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")
        return {"mensaje": "Actividad actualizada exitosamente"}
    finally:
        cursor.close()
        close_db_connection(connection)



@app.post("/clases/")
def crear_clase(clase: Clase):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO clase (ci_instructor, id_actividad, id_turno, dictada)
            VALUES (%s, %s, %s, %s)
        """, (clase.ci_instructor, clase.id_actividad, clase.id_turno, clase.dictada))
        connection.commit()
        return {"mensaje": "Clase creada exitosamente"}
    except mysql.connector.IntegrityError as e:
        if "Duplicate entry" in str(e):
            raise HTTPException(status_code=400, detail="Instructor ya tiene una clase en ese turno.")
        raise HTTPException(status_code=500, detail="Error al crear la clase")
    finally:
        cursor.close()
        close_db_connection(connection)
        
@app.get("/clases/")
def obtener_clases():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                c.id AS id_clase,
                c.dictada,
                i.ci AS ci_instructor,
                i.nombre AS nombre_instructor,
                i.apellido AS apellido_instructor,
                a.id AS id_actividad,
                a.descripcion AS descripcion_actividad,
                t.id AS id_turno,
                SEC_TO_TIME(t.hora_inicio) AS hora_inicio,
                SEC_TO_TIME(t.hora_fin) AS hora_fin
            FROM clase c
            INNER JOIN instructores i ON c.ci_instructor = i.ci
            INNER JOIN actividades a ON c.id_actividad = a.id
            INNER JOIN turnos t ON c.id_turno = t.id
        """)
        clases = cursor.fetchall()
        return clases
    finally:
        cursor.close()
        close_db_connection(connection)

@app.put("/clases/{id}")
def actualizar_clase(id: int, clase: Clase):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            UPDATE clase 
            SET 
                ci_instructor = %s,
                id_actividad = %s,
                id_turno = %s,
                dictada = %s
            WHERE id = %s
        """, (
            clase.ci_instructor,
            clase.id_actividad,
            clase.id_turno,
            clase.dictada,
            id
        ))
        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Clase no encontrada")
        
        return {"mensaje": "Clase actualizada exitosamente"}
    finally:
        cursor.close()
        close_db_connection(connection)



@app.post("/clases/{id_clase}/alumnos/")
def agregar_alumno_a_clase(id_clase: int, alumno_clase: AlumnoClase):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT c.id_turno
            FROM clase c
            WHERE c.id = %s
        """, (id_clase,))
        clase_turno = cursor.fetchone()
        
        cursor.execute("""
            SELECT ac.id_clase
            FROM alumno_clase ac
            INNER JOIN clase c ON ac.id_clase = c.id
            WHERE ac.ci_alumno = %s AND c.id_turno = %s
        """, (alumno_clase.ci_alumno, clase_turno['id_turno']))
        conflict = cursor.fetchone()
        
        if conflict:
            raise HTTPException(
                status_code=400,
                detail=f"El alumno ya está inscrito en otra clase en el turno {clase_turno['id_turno']}"
            )
        
        cursor.execute("""
            INSERT INTO alumno_clase (id_clase, ci_alumno, id_equipamiento)
            VALUES (%s, %s, %s)
        """, (id_clase, alumno_clase.ci_alumno, alumno_clase.id_equipamiento))
        connection.commit()
        
        return {"mensaje": "Alumno agregado a la clase"}
    finally:
        cursor.close()
        close_db_connection(connection)

@app.post("/login/")
def login(request: LoginRequest):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM login WHERE correo = %s AND contraseña = %s", 
                       (request.correo, request.contraseña))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        
        token = secrets.token_hex(16)
        cursor.execute("INSERT INTO tokens (token, correo) VALUES (%s, %s)", (token, request.correo))
        connection.commit()

        return {"mensaje": "Login exitoso", "token": token}
    finally:
        cursor.close()
        close_db_connection(connection)
        
@app.post("/logout/")
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        token = credentials.credentials
        cursor.execute("DELETE FROM tokens WHERE token = %s", (token,))
        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=401, detail="Token inválido o ya eliminado")
        
        return {"mensaje": "Logout exitoso"}
    finally:
        cursor.close()
        close_db_connection(connection)



@app.delete("/alumnos/{ci}")
def eliminar_alumno(ci: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM alumnos WHERE ci = %s", (ci,))
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Alumno no encontrado")
        return {"mensaje": "Alumno eliminado exitosamente"}
    finally:
        cursor.close()
        close_db_connection(connection)

@app.delete("/instructores/{ci}")
def eliminar_instructor(ci: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM instructores WHERE ci = %s", (ci,))
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Instructor no encontrado")
        return {"mensaje": "Instructor eliminado exitosamente"}
    finally:
        cursor.close()
        close_db_connection(connection)

@app.delete("/turnos/{id}")
def eliminar_turno(id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM turnos WHERE id = %s", (id,))
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Turno no encontrado")
        return {"mensaje": "Turno eliminado exitosamente"}
    finally:
        cursor.close()
        close_db_connection(connection)

@app.delete("/actividades/{id}")
def eliminar_actividad(id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM actividades WHERE id = %s", (id,))
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Actividad no encontrada")
        return {"mensaje": "Actividad eliminada exitosamente"}
    finally:
        cursor.close()
        close_db_connection(connection)

@app.delete("/clases/{id}")
def eliminar_clase(id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM clase WHERE id = %s", (id,))
        connection.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Clase no encontrada")
        return {"mensaje": "Clase eliminada exitosamente"}
    finally:
        cursor.close()
        close_db_connection(connection)

@app.get("/equipamientos/")
def obtener_equipamientos():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id, id_actividad, descripcion, costo
            FROM equipamiento
        """)
        equipamientos = cursor.fetchall()
        return equipamientos
    finally:
        cursor.close()
        close_db_connection(connection)
