import psycopg2
import sys

import psycopg2.errorcodes
import psycopg2.extras 
from datetime import datetime, date

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
            return


    sql = '''
    INSERT INTO Usuario (nombre, correo, pseudonimo, password, fechaNacimiento)
    VALUES (%s, %s, %s, %s, %s)
    '''

    conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED
    #usamos este nivel de asilamiento porque no necesitamos verificar datos antes de insertar
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
    snombre = input("Nombre artista: ")
    sdescripcion = input("Descripción (opcional): ")
    snacionalidade = input("Nacionalidad: ")
    stipo = input("Tipo (solista, grupo...): ")
    sseguidores = input("Número de seg   uidores: ")
    sranking = input("Ranking: ")

    nombre = None if snombre == "" else snombre
    descripcion = None if sdescripcion == "" else sdescripcion
    nacionalidade = None if snacionalidade == "" else snacionalidade
    tipo = None if stipo == "" else stipo

    try:
        seguidores = None if sseguidores == "" else int(sseguidores)
        ranking = None if sranking == "" else int(sranking)
    except ValueError as e:
        print("Error ranking y/o seguidores debe ser un entero.")
        return


    sql = '''
    INSERT INTO Artista (nombre, descripcion, nacionalidad, tipo, numeroSeguidores, ranking)
    VALUES (%s, %s, %s, %s, %s, %s)
    '''

    conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED
    #usamos este nivel de asilamiento porque no necesitamos verificar datos antes de insertar
    try:
        with conn.cursor() as cur:
            print(descripcion)
            cur.execute(sql, (nombre, descripcion, nacionalidade, tipo, seguidores, ranking))
            conn.commit()
            print("Artista nuevo creado.")
    except psycopg2.Error as e:
        if e.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
            print(f"El artista {nombre} ya existe")
        elif e.pgcode == psycopg2.errorcodes.NOT_NULL_VIOLATION:
            if e.diag.column_name == "nombre":
                print("El nombre del artista es obligatorio")
            elif e.diag.column_name == "nacionalidad":
                print("La nacionalidad es obligatoria")
            elif e.diag.column_name == "tipo":
                print("El tipo es obligatorio")
            elif e.diag.column_name == "numeroSeguirdores":
                print("El numero de seguidores es obligatorio")
            else:
                print("El ranking es obligatorio")
        elif e.pgcode == psycopg2.errorcodes.CHECK_VIOLATION:
            if e.diag.constraint_name == "ranking":
                print("El ranking no puede ser menor que 1")
            else:
                print("Un artista tiene que tener 0 o mas seguidores")
        else:
            print(f"Erro {e.pgcode}: {e.pgerror}")
        conn.rollback()

#Baja: Eliminar usuario por su id
def delete_usuario(conn):
    print("Eliminar usuario:")
    sid_usuario = input("ID usuario: ")
    if sid_usuario == "":
        print("el id de usuario no puede ser nulo")
        return
    else:
        try:
            id_usuario = int(sid_usuario)
        except ValueError as e:
            print("El codigo debe ser un numero")
            return
    sql = "DELETE FROM Usuario WHERE idUsuario = %s"
    sql2 = "SELECT nombre, correo FROM Usuario WHERE idUsuario = %s"
    
    conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED
    #Usamos este nivel de aislamiento porque no necesitamos verficar que el usuario no ha 
    #sido borrado por una transaccion anterior y elimina de forma segura las filas de otras tablas
    #dependientes
    try:
        with conn.cursor() as cur:
            cur.execute(sql2, (id_usuario,))
            if cur.rowcount == 0:
                print(f"No existe ningún usuario con id {id_usuario}.")
            else:
                row = cur.fetchone()
                verificacion = input(f"¿Seguro que quieres eliminar al usuario {row[0]} con id {id_usuario} y correo {row[1]}?(y/n)")
                if verificacion != "y":
                    print("Se cancelo la elminacion del usuario")
                else:
                   cur.execute(sql, (id_usuario,))
                   print(f"El usuario {row[0]} ha sido eliminado")
            conn.commit()
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
    print("Consultar artista por ID")
    id_artista = input("ID del artista: ")

    if (not id_artista.isdigit() and id_artista > 0) :
        print("El id del artista tiene que ser un numero entero positivo")
        return
    else:
        id_artista = int(id_artista) 

    sql = "SELECT idArtista, nombre, descripcion, nacionalidad, tipo, numeroSeguidores, ranking FROM Artista WHERE idArtista = %s"
    #Usamos este nivel de aislamiento porque solo queremos leer datos confirmados
    #y no vamos a escribir solo leer
    conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (id_artista,))
            artista = cur.fetchone()
            if artista:
                ###cambiar esta linea esta mal falta descripcion
                print(f"Id: {artista[0]}")
                print(f"Nombre: {artista[1]}")
                print(f"Descripcion: {artista[2]}")
                print(f"Nacionalida: {artista[3]}")
                print(f"Tipo: {artista[4]}")
                print(f"Numero Seguidores: {artista[5]}")
                print(f"Ranking: {artista[6]}")
            else:
                print(f"Artista con codigo {id_artista} no existe.")
            conn.commit()
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


