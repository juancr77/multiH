from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models.Data import (
    DatabaseSingleton,
    Administrador,
    Propietario,
    Seguro,
    Propiedad,
    Venta,
    Estatus,
    Construccion,
    Mudanza
)
from sqlalchemy.exc import IntegrityError
from fpdf import FPDF
import os

# Configuración de la aplicación Flask
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Cambia esto por una clave secreta segura
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuración del servidor de correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'reissjony411@gmail.com'  # Reemplaza con tu correo
app.config['MAIL_PASSWORD'] = 'keau iufr bgha bxnc'        # Reemplaza con tu contraseña o usa variables de entorno

mail = Mail(app)

# Obtener sesión de la base de datos
db_singleton = DatabaseSingleton()
db_session = db_singleton.get_session()

# Session management
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# Helper para verificar archivos permitidos
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Middleware para verificar si el usuario es administrador
def is_admin():
    return 'user_id' in session

# ------------------------------- Rutas Principales -------------------------------- #
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/compra")
def compra():
    return render_template("compra.html")

@app.route("/construir")
def construir():
    return render_template("construir.html")

@app.route("/venta")
def venta():
    return render_template("venta.html")

@app.route("/mudanzas_2")
def mudanzas_publico():
    return render_template("mudanzas.html")

@app.route("/seguros_publico")
def seguros_publico():
    return render_template("seguros.html")

@app.route("/contactos", methods=["GET", "POST"])
def contactos():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        mensaje = request.form.get("mensaje")

        try:
            msg = Message(
                subject="Nuevo mensaje de contacto",
                sender=app.config['MAIL_USERNAME'],
                recipients=['reissjony411@gmail.com'],  # Reemplaza con el correo destinatario
                body=f"Nombre: {nombre}\nCorreo: {email}\nMensaje: {mensaje}"
            )
            mail.send(msg)
            flash("Tu mensaje ha sido enviado correctamente. ¡Gracias por contactarnos!")
        except Exception as e:
            flash(f"Error al enviar el mensaje: {str(e)}")
        return redirect(url_for("contactos"))

    return render_template("contactos.html")

# ----------------------------- Rutas de Autenticación ----------------------------- #
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            admin = db_session.query(Administrador).filter_by(username=username).first()
            if admin and check_password_hash(admin.password_hash, password):
                session['user_id'] = admin.idAdmin
                session['username'] = admin.username
                flash('Inicio de sesión exitoso.', 'success')
                return redirect(url_for('menu'))
            else:
                flash('Usuario o contraseña incorrectos.', 'error')
        except Exception as e:
            db_session.rollback()
            flash(f"Error: {str(e)}", 'error')

    return render_template('admin.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente.', 'success')
    return redirect(url_for('admin'))

@app.route('/menu')
def menu():
    if not is_admin():
        flash('Debes iniciar sesión primero.', 'error')
        return redirect(url_for('admin'))
    return render_template('menu_admin.html')

# ----------------------------- Registro de Administradores ----------------------------- #
@app.route('/admin/registrar', methods=['GET', 'POST'])
def registrar_admin():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        telefono = request.form['telefono']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # Hash the password
        password_hash = generate_password_hash(password)

        nuevo_admin = Administrador(
            nombre=nombre,
            apellido=apellido,
            telefono=telefono,
            email=email,
            username=username,
            password_hash=password_hash
        )
        try:
            db_session.add(nuevo_admin)
            db_session.commit()
            flash('Administrador registrado exitosamente.', 'success')
            return redirect(url_for('admin'))
        except IntegrityError:
            db_session.rollback()
            flash('Error al registrar el administrador. El usuario o email ya existe.', 'error')
    return render_template('registrar_admin.html')

# ----------------------------- Gestión de Ventas ----------------------------- #
@app.route('/ventas')
def listar_ventas():
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))
    ventas = db_session.query(Venta).all()
    return render_template('ventas_admin.html', ventas=ventas)

