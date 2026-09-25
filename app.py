from flask import Flask, render_template, redirect, url_for
from models import User
from werkzeug.security import generate_password_hash
from extensions import db, login_manager
from routes import auth, admin, staff, user
from flask_login import current_user

import os
import shutil

app = Flask(__name__)

# Configs
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your-secret-key")

database_url = os.environ.get("DATABASE_URL")
if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
elif os.environ.get("VERCEL"):
    db_path = "/tmp/trekking.db"
    seed_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trekking_init.db")
    if not os.path.exists(db_path) and os.path.exists(seed_db):
        try:
            shutil.copy2(seed_db, db_path)
        except Exception as e:
            print("Failed to copy seed db:", e)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trekking.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# db
db.init_app(app)

# Login
login_manager.init_app(app)
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"

# Blueprints
app.register_blueprint(auth.auth_bp, url_prefix = "/auth")
app.register_blueprint(admin.admin_bp, url_prefix = "/admin")
app.register_blueprint(staff.staff_bp, url_prefix = "/staff")
app.register_blueprint(user.user_bp, url_prefix = "/user")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def init_db() : 
    with app.app_context() :
        db.create_all()

        admin = User.query.filter_by(username = "admin").first()
        if not admin :
            admin = User(
                # Default Admin Credentials
                username = "admin",
                email = "admin@trek.com",
                password_hash = generate_password_hash("admin123"),
                full_name = "System Administrator",
                role = "admin",
                status = "active"
            )
            db.session.add(admin)
            db.session.commit()
            print("Default admin created.")
        else :
            print("Default admin already exists.")

with app.app_context():
    try:
        init_db()
    except Exception as e:
        print("Database initialization note:", e)



@app.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        elif current_user.role == "staff":
            return redirect(url_for("staff.dashboard"))
        else:
            return redirect(url_for("user.dashboard"))
    return render_template("landing.html")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)