import psycopg2
import sys

import psycopg2.errorcodes
import psycopg2.extras 
from datetime import datetime

def connect_db():
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='youtubemusic',
            user='usuario',
            password='clave'
        )
        conn.autocommit = False
        return conn
    except psycopg2.Error as e:
        print(f"Error de conexión: {e}")
        sys.exit(1)

def disconnect_db(conn):
    conn.commit()
    conn.close()
    print("Desconectado de la base de datos.")

# Alta: Engadir usuario
def add_usuario(conn):
    print("Alta nuevo usuario:")
    snombre = input("Nombre: ")
    scorreo = input("Correo electrónico: ")
    spseudonimo = input("Pseudónimo: ")
    spassword = input("Contraseña: ")
    sdata_nacemento = input("Fecha de nacimiento (AAAA-MM-DD): ")

    nombre = None if snombre == "" else snombre
    correo = None if scorreo == "" else scorreo
    pseudonimo = None if spseudonimo == "" else spseudonimo
    password = None if spassword == "" else spassword
    if sdata_nacemento == "":
        data_nacemento = None
    else:
        try:
            data_nacemento =  datetime.strptime(sdata_nacemento, "%Y-%m-%d").date()
        except ValueError as e:
            print(f"Error: Formato de fecha inválido. Detalles: {e}")
            pass


    sql = '''
    INSERT INTO Usuario (nombre, correo, pseudonimo, password, fechaNacimiento)
    VALUES (%s, %s, %s, %s, %s)
    '''

    conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (nombre, correo, pseudonimo, password, data_nacemento))
            conn.commit()
            print("Usuario nuevo creado.")
    except psycopg2.Error as e:
        if e.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
            if e.diag.constraint_name == "usuario_correo_key":
                print(f"El correo {correo} ya esta registrado")
            else:
                print(f"El pseudonimo {pseudonimo} ya está en uso")
        elif e.pgcode == psycopg2.errorcodes.NOT_NULL_VIOLATION:
            if e.diag.column_name == "nombre":
                print("El nombre es obligatorio")
            elif e.diag.column_name == "correo":
                print("El correo es obligatorio")
            elif e.diag.column_name == "pseudonimo":
                print("El pseudonimo es obligatorio")
            elif e.diag.column_name == "password":
                print("La contraseña es obligatoria")
            else:
                print("La fecha es obligatoria")
        else:
            print(f"Erro {e.pgcode}: {e.pgerror}")
        conn.rollback()

# Alta: Engadir artista
def add_artista(conn):
    print("Alta nuevo artista:")
    nombre = input("Nombre artista: ")
    descripcion = input("Descripción (opcional): ")
    nacionalidade = input("Nacionalidad: ")
    tipo = input("Tipo (solista, grupo...): ")
    seguidores = input("Número de seg   uidores: ")
    ranking = input("Ranking: ")

    sql = '''
    INSERT INTO Artista (nombre, descripcion, nacionalidad, tipo, numeroSeguidores, ranking)
    VALUES (%s, %s, %s, %s, %s, %s)
    '''
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (nombre, descripcion or None, nacionalidade, tipo, seguidores, ranking))
            conn.commit()
            print("Artista nuevo creado.")
    except psycopg2.Error as e:
        print(f"Error al crear artista: {e.pgerror}")
        conn.rollback()

#Baja: Eliminar usuario por su id
def delete_usuario(conn):
    print("Eliminar usuario:")
    id_usuario = input("ID usuario: ")
    sql = "DELETE FROM Usuario WHERE idUsuario = %s"

    try:
        with conn.cursor() as cur:
            cur.execute(sql, (id_usuario,))
            if cur.rowcount == 0:
                print("No existe ningún usuario con ese ID.")
            else:
                conn.commit()
                print("Usuario eliminado correctamente.")
    except psycopg2.Error as e:
        print(f"Error al eliminar usuario: {e.pgerror}")
        conn.rollback()

#Update: Actualizar ranking de artista
def update_ranking_artista(conn):
    print("Actualizar ranking de un artista (valor independente):")
    id_artista = input("ID artista: ")
    novo_ranking = input("Nuevo valor de ranking: ")

    sql = "UPDATE Artista SET ranking = %s WHERE idArtista = %s"
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (novo_ranking, id_artista))
            if cur.rowcount == 0:
                print("No se encontro el artista.")
            else:
                conn.commit()
                print("Ranking actualizado correctamente.")
    except psycopg2.Error as e:
        print(f"Error al actualizar ranking: {e.pgerror}")
        conn.rollback()

#Update: Aumentar manualmente seguidores de un artista en un 20%
def aumentar_seguidores_artista(conn):
    print("Aumentar seguidores de un artista en un 20%:")
    id_artista = input("ID artista: ")

    sql = "UPDATE Artista SET numeroSeguidores = numeroSeguidores * 1.2 WHERE idArtista = %s"
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (id_artista,))
            if cur.rowcount == 0:
                print("No se encontro el artista.")
            else:
                conn.commit()
                print("Seguidores aumentados correctamente.")
    except psycopg2.Error as e:
        print(f"Error al aumentar seguidores: {e.pgerror}")
        conn.rollback()