@app.route('/ventas/agregar', methods=['GET', 'POST'])
def agregar_venta():
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        idProfk = request.form['idProfk']
        idEstatusfk = request.form['idEstatusfk']
        idPropietario = request.form['idPropietario']
        fecha_venta = request.form['fecha_venta']

        nueva_venta = Venta(
            idProfk=idProfk,
            idEstatusfk=idEstatusfk,
            idPropietario=idPropietario,
            fecha_venta=fecha_venta
        )
        try:
            db_session.add(nueva_venta)
            db_session.commit()
            flash('Venta agregada exitosamente.', 'success')
            return redirect(url_for('listar_ventas'))
        except IntegrityError:
            db_session.rollback()
            flash('Error al agregar la venta. Revisa los datos.', 'error')

    propiedades = db_session.query(Propiedad).all()
    estatuses = db_session.query(Estatus).all()
    propietarios = db_session.query(Propietario).all()
    return render_template('agregar_venta_admin.html', propiedades=propiedades, estatuses=estatuses, propietarios=propietarios)

@app.route('/ventas/eliminar/<int:id>', methods=['POST'])
def eliminar_venta(id):
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))

    venta = db_session.query(Venta).get(id)
    if not venta:
        flash('Venta no encontrada.', 'error')
        return redirect(url_for('listar_ventas'))

    try:
        db_session.delete(venta)
        db_session.commit()
        flash('Venta eliminada exitosamente.', 'success')
    except IntegrityError:
        db_session.rollback()
        flash('Error al eliminar la venta.', 'error')

    return redirect(url_for('listar_ventas'))

@app.route('/ventas/editar/<int:id>', methods=['GET', 'POST'])
def editar_venta(id):
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))

    venta = db_session.query(Venta).get(id)
    if not venta:
        flash('Venta no encontrada.', 'error')
        return redirect(url_for('listar_ventas'))

    if request.method == 'POST':
        venta.idProfk = request.form['idProfk']
        venta.idEstatusfk = request.form['idEstatusfk']
        venta.idPropietario = request.form['idPropietario']
        venta.fecha_venta = request.form['fecha_venta']
        try:
            db_session.commit()
            flash('Venta actualizada exitosamente.', 'success')
            return redirect(url_for('listar_ventas'))
        except IntegrityError:
            db_session.rollback()
            flash('Error al actualizar la venta. Revisa los datos.', 'error')

    propiedades = db_session.query(Propiedad).all()
    estatuses = db_session.query(Estatus).all()
    propietarios = db_session.query(Propietario).all()
    return render_template('editar_venta_admin.html', venta=venta, propiedades=propiedades, estatuses=estatuses, propietarios=propietarios)

# ----------------------------- Gestión de Propiedades ----------------------------- #
@app.route('/propiedades')
def listar_propiedades():
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))
    propiedades = db_session.query(Propiedad).all()
    return render_template('propiedades_admin.html', propiedades=propiedades)

@app.route('/propiedades/agregar', methods=['GET', 'POST'])
def agregar_propiedad():
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        ciudad = request.form['ciudad']
        estado = request.form['estado']
        codigo_postal = request.form['codigo_postal']
        precio = request.form['precio']
        num_recamaras = request.form['num_recamaras']
        num_banos = request.form['num_banos']
        idSeguro = request.form['idSeguro']
        file = request.files['imagen']

        filepath = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            filepath = filepath.replace("static/", "")

        nueva_propiedad = Propiedad(
            ciudad=ciudad,
            estado=estado,
            codigo_postal=codigo_postal,
            precio=precio,
            num_recamaras=num_recamaras,
            num_banos=num_banos,
            idSeguro=idSeguro,
            imagen=filepath
        )
        try:
            db_session.add(nueva_propiedad)
            db_session.commit()
            flash('Propiedad agregada exitosamente.', 'success')
            return redirect(url_for('listar_propiedades'))
        except IntegrityError:
            db_session.rollback()
            flash('Error al agregar la propiedad. Revisa los datos.', 'error')

    seguros = db_session.query(Seguro).all()
    return render_template('agregar_propiedad_admin.html', seguros=seguros)

