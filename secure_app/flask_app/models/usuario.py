import re
from flask import flash
from flask_app.config.mysqlconnection import connectToMySQL

# Expresion regular para validar formato de correo
EXPRESION_CORREO = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class Usuario:
    BASE_DATOS = "bd_bookhub"

    def __init__(self, datos):
        self.id = datos['id']
        self.nombre = datos['nombre']
        self.apellido = datos['apellido']
        self.correo = datos['correo']
        self.contrasena = datos['contrasena']
        self.fecha_creacion = datos['fecha_creacion']
        self.fecha_actualizacion = datos['fecha_actualizacion']

    @classmethod
    def guardar(cls, datos):
        consulta = """
        INSERT INTO usuarios (nombre, apellido, correo, contrasena)
        VALUES (%(nombre)s, %(apellido)s, %(correo)s, %(contrasena)s);
        """
        return connectToMySQL(cls.BASE_DATOS).query_db(consulta, datos)

    @classmethod
    def obtener_por_correo(cls, datos):
        consulta = "SELECT * FROM usuarios WHERE correo = %(correo)s;"
        resultados = connectToMySQL(cls.BASE_DATOS).query_db(consulta, datos)
        if not resultados or len(resultados) < 1:
            return False
        return cls(resultados[0])

    @classmethod
    def obtener_por_id(cls, datos):
        consulta = "SELECT * FROM usuarios WHERE id = %(id)s;"
        resultados = connectToMySQL(cls.BASE_DATOS).query_db(consulta, datos)
        if not resultados or len(resultados) < 1:
            return False
        return cls(resultados[0])

    @staticmethod
    def validar_registro(formulario):
        es_valido = True

        # Validacion de Nombre
        if not formulario['nombre'] or len(formulario['nombre'].strip()) < 2:
            flash("El nombre es obligatorio y debe tener al menos 2 caracteres.", "registro")
            es_valido = False

        # Validacion de Apellido
        if not formulario['apellido'] or len(formulario['apellido'].strip()) < 2:
            flash("El apellido es obligatorio y debe tener al menos 2 caracteres.", "registro")
            es_valido = False

        # Validacion de E-mail
        if not formulario['correo']:
            flash("El e-mail es obligatorio.", "registro")
            es_valido = False
        elif not EXPRESION_CORREO.match(formulario['correo']):
            flash("El e-mail debe tener un formato valido.", "registro")
            es_valido = False
        else:
            usuario_existente = Usuario.obtener_por_correo({'correo': formulario['correo']})
            if usuario_existente:
                flash("El e-mail ya esta registrado.", "registro")
                es_valido = False

        # Validacion de Contrasenas
        if not formulario['contrasena']:
            flash("La contrasena es obligatoria.", "registro")
            es_valido = False

        if not formulario['confirmar_contrasena']:
            flash("La confirmacion de contrasena es obligatoria.", "registro")
            es_valido = False

        if formulario['contrasena'] and formulario['confirmar_contrasena']:
            if formulario['contrasena'] != formulario['confirmar_contrasena']:
                flash("La contrasena y su confirmacion deben coincidir.", "registro")
                es_valido = False

        return es_valido