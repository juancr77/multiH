from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
from flask_mail import Mail, Message
from flask import Flask, render_template, request, redirect, url_for, flash, session
from models.Data import DatabaseSingleton, Administrador  # Importar desde tu archivo
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash, session
from models.Data import DatabaseSingleton, Administrador, Venta, Propiedad, Estatus, Propietario,Seguro,Construccion,Mudanza
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash, session
from models.Data import DatabaseSingleton, Administrador, Venta, Propiedad, Estatus, Propietario,Seguro
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from flask import send_file
from fpdf import FPDF
from werkzeug.security import generate_password_hash
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Configuración de Flask
app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Obtener sesión de la base de datos
db_singleton = DatabaseSingleton()
db_session = db_singleton.get_session()

# Configuración del servidor de correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Servidor SMTP
app.config['MAIL_PORT'] = 587  # Puerto SMTP
app.config['MAIL_USE_TLS'] = True  # Activar encriptación TLS
app.config['MAIL_USE_SSL'] = False  # No usar SSL
app.config['MAIL_USERNAME'] = 'reissjony411@gmail.com'  # Cambia por tu correo
app.config['MAIL_PASSWORD'] = 'thae labz ojig nest'  # Cambia por tu contraseña
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

mail = Mail(app)

# Ruta para la página principal
@app.route("/")
def index():
    return render_template("index.html")

# Rutas para las páginas específicas
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
def mudanzas():
    return render_template("mudanzas.html")

@app.route("/seguros_publico")
def seguros_publico():
    return render_template("seguros.html")

# Ruta para la página de contacto (con formulario)
@app.route("/contactos", methods=["GET", "POST"])
def contactos():
    if request.method == "POST":
        # Recoger datos del formulario
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        mensaje = request.form.get("mensaje")

        # Crear y enviar el correo
        try:
            msg = Message(
                subject="Nuevo mensaje de contacto",
                sender=app.config['MAIL_USERNAME'],
                recipients=['reissjony411@gmail.com'],  # Cambia por el correo de destino
                body=f"Nombre: {nombre}\nCorreo: {email}\nMensaje: {mensaje}"
            )
            mail.send(msg)
            flash("Tu mensaje ha sido enviado correctamente. ¡Gracias por contactarnos!")
        except Exception as e:
            flash(f"Error al enviar el mensaje: {str(e)}")
        
        return redirect(url_for("contactos"))
    
    return render_template("contactos.html")
########--------Admin---------------------#################################
# Ruta para la página principal de login y registro
# Verificar si el usuario es administrador
def is_admin():
    return 'user_id' in session

# Ruta para login y registro
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'login':
            # Login de administrador
            username = request.form['username']
            password = request.form['password']
            admin = db_session.query(Administrador).filter_by(username=username).first()
            if admin and check_password_hash(admin.password_hash, password):
                session['user_id'] = admin.idAdmin
                session['username'] = admin.username
                flash('Inicio de sesión exitoso.', 'success')
                return redirect(url_for('menu'))  # Redirigir al menú principal
            else:
                flash('Usuario o contraseña incorrectos.', 'error')
    return render_template('admin.html')




@app.route('/admin/registrar', methods=['GET', 'POST'])
def registrar_admin():
    if request.method == 'POST':
        try:
            # Recibir datos del formulario
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            telefono = request.form.get('telefono', None)
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']

            # Validar duplicados
            if db_session.query(Administrador).filter_by(email=email).first():
                flash('El email ya está registrado.', 'error')
                return redirect(url_for('registrar_admin'))
            if db_session.query(Administrador).filter_by(username=username).first():
                flash('El username ya está registrado.', 'error')
                return redirect(url_for('registrar_admin'))

            # Crear y guardar nuevo administrador
            password_hash = generate_password_hash(password)
            nuevo_admin = Administrador(
                nombre=nombre,
                apellido=apellido,
                telefono=telefono,
                email=email,
                username=username,
                password_hash=password_hash
            )
            db_session.add(nuevo_admin)
            db_session.commit()

            flash('Administrador registrado exitosamente.', 'success')
            return redirect(url_for('admin'))
        except Exception as e:
            db_session.rollback()
            print(f"Error al registrar administrador: {e}")  # Imprimir el error en consola
            flash('Error interno. Intenta de nuevo.', 'error')

    return render_template('registrar_admin.html')








