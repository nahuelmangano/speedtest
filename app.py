from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
import speedtest
import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()  # carga variables del archivo .env

app = Flask(__name__)

# Configuración clave secreta para sesiones y flashes
app.secret_key = os.environ.get("SECRET_KEY", "clave_super_secreta_cambiame")

# Configuración PostgreSQL con variable de entorno
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://nmangano:tu_password_seguro@localhost/portfolio_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar base de datos
db = SQLAlchemy(app)

# Tabla intermedia para relación muchos a muchos entre usuarios y roles
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)  # Sin límite de tamaño
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

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
        return jsonify({
            "download": download,
            "upload": upload,
            "ping": ping
        })
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

# Ruta protegida, solo para usuarios logueados
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        flash("Por favor logueate primero", "error")
        return redirect(url_for("login"))
    users = User.query.all()
    return render_template("dashboard.html", users=users)

# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Sesión cerrada", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Crear roles por defecto si no existen
        for role_name in ["admin", "user", "moderator"]:
            rol = Role.query.filter_by(name=role_name).first()
            if not rol:
                db.session.add(Role(name=role_name))
        db.session.commit()

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