@app.route('/propiedades/editar/<int:id>', methods=['GET', 'POST'])
def editar_propiedad(id):
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))
    
    propiedad = db_session.query(Propiedad).get(id)
    if not propiedad:
        flash('Propiedad no encontrada.', 'error')
        return redirect(url_for('listar_propiedades'))
    
    if request.method == 'POST':
        propiedad.ciudad = request.form['ciudad']
        propiedad.estado = request.form['estado']
        propiedad.codigo_postal = request.form['codigo_postal']
        propiedad.precio = request.form['precio']
        propiedad.num_recamaras = request.form['num_recamaras']
        propiedad.num_banos = request.form['num_banos']
        propiedad.idSeguro = request.form['idSeguro']
        
        file = request.files.get('imagen')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            filepath = filepath.replace("static/", "")
            propiedad.imagen = filepath  # Actualizar la imagen
        
        try:
            db_session.commit()
            flash('Propiedad actualizada exitosamente.', 'success')
            return redirect(url_for('listar_propiedades'))
        except IntegrityError:
            db_session.rollback()
            flash('Error al actualizar la propiedad. Revisa los datos.', 'error')
    
    seguros = db_session.query(Seguro).all()
    return render_template('editar_propiedad_admin.html', propiedad=propiedad, seguros=seguros)

@app.route('/propiedades/eliminar/<int:id>', methods=['POST'])
def eliminar_propiedad(id):
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))
    
    propiedad = db_session.query(Propiedad).get(id)
    if not propiedad:
        flash('Propiedad no encontrada.', 'error')
        return redirect(url_for('listar_propiedades'))
    
    try:
        db_session.delete(propiedad)
        db_session.commit()
        flash('Propiedad eliminada exitosamente.', 'success')
    except IntegrityError:
        db_session.rollback()
        flash('Error al eliminar la propiedad.', 'error')
    
    return redirect(url_for('listar_propiedades'))

# ----------------------------- Gestión de Propietarios ----------------------------- #
@app.route('/propietarios')
def listar_propietarios():
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))
    propietarios = db_session.query(Propietario).all()
    return render_template('propietarios_admin.html', propietarios=propietarios)

@app.route('/propietarios/agregar', methods=['GET', 'POST'])
def agregar_propietario():
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        telefono = request.form['telefono']
        email = request.form['email']
        direccion = request.form['direccion']
        fecha_registro = request.form['fecha_registro']

        nuevo_propietario = Propietario(
            nombre=nombre,
            apellido=apellido,
            telefono=telefono,
            email=email,
            direccion=direccion,
            fecha_registro=fecha_registro
        )
        try:
            db_session.add(nuevo_propietario)
            db_session.commit()
            flash('Propietario agregado exitosamente.', 'success')
            return redirect(url_for('listar_propietarios'))
        except IntegrityError:
            db_session.rollback()
            flash('Error al agregar el propietario. Revisa los datos.', 'error')

    return render_template('agregar_propietario_admin.html')

@app.route('/propietarios/editar/<int:id>', methods=['GET', 'POST'])
def editar_propietario(id):
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))

    propietario = db_session.query(Propietario).get(id)
    if not propietario:
        flash('Propietario no encontrado.', 'error')
        return redirect(url_for('listar_propietarios'))

    if request.method == 'POST':
        propietario.nombre = request.form['nombre']
        propietario.apellido = request.form['apellido']
        propietario.telefono = request.form['telefono']
        propietario.email = request.form['email']
        propietario.direccion = request.form['direccion']
        propietario.fecha_registro = request.form['fecha_registro']
        try:
            db_session.commit()
            flash('Propietario actualizado exitosamente.', 'success')
            return redirect(url_for('listar_propietarios'))
        except IntegrityError:
            db_session.rollback()
            flash('Error al actualizar el propietario. Revisa los datos.', 'error')

    return render_template('editar_propietario_admin.html', propietario=propietario)

@app.route('/propietarios/eliminar/<int:id>', methods=['POST'])
def eliminar_propietario(id):
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))

    propietario = db_session.query(Propietario).get(id)
    if not propietario:
        flash('Propietario no encontrado.', 'error')
        return redirect(url_for('listar_propietarios'))

    try:
        db_session.delete(propietario)
        db_session.commit()
        flash('Propietario eliminado exitosamente.', 'success')
    except IntegrityError:
        db_session.rollback()
        flash('Error al eliminar el propietario.', 'error')

    return redirect(url_for('listar_propietarios'))

# ----------------------------- Gestión de Seguros ----------------------------- #
@app.route('/seguros')
def listar_seguros():
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))
    seguros = db_session.query(Seguro).all()
    return render_template('seguros_admin.html', seguros=seguros)