# Ruta para el menú principal
@app.route('/menu')
def menu():
    if not is_admin():
        flash('Debes iniciar sesión primero.', 'error')
        return redirect(url_for('admin'))
    return render_template('menu_admin.html')

# Rutas de CRUD para Ventas (solo administradores)

# Listar todas las ventas
@app.route('/ventas')
def listar_ventas():
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))
    ventas = db_session.query(Venta).all()
    return render_template('ventas_admin.html', ventas=ventas)

# Agregar una nueva venta
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

# Eliminar una venta
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

    # Obtener la venta a editar
    venta = db_session.query(Venta).get(id)
    if not venta:
        flash('Venta no encontrada.', 'error')
        return redirect(url_for('listar_ventas'))

    if request.method == 'POST':
        # Actualizar los campos de la venta
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

    # Obtener listas de datos relacionados
    propiedades = db_session.query(Propiedad).all()
    estatuses = db_session.query(Estatus).all()
    propietarios = db_session.query(Propietario).all()
    return render_template('editar_venta_admin.html', venta=venta, propiedades=propiedades, estatuses=estatuses, propietarios=propietarios)
#---------------------crud propiedades --------------------##### Ruta para editar propiedades
@app.route('/propiedades')
def listar_propiedades():
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))
    propiedades = db_session.query(Propiedad).all()
    return render_template('propiedades_admin.html', propiedades=propiedades)

from werkzeug.utils import secure_filename

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
        
        # Guardar imagen si se subió
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            filepath = filepath.replace("static/", "")  # Guardar ruta relativa
        else:
            filepath = None  # Imagen no subida

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

    # Obtener seguros de la base de datos para mostrarlos en el formulario
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

        # Actualizar imagen si se subió una nueva
        file = request.files['imagen']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            propiedad.imagen = filepath.replace("static/", "")  # Guardar ruta relativa

        try:
            db_session.commit()
            flash('Propiedad actualizada exitosamente.', 'success')
            return redirect(url_for('listar_propiedades'))
        except IntegrityError:
            db_session.rollback()
            flash('Error al actualizar la propiedad. Revisa los datos.', 'error')

    # Obtener seguros para el formulario
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
        # Eliminar la imagen asociada del servidor (si existe)
        if propiedad.imagen:
            filepath = os.path.join('static', propiedad.imagen)
            if os.path.exists(filepath):
                os.remove(filepath)

        db_session.delete(propiedad)
        db_session.commit()
        flash('Propiedad eliminada exitosamente.', 'success')
    except IntegrityError:
        db_session.rollback()
        flash('Error al eliminar la propiedad.', 'error')
    return redirect(url_for('listar_propiedades'))

#-------------Propietario--------------------------------#
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
#--------------------Seguro--------------------------------------------#
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

#------------------------Mudanza----------------------------------------#
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


@app.route('/mudanzas/editar/<int:id>', methods=['GET', 'POST'])
def editar_mudanza(id):
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))

    mudanza = db_session.query(Mudanza).get(id)
    if not mudanza:
        flash('Mudanza no encontrada.', 'error')
        return redirect(url_for('listar_mudanzas'))

    if request.method == 'POST':
        mudanza.idSfK2 = request.form['idSfK2']
        mudanza.idPropietario = request.form['idPropietario']
        mudanza.empresa_mudanza = request.form['empresa_mudanza']
        mudanza.fecha_mudanza = request.form['fecha_mudanza']
        mudanza.costo = request.form['costo']
        mudanza.comentarios = request.form['comentarios']
        try:
            db_session.commit()
            flash('Mudanza actualizada exitosamente.', 'success')
            return redirect(url_for('listar_mudanzas'))
        except IntegrityError:
            db_session.rollback()
            flash('Error al actualizar la mudanza. Revisa los datos.', 'error')

    seguros = db_session.query(Seguro).all()
    propietarios = db_session.query(Propietario).all()
    return render_template('editar_mudanza_admin.html', mudanza=mudanza, seguros=seguros, propietarios=propietarios)


