# 🏔️ Trekking Management Application

A role-based **Trekking Management Application** developed using **Flask**, **SQLite**, and **Bootstrap 5** for the **Modern Application Development I (MAD-I)** course under the **IIT Madras BS Degree in Data Science and Applications**.

The application provides separate portals for **Administrators**, **Trek Staff**, and **Trekkers**, enabling complete trek management, participant management, booking management, demo payments, and trekking history.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/) [![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/) [![SQLite](https://img.shields.io/badge/Database-SQLite-orange.svg)](https://www.sqlite.org/) [![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple.svg)](https://getbootstrap.com/)

---

## ✨ Features

### 🔐 Authentication

- User Registration
- Secure Login
- Password Hashing using Werkzeug
- Flask-Login Session Management
- Role-Based Access Control

---

### 👨‍💼 Admin Portal

- Dashboard with system statistics
- Create new treks
- Edit trek information
- Delete treks
- Assign/Reassign trek staff
- Upload trek image URLs
- View all bookings
- Approve or reject staff registrations
- Activate or blacklist users
- Activate or blacklist staff
- Search users
- Search staff
- Search treks
- Search bookings

---

### 🧗 Staff Portal

- Staff Dashboard
- View assigned treks
- Manage assigned trek
- Update trek status
- Manage available slots
- View trek participants
- Mark participant bookings as completed
- Update personal profile

---

### 🥾 User Portal

- Browse available treks
- Search treks
- Filter by difficulty
- Filter by location
- View trek details
- Demo payment page
- Book treks
- Cancel bookings
- View active bookings
- View trekking history
- Update profile

---

## 📋 Booking Features

- Duplicate booking prevention
- Prevent overbooking
- Automatic slot management
- Demo payment workflow
- Booking cancellation
- Refund status tracking
- Trek completion tracking

### Trek Status

- Open
- Closed
- Started
- Ongoing
- Completed

### Booking Status

- Booked
- Cancelled
- Completed

### Payment Status

- Pending
- Paid
- Refunded

---

## 🛠️ Technology Stack

### Backend

- Flask
- Flask-SQLAlchemy
- Flask-Login
- Werkzeug

### Frontend

- HTML5
- CSS3
- Bootstrap 5
- Bootstrap Icons
- Jinja2

### Database

- SQLite

---

## 🗄️ Database Schema

---

### Entity Relationship Diagram

                           USER
                  ┌──────────────────────┐
                  │ id (PK)              │
                  │ username (UNIQUE)    │
                  │ email (UNIQUE)       │
                  │ password_hash        │
                  │ full_name            │
                  │ phone                │
                  │ role                 │
                  │ status               │
                  │ created_at           │
                  └──────────────────────┘
                     │               │
                 1:1 │               │ 1:N
                     ▼               ▼

         STAFF_PROFILE             BOOKING
      ┌───────────────────┐    ┌──────────────────┐
      │ user_id (PK)(FK)  │    │ id (PK)          │
      │ approval_status   │    │ user_id (FK)     │
      │ experience        │    │ trek_id (FK)     │
      └───────────────────┘    │ payment_status   │
                               │ status           │
                               │ booking_date     │
                               └──────────────────┘
                                       ▲
                                       │ N:1
                                       │

                                    TREK                  
                               ┌────────────────────────┐
                               │ id (PK)                │
                               │ assigned_staff_id (FK) │
                               │ name                   │
                               │ location               │
                               │ difficulty             │
                               │ duration_days          │
                               │ total_slots            │
                               │ available_slots        │
                               │ price                  │
                               │ image_url              │
                               │ description            │
                               │ start_date             │
                               │ end_date               │
                               │ status                 │
                               │ created_at             │
                               └────────────────────────┘

## 📡 Route Design

### Authentication

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET, POST | `/auth/login` | User Login |
| GET, POST | `/auth/register` | User Registration |
| GET | `/auth/logout` | Logout |

---

### Admin Routes

| Method | Endpoint |
|---------|----------|
| GET | `/admin/dashboard` |
| GET | `/admin/treks` |
| GET, POST | `/admin/treks/create` |
| GET, POST | `/admin/treks/<id>/edit` |
| POST | `/admin/treks/<id>/delete` |
| GET, POST | `/admin/treks/<id>/assign` |
| GET | `/admin/staff` |
| POST | `/admin/staff/<id>/approve` |
| POST | `/admin/staff/<id>/reject` |
| GET | `/admin/users` |
| POST | `/admin/account/<id>/status` |
| GET | `/admin/bookings` |

---

### Staff Routes

| Method | Endpoint |
|---------|----------|
| GET | `/staff/dashboard` |
| GET | `/staff/treks` |
| GET, POST | `/staff/treks/<id>` |
| GET | `/staff/participants` |
| POST | `/staff/bookings/<id>/complete` |
| GET, POST | `/staff/profile` |

---

### User Routes

| Method | Endpoint |
|---------|----------|
| GET | `/user/dashboard` |
| GET | `/user/treks` |
| GET | `/user/treks/<id>` |
| GET, POST | `/user/treks/<id>/payment` |
| GET | `/user/bookings` |
| GET | `/user/bookings/<id>` |
| POST | `/user/bookings/<id>/cancel` |
| GET | `/user/history` |
| GET, POST | `/user/profile` |

---

## 📂 Project Structure

```text
trekking-management-app/
│
├── app.py                              # Application entry point
├── extensions.py
├── models.py                           # SQLAlchemy models
├── requirements.txt
├── README.md
├── seed.py                             # Demo data generator
│
├── routes/                             # Blueprint definitions
│   ├── __init__.py
│   ├── admin.py
│   ├── auth.py
│   ├── staff.py
│   ├── user.py
│   └── utils.py
│
├── static/
│   ├── css/style.css                   # Custom stylesheets
│   └── images/default-trek.jpg         # Static images
│       
│
├── templates/                          # Jinja2 HTML Templates
│   ├── admin/
│   │   ├── assign_staff.html
│   │   ├── bookings.html
│   │   ├── create_trek.html
│   │   ├── dashboard.html
│   │   ├── edit_trek.html
│   │   ├── staff.html
│   │   ├── treks.html
│   │   └── users.html
│   │
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   │
│   ├── staff/
│   │   ├── dashboard.html
│   │   ├── manage_trek.html
│   │   ├── my_treks.html
│   │   ├── participants.html
│   │   └── profile.html
│   │
│   ├── user/
│   │   ├── booking_details.html
│   │   ├── browse_treks.html
│   │   ├── dashboard.html
│   │   ├── history.html
│   │   ├── my_bookings.html
│   │   ├── payment.html
│   │   ├── profile.html
│   │   └── trek_details.html
│   │
│   ├── base.html
│   └── landing.html
│
└── instance/                           # SQLite database

```

---

## 🚀 Quick Start

Clone the repository

```bash
# 1. Clone the repository
git clone https://github.com/24f2002648/trekking-management-app.git
cd trekking-management-app

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment

## Windows
venv\Scripts\activate
## macOS / Linux
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Generate Demo Data (Optional but recommended)
python seed.py

# 6. Run the application
python app.py
```

> ⚠️ **Note:** The `seed.py` script is provided strictly for generating demo data and populating the database during development or evaluation.

The application will start on **http://127.0.0.1:5000**

---

## 🔑 Demo Credentials

> **Note:** The application automatically creates the default administrator on first run. Running `seed.py` additionally generates demo staff, trekkers, treks, and bookings.


### Administrator

| Username | Password |
|----------|----------|
| admin | admin123 |

---

### Staff

| Username | Password |
|----------|----------|
| staff1 | staff123 |
| staff2 | staff123 |
| staff3 | staff123 |
| staff4 | staff123 |
| staff5 | staff123 |
| staff6 | staff123 |
| staff7 | staff123 |
| staff8 | staff123 |

---

### Users

| Username | Password |
|----------|----------|
| user1 | user123 |
| user2 | user123 |
| user3 | user123 |
| user4 | user123 |
| user5 | user123 |
| user6 | user123 |
| user7 | user123 |
| user8 | user123 |
| user9 | user123 |
| user10 | user123 |
| user11 | user123 |
| user12 | user123 |
| user13 | user123 |
| user14 | user123 |
| user15 | user123 |
| user16 | user123 |
| user17 | user123 |
| user18 | user123 |
| user19 | user123 |
| user20 | user123 |

---

## ✅ Validation Rules

- Duplicate trek bookings are prevented.
- Users can book only open treks.
- Users cannot book treks with no available slots.
- Slots are automatically updated after booking and cancellation.
- Only approved staff can access the staff portal.
- Only assigned staff can manage their assigned treks.
- Users can only view and manage their own bookings.
- Administrators have complete access to all modules.

---

## 🤖 AI Usage Declaration

AI tools (ChatGPT) were used as a development assistant for:

- Debugging
- Code review
- UI improvements
- Documentation drafting
- Refactoring suggestions

The application architecture, database design, implementation, testing, and integration were completed and verified by the author.

---

## 👨‍🎓 Academic Information

**Course**

Modern Application Development I (MAD-I)

**Institution**

Indian Institute of Technology Madras

**Programme**

BS Degree in Data Science and Applications

---

<div align="center">

Made with ❤️ by **Vineet Sharma**

</div>