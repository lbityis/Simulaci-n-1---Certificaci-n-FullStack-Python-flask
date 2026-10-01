from datetime import datetime
from flask import flash
from flask_app.config.mysqlconnection import connectToMySQL

class Libro:
    BASE_DATOS = "bd_bookhub"

    def __init__(self, datos):
        self.id = datos['id']
        self.titulo = datos['titulo']
        self.autor = datos['autor']
        self.genero = datos['genero']
        self.fecha_publicacion = datos['fecha_publicacion']
        self.descripcion = datos['descripcion']
        self.usuario_id = datos['usuario_id']
        self.fecha_creacion = datos['fecha_creacion']
        self.fecha_actualizacion = datos['fecha_actualizacion']
        self.creador_nombre = datos.get('nombre', '')
        self.creador_apellido = datos.get('apellido', '')
        self.total_favoritos = datos.get('total_favoritos', 0)

    @classmethod
    def guardar(cls, datos):
        consulta = """
        INSERT INTO libros (titulo, autor, genero, fecha_publicacion, descripcion, usuario_id)
        VALUES (%(titulo)s, %(autor)s, %(genero)s, %(fecha_publicacion)s, %(descripcion)s, %(usuario_id)s);
        """
        return connectToMySQL(cls.BASE_DATOS).query_db(consulta, datos)

    @classmethod
    def obtener_libros_usuario(cls, datos):
        consulta = """
        SELECT l.*, COUNT(f.usuario_id) AS total_favoritos
        FROM libros l
        LEFT JOIN favoritos f ON l.id = f.libro_id
        WHERE l.usuario_id = %(usuario_id)s
        GROUP BY l.id
        ORDER BY l.fecha_creacion DESC;
        """
        resultados = connectToMySQL(cls.BASE_DATOS).query_db(consulta, datos)
        libros = []
        if resultados:
            for fila in resultados:
                libros.append(cls(fila))
        return libros

    @classmethod
    def obtener_libros_comunidad(cls, datos):
        consulta = """
        SELECT l.*, u.nombre, u.apellido, COUNT(f.usuario_id) AS total_favoritos
        FROM libros l
        JOIN usuarios u ON l.usuario_id = u.id
        LEFT JOIN favoritos f ON l.id = f.libro_id
        WHERE l.usuario_id != %(usuario_id)s
        GROUP BY l.id
        ORDER BY l.fecha_creacion DESC;
        """
        resultados = connectToMySQL(cls.BASE_DATOS).query_db(consulta, datos)
        libros = []
        if resultados:
            for fila in resultados:
                libros.append(cls(fila))
        return libros

    @classmethod
    def obtener_por_id(cls, datos):
        consulta = """
        SELECT l.*, u.nombre, u.apellido, COUNT(f.usuario_id) AS total_favoritos
        FROM libros l
        JOIN usuarios u ON l.usuario_id = u.id
        LEFT JOIN favoritos f ON l.id = f.libro_id
        WHERE l.id = %(id)s
        GROUP BY l.id;
        """
        resultados = connectToMySQL(cls.BASE_DATOS).query_db(consulta, datos)
        if not resultados:
            return None
        return cls(resultados[0])

    @classmethod
    def actualizar(cls, datos):
        consulta = """
        UPDATE libros
        SET titulo = %(titulo)s, autor = %(autor)s, genero = %(genero)s,
            fecha_publicacion = %(fecha_publicacion)s, descripcion = %(descripcion)s
        WHERE id = %(id)s AND usuario_id = %(usuario_id)s;
        """
        return connectToMySQL(cls.BASE_DATOS).query_db(consulta, datos)

    @classmethod
    def eliminar(cls, datos):
        consulta = "DELETE FROM libros WHERE id = %(id)s AND usuario_id = %(usuario_id)s;"
        return connectToMySQL(cls.BASE_DATOS).query_db(consulta, datos)

    @classmethod
    def agregar_favorito(cls, datos):
        consulta = "INSERT IGNORE INTO favoritos (usuario_id, libro_id) VALUES (%(usuario_id)s, %(libro_id)s);"
        return connectToMySQL(cls.BASE_DATOS).query_db(consulta, datos)

    @classmethod
    def es_favorito_de_usuario(cls, datos):
        consulta = "SELECT * FROM favoritos WHERE usuario_id = %(usuario_id)s AND libro_id = %(libro_id)s;"
        resultados = connectToMySQL(cls.BASE_DATOS).query_db(consulta, datos)
        return len(resultados) > 0 if resultados else False

    @classmethod
    def obtener_usuarios_que_agregaron_favorito(cls, datos):
        consulta = """
        SELECT u.nombre, u.apellido
        FROM usuarios u
        JOIN favoritos f ON u.id = f.usuario_id
        WHERE f.libro_id = %(libro_id)s;
        """
        return connectToMySQL(cls.BASE_DATOS).query_db(consulta, datos)

    @classmethod
    def obtener_favoritos_de_usuario(cls, datos):
        consulta = """
        SELECT l.*, f.fecha_creacion AS fecha_favorito
        FROM libros l
        JOIN favoritos f ON l.id = f.libro_id
        WHERE f.usuario_id = %(usuario_id)s
        ORDER BY f.fecha_creacion DESC;
        """
        resultados = connectToMySQL(cls.BASE_DATOS).query_db(consulta, datos)
        libros = []
        if resultados:
            for fila in resultados:
                libros.append(cls(fila))
        return libros

    @staticmethod
    def validar_libro(formulario):
        es_valido = True

        # Comprobacion general de campos obligatorios
        if not formulario.get('titulo') or not formulario.get('autor') or not formulario.get('genero') or not formulario.get('fecha_publicacion') or not formulario.get('descripcion'):
            flash("Todos los campos son obligatorios.", "libro")
            return False

        # Titulo minimo 2 caracteres
        if len(formulario['titulo'].strip()) < 2:
            flash("El titulo debe tener como minimo 2 caracteres.", "libro")
            es_valido = False

        # Autor obligatorio
        if len(formulario['autor'].strip()) == 0:
            flash("El autor es obligatorio.", "libro")
            es_valido = False

        # Genero obligatorio
        if not formulario['genero'].strip():
            flash("El genero es obligatorio.", "libro")
            es_valido = False

        # Fecha no puede ser futura
        try:
            fecha_ingresada = datetime.strptime(formulario['fecha_publicacion'], '%Y-%m-%d').date()
            if fecha_ingresada > datetime.now().date():
                flash("La fecha de publicacion no puede ser una fecha futura.", "libro")
                es_valido = False
        except ValueError:
            flash("Formato de fecha de publicacion no valido.", "libro")
            es_valido = False

        # Descripcion minimo 10 caracteres
        if len(formulario['descripcion'].strip()) < 10:
            flash("La descripcion debe tener como minimo 10 caracteres.", "libro")
            es_valido = False

        return es_valido