@app.route('/mudanzas/eliminar/<int:id>', methods=['POST'])
def eliminar_mudanza(id):
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))

    mudanza = db_session.query(Mudanza).get(id)
    if not mudanza:
        flash('Mudanza no encontrada.', 'error')
        return redirect(url_for('listar_mudanzas'))

    try:
        db_session.delete(mudanza)
        db_session.commit()
        flash('Mudanza eliminada exitosamente.', 'success')
    except IntegrityError:
        db_session.rollback()
        flash('Error al eliminar la mudanza.', 'error')
    return redirect(url_for('listar_mudanzas'))

#------------------------------construciones------------------------------#
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
#----Dashboard----------------#
@app.route('/dashboard', methods=['GET'])
def dashboard():
    if not is_admin():
        flash('Debes iniciar sesión como administrador.', 'error')
        return redirect(url_for('admin'))
    return render_template('dashboard.html')

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


# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente.', 'success')
    return redirect(url_for('admin'))
#------------------------Busqueda cliente----------------------------------------#
@app.route('/busqueda_casas', methods=['GET', 'POST'])
def busqueda_casas():
    if request.method == 'POST':
        # Obtener los parámetros de búsqueda desde el formulario
        ciudad = request.form.get('ciudad')
        precio_min = request.form.get('precio_min', type=float)
        precio_max = request.form.get('precio_max', type=float)
        num_recamaras = request.form.get('num_recamaras', type=int)

        # Crear la consulta de búsqueda
        query = db_session.query(Propiedad).join(Venta, Propiedad.idPro == Venta.idProfk, isouter=True)
        query = query.filter(Venta.idProfk == None)  # Asegurarnos de buscar casas que no están vendidas

        if ciudad:
            query = query.filter(Propiedad.ciudad.ilike(f"%{ciudad}%"))
        if precio_min is not None:
            query = query.filter(Propiedad.precio >= precio_min)
        if precio_max is not None:
            query = query.filter(Propiedad.precio <= precio_max)
        if num_recamaras is not None:
            query = query.filter(Propiedad.num_recamaras == num_recamaras)

        # Ejecutar la consulta
        propiedades = query.all()
        return render_template('resultado_busqueda.html', propiedades=propiedades)

    return render_template('busqueda_casas.html')
#-----------------Reporte_casas--------------------#

@app.route('/reporte_casas', methods=['GET'])
def reporte_casas():
    # Consulta para obtener todas las propiedades con su estatus
    propiedades = (
        db_session.query(Propiedad, Venta)
        .outerjoin(Venta, Propiedad.idPro == Venta.idProfk)
        .all()
    )
    
    # Convertir los resultados a un formato procesable
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

    return render_template('reporte_casas.html', reporte=reporte)

@app.route('/ficha_tecnica/<int:id>', methods=['GET'])
def ficha_tecnica(id):
    # Consultar los datos de la casa específica
    propiedad = db_session.query(Propiedad).filter_by(idPro=id).first()

    if not propiedad:
        flash('La propiedad no existe.', 'error')
        return redirect(url_for('reporte_casas'))

    # Generar el contenido del PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Título
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt="Ficha Técnica de la Propiedad", ln=True, align='C')
    pdf.ln(10)

    # Datos de la propiedad
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Ciudad: {propiedad.ciudad}", ln=True)
    pdf.cell(200, 10, txt=f"Estado: {propiedad.estado}", ln=True)
    pdf.cell(200, 10, txt=f"Precio: ${propiedad.precio}", ln=True)
    pdf.cell(200, 10, txt=f"Número de Recámaras: {propiedad.num_recamaras}", ln=True)
    pdf.cell(200, 10, txt=f"Número de Baños: {propiedad.num_banos}", ln=True)
    pdf.ln(10)

    # Imagen (si está disponible)
    if propiedad.imagen:
        image_path = f"static/{propiedad.imagen}"
        try:
            pdf.image(image_path, x=10, y=pdf.get_y(), w=100)
        except:
            pdf.cell(200, 10, txt="Error al cargar la imagen.", ln=True)
    
    # Guardar el PDF en un archivo temporal
    file_path = f"static/ficha_tecnica_{id}.pdf"
    pdf.output(file_path)

    return send_file(file_path, as_attachment=True)

@app.route('/seleccionar_casa', methods=['GET'])
def seleccionar_casa():
    # Consultar todas las casas
    propiedades = db_session.query(Propiedad).all()
    return render_template('seleccionar_casa.html', propiedades=propiedades)



if __name__ == '__main__':
    app.run(debug=True)