from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message

# Configuración de la aplicación Flask
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Clave secreta para mensajes flash

# Configuración del servidor de correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Servidor SMTP
app.config['MAIL_PORT'] = 587  # Puerto SMTP
app.config['MAIL_USE_TLS'] = True  # Activar encriptación TLS
app.config['MAIL_USE_SSL'] = False  # No usar SSL
app.config['MAIL_USERNAME'] = 'reissjony411@gmail.com'  # Cambia por tu correo
app.config['MAIL_PASSWORD'] = 'thae labz ojig nest'  # Cambia por tu contraseña

mail = Mail(app)

# Ruta para la página principal
@app.route("/")
def index():
    return render_template("index.html")

# Otras rutas (agrega aquí todas tus rutas necesarias)
@app.route("/la_compania")
def la_compania():
    return render_template("la_compania.html")

@app.route("/servicios")
def servicios():
    return render_template("servicios.html")

@app.route("/requisitos")
def requisitos():
    return render_template("requisitos.html")

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

@app.route("/seguros")
def seguros():
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
                recipients=['reissjony411@gmail.com'],  # Cambia por el correo de destino
                body=f"Nombre: {nombre}\nCorreo: {email}\nMensaje: {mensaje}"
            )
            mail.send(msg)
            flash("Tu mensaje ha sido enviado correctamente. ¡Gracias por contactarnos!")
        except Exception as e:
            flash(f"Error al enviar el mensaje: {str(e)}")
        return redirect(url_for("contactos"))
    return render_template("contactos.html")

# Ejecutar la aplicación con recarga automática
if __name__ == "__main__":
    app.run(debug=True)