@app.route('/seguros/agregar', methods=['GET', 'POST'])
def agregar_seguro():
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        detalle = request.form['detalle']

        nuevo_seguro = Seguro(detalle=detalle)
        try:
            db_session.add(nuevo_seguro)
            db_session.commit()
            flash('Seguro agregado exitosamente.', 'success')
            return redirect(url_for('listar_seguros'))
        except IntegrityError:
            db_session.rollback()
            flash('Error al agregar el seguro. Revisa los datos.', 'error')

    return render_template('agregar_seguro_admin.html')

@app.route('/seguros/editar/<int:id>', methods=['GET', 'POST'])
def editar_seguro(id):
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))

    seguro = db_session.query(Seguro).get(id)
    if not seguro:
        flash('Seguro no encontrado.', 'error')
        return redirect(url_for('listar_seguros'))

    if request.method == 'POST':
        seguro.detalle = request.form['detalle']
        try:
            db_session.commit()
            flash('Seguro actualizado exitosamente.', 'success')
            return redirect(url_for('listar_seguros'))
        except IntegrityError:
            db_session.rollback()
            flash('Error al actualizar el seguro. Revisa los datos.', 'error')

    return render_template('editar_seguro_admin.html', seguro=seguro)

@app.route('/seguros/eliminar/<int:id>', methods=['POST'])
def eliminar_seguro(id):
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))

    seguro = db_session.query(Seguro).get(id)
    if not seguro:
        flash('Seguro no encontrado.', 'error')
        return redirect(url_for('listar_seguros'))

    try:
        db_session.delete(seguro)
        db_session.commit()
        flash('Seguro eliminado exitosamente.', 'success')
    except IntegrityError:
        db_session.rollback()
        flash('Error al eliminar el seguro.', 'error')

    return redirect(url_for('listar_seguros'))

# ----------------------------- Gestión de Mudanzas ----------------------------- #
@app.route('/mudanzas')
def listar_mudanzas():
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))
    mudanzas = db_session.query(Mudanza).all()
    return render_template('mudanzas_admin.html', mudanzas=mudanzas)

@app.route('/mudanzas/agregar', methods=['GET', 'POST'])
def agregar_mudanza():
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        idSfK2 = request.form['idSfK2']
        idPropietario = request.form['idPropietario']
        empresa_mudanza = request.form['empresa_mudanza']
        fecha_mudanza = request.form['fecha_mudanza']
        costo = request.form['costo']
        comentarios = request.form['comentarios']

        nueva_mudanza = Mudanza(
            idSfK2=idSfK2,
            idPropietario=idPropietario,
            empresa_mudanza=empresa_mudanza,
            fecha_mudanza=fecha_mudanza,
            costo=costo,
            comentarios=comentarios
        )
        try:
            db_session.add(nueva_mudanza)
            db_session.commit()
            flash('Mudanza agregada exitosamente.', 'success')
            return redirect(url_for('listar_mudanzas'))
        except IntegrityError:
            db_session.rollback()
            flash('Error al agregar la mudanza. Revisa los datos.', 'error')

    seguros = db_session.query(Seguro).all()
    propietarios = db_session.query(Propietario).all()
    return render_template('agregar_mudanza_admin.html', seguros=seguros, propietarios=propietarios)

# ----------------------------- Gestión de Construcciones ----------------------------- #
@app.route('/construcciones')
def listar_construcciones():
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))
    construcciones = db_session.query(Construccion).all()
    return render_template('construcciones_admin.html', construcciones=construcciones)

@app.route('/construcciones/agregar', methods=['GET', 'POST'])
def agregar_construccion():
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))

    if request.method == 'POST':
        idSfK1 = request.form['idSfK1']
        idPropietario = request.form['idPropietario']
        materiales_usados = request.form['materiales_usados']
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']
        estado_construccion = request.form['estado_construccion']

        nueva_construccion = Construccion(
            idSfK1=idSfK1,
            idPropietario=idPropietario,
            materiales_usados=materiales_usados,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado_construccion=estado_construccion
        )
        try:
            db_session.add(nueva_construccion)
            db_session.commit()
            flash('Construcción agregada exitosamente.', 'success')
            return redirect(url_for('listar_construcciones'))
        except IntegrityError:
            db_session.rollback()
            flash('Error al agregar la construcción. Revisa los datos.', 'error')

    seguros = db_session.query(Seguro).all()
    propietarios = db_session.query(Propietario).all()
    return render_template('agregar_construccion_admin.html', seguros=seguros, propietarios=propietarios)

