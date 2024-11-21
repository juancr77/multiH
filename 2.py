from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from flask import Flask, render_template, request, redirect, url_for, flash, session
from models.Data import DatabaseSingleton, Administrador  # Importar desde tu archivo
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash, session
from models.Data import DatabaseSingleton, Administrador, Venta, Propiedad, Estatus, Propietario,Seguro
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError


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
app.config['MAIL_USERNAME'] = 'tu_correo@gmail.com'  # Cambia por tu correo
app.config['MAIL_PASSWORD'] = 'tu_contraseña'  # Cambia por tu contraseña

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

@app.route("/mudanzas")
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
                recipients=['destinatario@gmail.com'],  # Cambia por el correo de destino
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

        nueva_propiedad = Propiedad(
            ciudad=ciudad,
            estado=estado,
            codigo_postal=codigo_postal,
            precio=precio,
            num_recamaras=num_recamaras,
            num_banos=num_banos
        )
        try:
            db_session.add(nueva_propiedad)
            db_session.commit()
            flash('Propiedad agregada exitosamente.', 'success')
            return redirect(url_for('listar_propiedades'))
        except IntegrityError:
            db_session.rollback()
            flash('Error al agregar la propiedad. Revisa los datos.', 'error')

    return render_template('agregar_propiedad_admin.html')


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
        try:
            db_session.commit()
            flash('Propiedad actualizada exitosamente.', 'success')
            return redirect(url_for('listar_propiedades'))
        except IntegrityError:
            db_session.rollback()
            flash('Error al actualizar la propiedad. Revisa los datos.', 'error')

    return render_template('editar_propiedad_admin.html', propiedad=propiedad)


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

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente.', 'success')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)