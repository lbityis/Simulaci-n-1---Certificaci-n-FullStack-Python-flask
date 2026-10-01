from flask import render_template, redirect, request, session, flash
from flask_app import app
from flask_app.models.libro import Libro

@app.route("/libros")
def pagina_principal_libros():
    if 'usuario_id' not in session:
        flash("Operacion no permitida. Debe iniciar sesion.", "login")
        return redirect("/login")

    datos_usuario = {'usuario_id': session['usuario_id']}
    mis_libros = Libro.obtener_libros_usuario(datos_usuario)
    libros_comunidad = Libro.obtener_libros_comunidad(datos_usuario)

    return render_template("libros.html", mis_libros=mis_libros, libros_comunidad=libros_comunidad)

@app.route("/libros/nuevo")
def formulario_nuevo_libro():
    if 'usuario_id' not in session:
        flash("Operacion no permitida.", "login")
        return redirect("/login")

    return render_template("nuevo_libro.html")

@app.route("/libros/crear", methods=["POST"])
def crear_libro():
    if 'usuario_id' not in session:
        return redirect("/login")

    if not Libro.validar_libro(request.form):
        return redirect("/libros/nuevo")

    datos = {
        "titulo": request.form['titulo'],
        "autor": request.form['autor'],
        "genero": request.form['genero'],
        "fecha_publicacion": request.form['fecha_publicacion'],
        "descripcion": request.form['descripcion'],
        "usuario_id": session['usuario_id']
    }

    Libro.guardar(datos)
    flash("Libro creado correctamente.", "exito")
    return redirect("/libros")

@app.route("/libros/<int:id>")
def ver_detalle_libro(id):
    if 'usuario_id' not in session:
        return redirect("/login")

    libro = Libro.obtener_por_id({'id': id})
    if not libro:
        return redirect("/libros")

    es_favorito = Libro.es_favorito_de_usuario({'usuario_id': session['usuario_id'], 'libro_id': id})
    usuarios_favoritos = Libro.obtener_usuarios_que_agregaron_favorito({'libro_id': id})

    return render_template("detalle_libro.html", libro=libro, es_favorito=es_favorito, usuarios_favoritos=usuarios_favoritos)

@app.route("/libros/editar/<int:id>")
def formulario_editar_libro(id):
    if 'usuario_id' not in session:
        return redirect("/login")

    libro = Libro.obtener_por_id({'id': id})

    # Verificacion de propietario
    if not libro or libro.usuario_id != session['usuario_id']:
        flash("Operacion no permitida. Solo el propietario puede editar este libro.", "error")
        return redirect("/libros")

    return render_template("editar_libro.html", libro=libro)

@app.route("/libros/actualizar/<int:id>", methods=["POST"])
def actualizar_libro(id):
    if 'usuario_id' not in session:
        return redirect("/login")

    libro = Libro.obtener_por_id({'id': id})

    if not libro or libro.usuario_id != session['usuario_id']:
        flash("Operacion no permitida. Acceso denegado.", "error")
        return redirect("/libros")

    if not Libro.validar_libro(request.form):
        return redirect(f"/libros/editar/{id}")

    datos = {
        "id": id,
        "titulo": request.form['titulo'],
        "autor": request.form['autor'],
        "genero": request.form['genero'],
        "fecha_publicacion": request.form['fecha_publicacion'],
        "descripcion": request.form['descripcion'],
        "usuario_id": session['usuario_id']
    }

    Libro.actualizar(datos)
    flash("Libro actualizado correctamente.", "exito")
    return redirect("/libros")

@app.route("/libros/borrar/<int:id>")
def eliminar_libro(id):
    if 'usuario_id' not in session:
        return redirect("/login")

    libro = Libro.obtener_por_id({'id': id})

    if not libro or libro.usuario_id != session['usuario_id']:
        flash("Operacion no permitida. No puedes borrar un libro de otro usuario.", "error")
        return redirect("/libros")

    Libro.eliminar({'id': id, 'usuario_id': session['usuario_id']})
    flash("Libro eliminado correctamente.", "exito")
    return redirect("/libros")

@app.route("/favoritos/agregar/<int:libro_id>", methods=["POST"])
def agregar_a_favoritos(libro_id):
    if 'usuario_id' not in session:
        return redirect("/login")

    ya_es_favorito = Libro.es_favorito_de_usuario({'usuario_id': session['usuario_id'], 'libro_id': libro_id})

    if ya_es_favorito:
        flash("Libro ya agregado a favoritos.", "info")
    else:
        Libro.agregar_favorito({'usuario_id': session['usuario_id'], 'libro_id': libro_id})
        flash("Libro agregado a favoritos.", "exito")

    return redirect(f"/libros/{libro_id}")

@app.route("/favoritos")
def ver_mis_favoritos():
    if 'usuario_id' not in session:
        return redirect("/login")

    libros_favoritos = Libro.obtener_favoritos_de_usuario({'usuario_id': session['usuario_id']})
    return render_template("favoritos.html", libros_favoritos=libros_favoritos)