@app.route('/construcciones/editar/<int:id>', methods=['GET', 'POST'])
def editar_construccion(id):
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))

    construccion = db_session.query(Construccion).get(id)
    if not construccion:
        flash('Construcción no encontrada.', 'error')
        return redirect(url_for('listar_construcciones'))

    if request.method == 'POST':
        construccion.idSfK1 = request.form['idSfK1']
        construccion.idPropietario = request.form['idPropietario']
        construccion.materiales_usados = request.form['materiales_usados']
        construccion.fecha_inicio = request.form['fecha_inicio']
        construccion.fecha_fin = request.form['fecha_fin']
        construccion.estado_construccion = request.form['estado_construccion']
        try:
            db_session.commit()
            flash('Construcción actualizada exitosamente.', 'success')
            return redirect(url_for('listar_construcciones'))
        except IntegrityError:
            db_session.rollback()
            flash('Error al actualizar la construcción. Revisa los datos.', 'error')

    seguros = db_session.query(Seguro).all()
    propietarios = db_session.query(Propietario).all()
    return render_template('editar_construccion_admin.html', construccion=construccion, seguros=seguros, propietarios=propietarios)

@app.route('/construcciones/eliminar/<int:id>', methods=['POST'])
def eliminar_construccion(id):
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))

    construccion = db_session.query(Construccion).get(id)
    if not construccion:
        flash('Construcción no encontrada.', 'error')
        return redirect(url_for('listar_construcciones'))

    try:
        db_session.delete(construccion)
        db_session.commit()
        flash('Construcción eliminada exitosamente.', 'success')
    except IntegrityError:
        db_session.rollback()
        flash('Error al eliminar la construcción.', 'error')

    return redirect(url_for('listar_construcciones'))

# ----------------------------- Búsqueda de Casas ----------------------------- #
@app.route('/busqueda_casas', methods=['GET', 'POST'])
def busqueda_casas():
    if request.method == 'POST':
        ciudad = request.form.get('ciudad')
        precio_min = request.form.get('precio_min', type=float)
        precio_max = request.form.get('precio_max', type=float)
        num_recamaras = request.form.get('num_recamaras', type=int)

        query = db_session.query(Propiedad).join(Venta, Propiedad.idPro == Venta.idProfk, isouter=True)
        query = query.filter(Venta.idProfk == None)  # Buscar solo propiedades no vendidas

        if ciudad:
            query = query.filter(Propiedad.ciudad.ilike(f"%{ciudad}%"))
        if precio_min is not None:
            query = query.filter(Propiedad.precio >= precio_min)
        if precio_max is not None:
            query = query.filter(Propiedad.precio <= precio_max)
        if num_recamaras is not None:
            query = query.filter(Propiedad.num_recamaras == num_recamaras)

        propiedades = query.all()
        return render_template('resultado_busqueda.html', propiedades=propiedades)

    return render_template('busqueda_casas.html')

# ----------------------------- Reporte de Casas ----------------------------- #
@app.route('/reporte_casas', methods=['GET'])
def reporte_casas():
    propiedades = (
        db_session.query(Propiedad, Venta)
        .outerjoin(Venta, Propiedad.idPro == Venta.idProfk)
        .all()
    )
    reporte = [
        {
            'ciudad': propiedad.ciudad,
            'estado': propiedad.estado,
            'precio': propiedad.precio,
            'recamaras': propiedad.num_recamaras,
            'banos': propiedad.num_banos,
            'estatus': 'Vendida' if venta else 'En Venta',
            'imagen': propiedad.imagen,
        }
        for propiedad, venta in propiedades
    ]
    return render_template('reporte_casas.html', reporte=reporte)

