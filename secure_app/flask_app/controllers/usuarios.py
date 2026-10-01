from flask import render_template, redirect, request, session, flash
from flask_app import app, bcrypt
from flask_app.models.usuario import Usuario

@app.route("/")
def ruta_raiz():
    return redirect("/login")

@app.route("/login")
def vista_login():
    if 'usuario_id' in session:
        return redirect("/libros")
    return render_template("index.html")

@app.route("/registro", methods=["POST"])
def registrar_usuario():
    if not Usuario.validar_registro(request.form):
        return redirect("/login")

    contrasena_encriptada = bcrypt.generate_password_hash(request.form['contrasena']).decode('utf-8')

    datos = {
        "nombre": request.form['nombre'],
        "apellido": request.form['apellido'],
        "correo": request.form['correo'],
        "contrasena": contrasena_encriptada
    }

    usuario_id = Usuario.guardar(datos)

    session['usuario_id'] = usuario_id
    session['usuario_nombre'] = request.form['nombre']
    flash("Registro exitoso.", "exito")
    return redirect("/libros")

@app.route("/procesar_login", methods=["POST"])
def iniciar_sesion():
    if not request.form.get('correo'):
        flash("El e-mail es obligatorio.", "login")
        return redirect("/login")

    if not request.form.get('contrasena'):
        flash("La contrasena es obligatoria.", "login")
        return redirect("/login")

    usuario = Usuario.obtener_por_correo({'correo': request.form['correo']})

    if not usuario or not bcrypt.check_password_hash(usuario.contrasena, request.form['contrasena']):
        flash("Credenciales incorrectas.", "login")
        return redirect("/login")

    session['usuario_id'] = usuario.id
    session['usuario_nombre'] = usuario.nombre
    flash("Inicio de sesion exitoso.", "exito")
    return redirect("/libros")

@app.route("/logout")
def cerrar_sesion():
    session.clear()
    return redirect("/login")