def create_cancion(conn):
    print("Creacion nueva cancion")
    sidArtista = input("introduce el id del artista: ")
    stitulo = input("introduce el titulo de la cancion: ")
    stiempoDuracion = input("Introduce la duracion del cancion en segundos: ")
    sgenero = input("Introduce el genero: ")
    scatergoria = input("Introduce la categoria de la cancion: ")

    if not sidArtista.isdigit() or int(sidArtista) <= 0:
        print("El código debe ser un entero > 0")
        return
    idArtista = int(sidArtista)

    titulo = None if stitulo == "" else stitulo
    if not stiempoDuracion.isdigit() or int(stiempoDuracion) <= 0:
        print("El tiempo de duracion debe ser un numero > 0")
        return
    tiempoDuracion = int(stiempoDuracion)
    genero = None if sgenero == "" else sgenero
    categoria = None if scatergoria == "" else scatergoria

    sql = """
    INSERT INTO Cancion(idArtista, titulo, tiempoDuracion, fechaPublicacion, genero, categoria) 
    VALUES(%s,%s,%s,%s,%s,%s)
    """

    conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED
    #Usamos este nivel de aislamiento porque no tenemos problemas de lecturas sucias

    try:
        with conn.cursor() as cur:
            cur.execute(sql, (idArtista, titulo, tiempoDuracion, date.today(), genero, categoria))
            conn.commit()
            print(f"Se inserto la cancion {titulo}")
    except psycopg2.Error as e:
        print("No se creo la cancion")
        if e.pgcode == psycopg2.errorcodes.FOREIGN_KEY_VIOLATION:
            print(f"El artista con id {idArtista} no existe")
        elif e.pgcode == psycopg2.errorcodes.NOT_NULL_VIOLATION:
            if e.diag.column_name == "idArtista":
                print("El id del artista no puede ser nulo")
            elif e.diag.column_name == "titulo":
                print("El titulo de una cancion no puede ser nulo")
            elif e.diag.column_name == "tiempoDuracion":
                print("La duracion de la cancion no pude ser nula")
            elif e.diag.column_name == "genero":
                print("El genero no puede ser nulo")
            elif e.diag.column_name == "categoria":
                print("La categoria no puede ser nula")
        elif e.pgcode == psycopg2.errorcodes.CHECK_VIOLATION:
            print("La duracion debe ser mayor que 0")
        else:
            print(f"Erro {e.pgcode}: {e.pgerror}")
        conn.rollback()

def save_cancion(conn):
    print("Guardar cancion")
    sidUsuario = input("Introduce el id de usuario: ")
    sidCancion = input("Introduce el id de cancion a guardar: ")


    if not sidUsuario.isdigit() or int(sidUsuario) <= 0:
        print("El código debe ser un entero > 0")
        return
    idUsuario = int(sidUsuario)

    if not sidCancion.isdigit() or int(sidCancion) <= 0:
        print("El código debe ser un entero > 0")
        return
    idCancion = int(sidCancion)

    sql = """
    INSERT INTO Guarda (idUsuario, idCancion) 
    VALUES (%s, %s)
    """

    conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED
    #Usamos este nivel de aislamiento porque no necesitamos verificar los datos antes de insertar

    try:
        with conn.cursor() as cur:
            cur.execute(sql, (idUsuario, idCancion))
            conn.commit()
            print(f"Se inserto la cancion con id {idCancion} en el usuario {idUsuario}")
    except psycopg2.Error as e:
        print(f"Erro {e.pgcode}: {e.pgerror}")
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
9 - Ver canciones guardadas por un usuario
10 - Crear Cancion              
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
        elif opcion == "10":
            create_cancion(conn)
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