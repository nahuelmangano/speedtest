from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
import speedtest
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from models import db, User, Role, Categoria, Producto, user_roles

load_dotenv()  # carga variables del archivo .env

app = Flask(__name__)

# Configuración clave secreta
app.secret_key = os.environ.get("SECRET_KEY", "clave_super_secreta_cambiame")

# Configuración base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://nmangano:tu_password_seguro@localhost/portfolio_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar DB con app
db.init_app(app)

# Carpeta para uploads
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# --- Helpers ---
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Crear tablas y roles por defecto ---
with app.app_context():
    db.create_all()
    for role_name in ["admin", "user", "moderator"]:
        rol = Role.query.filter_by(name=role_name).first()
        if not rol:
            db.session.add(Role(name=role_name))
    db.session.commit()

# --- RUTAS PRINCIPALES ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/tortugas")
def tortugas_page():
    return render_template("tortuga.html")

@app.route("/perlin")
def perlin_page():
    return render_template("rperlin.html")

@app.route("/speedtest")
def speedtest_page():
    return render_template("speedtest.html")

@app.route("/run-speedtest")
def run_speedtest():
    try:
        test = speedtest.Speedtest()
        download = round(test.download() / 10**6, 2)
        upload = round(test.upload() / 10**6, 2)
        ping = test.results.ping
        return jsonify({"download": download, "upload": upload, "ping": ping})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- RUTAS DE AUTENTICACIÓN ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["user"] = user.username
            flash("Login exitoso", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Usuario o contraseña incorrectos", "error")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("El usuario ya existe", "error")
            return redirect(url_for("register"))

        new_user = User(username=username)
        new_user.set_password(password)

        # Asignar rol por defecto "user"
        role_user = Role.query.filter_by(name="user").first()
        if not role_user:
            role_user = Role(name="user")
            db.session.add(role_user)
            db.session.commit()

        new_user.roles.append(role_user)

        db.session.add(new_user)
        db.session.commit()

        flash("Registro exitoso, ahora podés ingresar", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

# --- RUTAS PROTEGIDAS ---
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        flash("Por favor logueate primero", "error")
        return redirect(url_for("login"))
    users = User.query.all()
    productos = Producto.query.all()
    return render_template("dashboard.html", users=users, productos=productos)

@app.route("/agregar_producto", methods=["GET", "POST"])
def agregar_producto():
    if "user" not in session:
        flash("Por favor logueate primero", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        nombre = request.form["nombre"]
        precio = request.form["precio"]
        stock = request.form["stock"]
        color = request.form.get("color")
        descripcion = request.form.get("descripcion")
        categoria_id = request.form.get("categoria_id")

        # Procesar la imagen
        imagen = request.files.get("imagen")
        imagen_url = None
        if imagen and imagen.filename != "":
            filename = secure_filename(imagen.filename)
            # Asegurarse de que exista la carpeta uploads
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            imagen.save(filepath)
            imagen_url = f"/static/uploads/{filename}"

        nuevo_producto = Producto(
            nombre=nombre,
            precio=precio,
            stock=stock,
            color=color,
            descripcion=descripcion,
            categoria_id=categoria_id,
            imagen_url=imagen_url
        )
        db.session.add(nuevo_producto)
        db.session.commit()

        flash("Producto agregado correctamente", "success")
        return redirect(url_for("dashboard"))

    categorias = Categoria.query.all()
    return render_template("agregar_producto.html", categorias=categorias)

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Sesión cerrada", "info")
    return redirect(url_for("login"))

#TIENDA PART
@app.route("/tienda")
def tienda():
    productos = Producto.query.all()
    return render_template("tienda.html", productos=productos)

# Mostrar un producto específico
@app.route("/producto/<int:producto_id>")
def producto_page(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    return render_template("producto.html", producto=producto)

# Ruta para agregar al carrito (solo un ejemplo simple)
@app.route("/agregar_carrito/<int:producto_id>")
def agregar_carrito(producto_id):
    if "carrito" not in session:
        session["carrito"] = []
    session["carrito"].append(producto_id)
    flash("Producto agregado al carrito", "success")
    return redirect(url_for("tienda"))

# Ruta para comprar (puede ser redirigir al checkout o procesar compra)
@app.route("/comprar/<int:producto_id>")
def comprar(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    # Aquí podrías restar stock, generar orden, etc.
    flash(f"Compra de {producto.nombre} realizada con éxito!", "success")
    return redirect(url_for("tienda"))



#FIN TIENDA PART
# --- RUN APP ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
