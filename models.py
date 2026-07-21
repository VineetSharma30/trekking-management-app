from extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model) :
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    password_hash = db.Column(db.String(256), nullable = False)
    full_name = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable = False, default = "user")  # admin, staff, user
    status = db.Column(db.String(20), nullable = False, default = "active")  # active, blacklisted
    created_at = db.Column(db.DateTime, default = datetime.utcnow)
    
    # Relationships
    bookings = db.relationship("Booking", backref="user", lazy = True)
    assigned_treks = db.relationship("Trek", backref = "assigned_staff", lazy = True, foreign_keys = "Trek.assigned_staff_id")
    staff_profile = db.relationship("StaffProfile", backref = "user", uselist = False, lazy = True)

    def __repr__(self):
        return f"<User {self.username}>"

class StaffProfile(db.Model) :
    __tablename__ = "staff_profiles"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key = True)
    approval_status = db.Column(db.String(20), nullable = False, default = "pending")
    experience = db.Column(db.Integer)

    def __repr__(self):
        return f"<StaffProfile User:{self.user_id}>"

class Trek(db.Model) :
    __tablename__ = "treks"

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150), nullable = False)
    location = db.Column(db.String(150), nullable = False)
    difficulty = db.Column(db.String(20), nullable = False)  # Easy, Moderate, Hard
    duration_days = db.Column(db.Integer, nullable = False)
    total_slots = db.Column(db.Integer, nullable = False)
    available_slots = db.Column(db.Integer, nullable = False)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = True)
    status = db.Column(db.String(20), nullable = False, default="Open")  # Open, Closed, Completed
    start_date = db.Column(db.Date, nullable = False)
    end_date = db.Column(db.Date, nullable = False)
    description = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default = datetime.utcnow)

    # Relationships
    bookings = db.relationship("Booking", backref = "trek", lazy = True)

    def __repr__(self):
        return f"<Trek {self.name}>"

class Booking(db.Model) :
    __tablename__ = "bookings"    

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable = False)
    payment_status = db.Column(db.String(20), nullable = False, default = "pending" ) # Pending, Paid, Refunded
    status = db.Column(db.String(20), nullable = False, default = "booked")  # Booked, Cancelled, Completed
    booking_date = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return f"<Booking {self.id}>"