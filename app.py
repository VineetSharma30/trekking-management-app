from flask import Flask
from models import db, User
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# Configs
app.config["SECRET_KEY"] = "your-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trekking.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# db
db.init_app(app)

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


# Temporary Route
@app.route("/")
def home():
    return "Trekking Management Application"


if __name__ == "__main__":
    init_db()
    app.run(debug=True)