@app.route('/ficha_tecnica/<int:id>', methods=['GET'])
def ficha_tecnica(id):
    propiedad = db_session.query(Propiedad).filter_by(idPro=id).first()

    if not propiedad:
        flash('La propiedad no existe.', 'error')
        return redirect(url_for('reporte_casas'))

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt="Ficha Técnica de la Propiedad", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Ciudad: {propiedad.ciudad}", ln=True)
    pdf.cell(200, 10, txt=f"Estado: {propiedad.estado}", ln=True)
    pdf.cell(200, 10, txt=f"Precio: ${propiedad.precio}", ln=True)
    pdf.cell(200, 10, txt=f"Número de Recámaras: {propiedad.num_recamaras}", ln=True)
    pdf.cell(200, 10, txt=f"Número de Baños: {propiedad.num_banos}", ln=True)
    pdf.ln(10)

    if propiedad.imagen:
        image_path = f"static/{propiedad.imagen}"
        try:
            pdf.image(image_path, x=10, y=pdf.get_y(), w=100)
        except:
            pdf.cell(200, 10, txt="Error al cargar la imagen.", ln=True)

    file_path = f"static/ficha_tecnica_{id}.pdf"
    pdf.output(file_path)

    return send_file(file_path, as_attachment=True)

@app.route('/seleccionar_casa', methods=['GET'])
def seleccionar_casa():
    propiedades = db_session.query(Propiedad).all()
    return render_template('seleccionar_casa.html', propiedades=propiedades)

# ----------------------------- APIs ----------------------------- #
@app.route('/api/estado_casas', methods=['GET'])
def estado_casas():
    casas_vendidas = db_session.query(Venta).count()
    total_casas = db_session.query(Propiedad).count()
    casas_en_venta = total_casas - casas_vendidas
    data = {
        'Vendidas': casas_vendidas,
        'En Venta': casas_en_venta
    }
    return jsonify(data)

@app.route('/api/casas_por_costo', methods=['GET'])
def casas_por_costo():
    rangos = {
        '0-100k': (0, 100000),
        '100k-200k': (100000, 200000),
        '200k-300k': (200000, 300000),
        '300k+': (300000, None)
    }
    casas_rango = {}
    for rango, (minimo, maximo) in rangos.items():
        query = db_session.query(Propiedad)
        if maximo is None:
            count = query.filter(Propiedad.precio > minimo).count()
        else:
            count = query.filter(Propiedad.precio >= minimo, Propiedad.precio <= maximo).count()
        casas_rango[rango] = count
    return jsonify(casas_rango)

# ----------------------------- Dashboard ----------------------------- #
@app.route('/dashboard', methods=['GET'])
def dashboard():
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))

    total_propiedades = db_session.query(Propiedad).count()
    total_ventas = db_session.query(Venta).count()

    return render_template('dashboard.html', total_propiedades=total_propiedades, total_ventas=total_ventas)

@app.route('/reporte_completo', methods=['GET'])
def reporte_completo():
    propiedades = (
        db_session.query(Propiedad, Venta)
        .outerjoin(Venta, Propiedad.idPro == Venta.idProfk)
        .all()
    )

    reporte = []
    for propiedad, venta in propiedades:
        reporte.append({
            'ciudad': propiedad.ciudad,
            'estado': propiedad.estado,
            'precio': propiedad.precio,
            'recamaras': propiedad.num_recamaras,
            'banos': propiedad.num_banos,
            'estatus': 'Vendida' if venta else 'En Venta',
            'imagen': propiedad.imagen,
        })

    return render_template('reporte_completo.html', propiedades=reporte)

@app.route('/generar_reporte_pdf', methods=['GET'])
def generar_reporte_pdf():
    propiedades = (
        db_session.query(Propiedad, Venta)
        .outerjoin(Venta, Propiedad.idPro == Venta.idProfk)
        .all()
    )

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt="Reporte Completo de Propiedades", ln=True, align='C')
    pdf.ln(10)

    for propiedad, venta in propiedades:
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Ciudad: {propiedad.ciudad}", ln=True)
        pdf.cell(200, 10, txt=f"Estado: {propiedad.estado}", ln=True)
        pdf.cell(200, 10, txt=f"Precio: ${propiedad.precio}", ln=True)
        pdf.cell(200, 10, txt=f"Recámaras: {propiedad.num_recamaras}", ln=True)
        pdf.cell(200, 10, txt=f"Baños: {propiedad.num_banos}", ln=True)
        pdf.cell(200, 10, txt=f"Estatus: {'Vendida' if venta else 'En Venta'}", ln=True)
        pdf.ln(10)

    file_path = "static/reporte_completo.pdf"
    pdf.output(file_path)

    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    # Crear carpetas necesarias si no existen
    if not os.path.exists('static/uploads'):
        os.makedirs('static/uploads')

    # Ejecutar la aplicación
    app.run(debug=True, host='0.0.0.0', port=5000)