#Funcionalidade 1: Crear unha canción e gardala ao mesmo tempo
def crear_y_guardar_cancion(conn):
    print("Crear canción e guardarla para un usuario:")
    id_usuario = input("ID usuario: ")
    id_artista = input("ID artista: ")
    titulo = input("Título canción: ")
    duracion = input("Duración (en milisegundos): ")
    fecha_publicacion = input("Fecha de publicación (AAAA-MM-DD): ")
    genero = input("Género: ")
    categoria = input("Categoría: ")

    sql_insert = '''
    INSERT INTO Cancion (idArtista, titulo, tiempoDuracion, fechaPublicacion, genero, categoria)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING idCancion;
    '''
    sql_guarda = '''
    INSERT INTO Guarda (idUsuario, idCancion)
    VALUES (%s, %s)
    '''
    try:
        with conn.cursor() as cur:
            cur.execute(sql_insert, (id_artista, titulo, duracion, fecha_publicacion, genero, categoria))
            id_cancion = cur.fetchone()[0]
            cur.execute(sql_guarda, (id_usuario, id_cancion))
            conn.commit()
            print("Canción creada y guardada correctamente.")
    except psycopg2.Error as e:
        print(f"Error en la transacción: {e.pgerror}")
        conn.rollback()

# Funcionalidade 2: Crear artista e a súa primeira canción
def crear_artista_con_cancion(conn):
    print("Crear artista y canción inicial:")
    nombre = input("Nombre artista: ")
    descripcion = input("Descripción (opcional): ")
    nacionalidade = input("Nacionalidad: ")
    tipo = input("Tipo (solista, grupo...): ")
    seguidores = input("Número de seguidores: ")
    ranking = input("Ranking: ")

    titulo = input("Título da canción: ")
    duracion = input("Duración (en milisegundos): ")
    fecha_publicacion = input("Fecha de publicación (AAAA-MM-DD): ")
    genero = input("Género: ")
    categoria = input("Categoría: ")

    sql_artista = '''
    INSERT INTO Artista (nombre, descripcion, nacionalidad, tipo, numeroSeguidores, ranking)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING idArtista;
    '''
    sql_cancion = '''
    INSERT INTO Cancion (idArtista, titulo, tiempoDuracion, fechaPublicacion, genero, categoria)
    VALUES (%s, %s, %s, %s, %s, %s)
    '''
    try:
        with conn.cursor() as cur:
            cur.execute(sql_artista, (nombre, descripcion or None, nacionalidade, tipo, seguidores, ranking))
            id_artista = cur.fetchone()[0]
            cur.execute(sql_cancion, (id_artista, titulo, duracion, fecha_publicacion, genero, categoria))
            conn.commit()
            print("Artista e canción creados correctamente.")
    except psycopg2.Error as e:
        print(f"Erro na transacción: {e.pgerror}")
        conn.rollback()

# Consulta 1: Ver datos de un artista por ID (devuelve 1 fila)
def ver_artista_por_id(conn):
    print("Consultar artista por ID:")
    id_artista = input("ID del artista: ")
    sql = "SELECT * FROM Artista WHERE idArtista = %s"
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (id_artista,))
            artista = cur.fetchone()
            if artista:
                print(f"ID: {artista[0]}, Nombre: {artista[1]}, Nacionalidad: {artista[3]}, Tipo: {artista[4]}, Seguidores: {artista[5]}, Ranking: {artista[6]}")
            else:
                print("Artista no encontrado.")
    except psycopg2.Error as e:
        print(f"Error en la consulta: {e.pgerror}")
        conn.rollback()

# Consulta 2: Ver canciones guardadas por un usuario (varias filas)
def ver_canciones_usuario(conn):
    print("Consultar canciones guardadas por un usuario:")
    id_usuario = input("ID del usuario: ")
    sql = '''
    SELECT c.idCancion, c.titulo
    FROM Cancion c
    JOIN Guarda g ON c.idCancion = g.idCancion
    WHERE g.idUsuario = %s
    '''
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (id_usuario,))
            rows = cur.fetchall()
            if not rows:
                print("El usuario no tiene canciones guardadas.")
            else:
                print("Canciones guardadas:")
                for row in rows:
                    print(f"ID: {row[0]}, Título: {row[1]}")
    except psycopg2.Error as e:
        print(f"Error en la consulta: {e.pgerror}")
        conn.rollback()


# Menú principal
def menu(conn):
    while True:
        print("""
--- MENÚ ---
1 - Crear usuario
2 - Crear artista
3 - Eliminar usuario
4 - Actualizar ranking de artista (valor independente)
5 - Aumentar seguidores de artista en un 20% (valor baseado)
6 - Crear canción y guardarla
7 - Crear artista y canción inicial
8 - Ver artista por ID
9 - Ver canciones guardadas por un usuariocertificado digital
q - Saír
""")
        opcion = input("Opción: ")
        if opcion == "1":
            add_usuario(conn)
        elif opcion == "2":
            add_artista(conn)
        elif opcion == "3":
            delete_usuario(conn)
        elif opcion == "4":
            update_ranking_artista(conn)
        elif opcion == "5":
            aumentar_seguidores_artista(conn)
        elif opcion == "6":
            crear_y_guardar_cancion(conn)
        elif opcion == "7":
            crear_artista_con_cancion(conn)
        elif opcion == "8":
            ver_artista_por_id(conn)
        elif opcion == "9":
            ver_canciones_usuario(conn)
        elif opcion == "q":
            break
        else:
            print("Opción no válida")

def main():
    conn = connect_db()
    print("Conectado a la base de datos.")
    menu(conn)
    disconnect_db(conn)

if __name__ == '__main__':
    main()