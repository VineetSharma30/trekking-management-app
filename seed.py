from random import choice, randint, sample, shuffle
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import app
from extensions import db
from models import User, StaffProfile, Trek, Booking

first_names=[
    "Aarav","Vivaan","Aditya","Vihaan","Arjun","Krishna","Aryan","Kabir","Rohan","Rahul",
    "Ananya","Diya","Aditi","Sara","Meera","Ishita","Riya","Priya","Sneha","Kavya"
]

last_names=[
    "Sharma","Verma","Singh","Patel","Gupta","Yadav","Kumar","Joshi","Mehta","Kapoor",
    "Mishra","Jain","Malhotra","Bansal","Pandey","Chauhan","Sinha","Agarwal","Reddy","Nair"
]

treks=[
    (
        "Kedarkantha Trek",
        "Uttarakhand",
        "easy",
        5,
        6999,
        "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b"
    ),
    (
        "Valley of Flowers",
        "Uttarakhand",
        "easy",
        6,
        7999,
        "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee"
    ),
    (
        "Hampta Pass",
        "Himachal Pradesh",
        "moderate",
        6,
        9999,
        "https://images.unsplash.com/photo-1469474968028-56623f02e42e"
    ),
    (
        "Kuari Pass",
        "Uttarakhand",
        "easy",
        5,
        8499,
        "https://images.unsplash.com/photo-1441974231531-c6227db76b6e"
    ),
    (
        "Sandakphu Trek",
        "West Bengal",
        "moderate",
        7,
        11999,
        "https://images.unsplash.com/photo-1465189684280-6a8fa9b19a7a"
    ),
    (
        "Brahmatal Trek",
        "Uttarakhand",
        "easy",
        6,
        8999,
        "https://images.unsplash.com/photo-1454496522488-7a8e488e8606"
    ),
    (
        "Kashmir Great Lakes",
        "Jammu & Kashmir",
        "hard",
        8,
        18999,
        "https://images.unsplash.com/photo-1506744038136-46273834b3fb"
    ),
    (
        "Goechala Trek",
        "Sikkim",
        "hard",
        10,
        24999,
        "https://images.unsplash.com/photo-1447752875215-b2761acb3c5d"
    ),
    (
        "Rupin Pass",
        "Himachal Pradesh",
        "hard",
        8,
        17999,
        "https://images.unsplash.com/photo-1470770841072-f978cf4d019e"
    ),
    (
        "Har Ki Dun",
        "Uttarakhand",
        "moderate",
        7,
        10999,
        "https://images.unsplash.com/photo-1482192596544-9eb780fc7f66"
    ),
    (
        "Tarsar Marsar",
        "Jammu & Kashmir",
        "moderate",
        7,
        16499,
        "https://images.unsplash.com/photo-1439066615861-d1af74d74000"
    ),
    (
        "Everest Base Camp",
        "Nepal",
        "hard",
        12,
        35999,
        "https://images.unsplash.com/photo-1519904981063-b0cf448d479e"
    ),
    (
        "Annapurna Base Camp",
        "Nepal",
        "hard",
        11,
        32999,
        "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b"
    ),
    (
        "Roopkund Trek",
        "Uttarakhand",
        "hard",
        8,
        15999,
        "https://images.unsplash.com/photo-1448375240586-882707db888b"
    ),
    (
        "Pin Parvati Pass",
        "Himachal Pradesh",
        "hard",
        11,
        28999,
        "https://images.unsplash.com/photo-1465919292275-c60ba49da6ae"
    )
]

with app.app_context():

    db.create_all()

    db.session.query(Booking).delete()
    db.session.query(Trek).delete()
    db.session.query(StaffProfile).delete()
    db.session.query(User).filter(User.role != "admin").delete()
    db.session.commit()

    staff_members=[]
    approval_statuses = [
        "approved",
        "approved",
        "approved",
        "approved",
        "approved",
        "pending",
        "pending",
        "rejected"
    ]
    shuffle(approval_statuses)

    for i in range(1,9):
        user=User(
            username=f"staff{i}",
            email=f"staff{i}@trek.com",
            password_hash=generate_password_hash("staff123"),
            full_name=f"{choice(first_names)} {choice(last_names)}",
            phone=f"98{randint(10000000,99999999)}",
            role="staff",
            status="active"
        )
        db.session.add(user)
        db.session.flush()

        db.session.add(
            StaffProfile(
                user_id=user.id,
                approval_status=approval_statuses[i - 1],
                experience=randint(1,8)
            )
        )

        staff_members.append(user)

    users=[]

    for i in range(1,21):
        user=User(
            username=f"user{i}",
            email=f"user{i}@gmail.com",
            password_hash=generate_password_hash("user123"),
            full_name=f"{choice(first_names)} {choice(last_names)}",
            phone=f"97{randint(10000000,99999999)}",
            role="user",
            status="active"
        )
        db.session.add(user)
        users.append(user)

    db.session.commit()
    approved_staff_members = [
        staff for staff in staff_members
        if staff.staff_profile.approval_status == "approved"
        and staff.status == "active"
    ]

    trek_objects=[]

    for i,data in enumerate(treks):

        name,location,difficulty,duration,price,image=data

        total_slots=randint(20,40)

        status=choice([
            "open",
            "open",
            "open",
            "started",
            "ongoing",
            "closed",
            "completed"
        ])

        today = datetime.today().date()

        if status == "open":
            start_date = today + timedelta(days=randint(5, 45))
            end_date = start_date + timedelta(days=duration)

        elif status == "started":
            start_date = today
            end_date = start_date + timedelta(days=duration)

        elif status == "ongoing":
            start_date = today - timedelta(days=randint(1, duration - 1))
            end_date = start_date + timedelta(days=duration)

        elif status == "closed":
            start_date = today + timedelta(days=randint(5, 30))
            end_date = start_date + timedelta(days=duration)

        else:
            end_date = today - timedelta(days=randint(5, 30))
            start_date = end_date - timedelta(days=duration)

        trek=Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration_days=duration,
            total_slots=total_slots,
            available_slots=total_slots,
            assigned_staff_id=choice(approved_staff_members).id,
            image_url=image,
            price=price,
            status=status,
            start_date=start_date,
            end_date=end_date,
            description=f"Experience the breathtaking beauty of {name}. This professionally guided trek offers scenic landscapes, unforgettable trails, and an exciting adventure suitable for {difficulty} level trekkers."
        )

        db.session.add(trek)
        trek_objects.append(trek)

    db.session.commit()

    for user in users:

        available_treks=sample(
            trek_objects,
            randint(1,4)
        )

        for trek in available_treks:

            if trek.available_slots <= 0:
                continue

            if trek.status == "completed":
                booking_status = "completed"
                payment_status = "paid"

            elif trek.status == "closed":
                booking_status = choice([
                    "completed",
                    "completed",
                    "cancelled"
                ])
                payment_status = (
                    "paid"
                    if booking_status == "completed"
                    else "refunded"
                )

            elif trek.status in ["started", "ongoing"]:
                booking_status = "booked"
                payment_status = "paid"

            else:
                booking_status = choice([
                    "booked",
                    "booked",
                    "booked",
                    "cancelled"
                ])
                payment_status = (
                    "paid" if booking_status == "booked"
                    else "refunded"
                )

            if trek.status == "completed":
                booking_date = datetime.combine(
                    trek.start_date - timedelta(days=randint(3, 15)),
                    datetime.min.time()
                )

            elif trek.status in ["started", "ongoing"]:
                booking_date = datetime.combine(
                    trek.start_date - timedelta(days=randint(2, 10)),
                    datetime.min.time()
                )

            else:
                booking_date = datetime.combine(
                    today - timedelta(days=randint(1, 20)),
                    datetime.min.time()
                )

            booking=Booking(
                user_id=user.id,
                trek_id=trek.id,
                status=booking_status,
                payment_status=payment_status,
                booking_date=booking_date
            )

            db.session.add(booking)

            if booking_status in ["booked","completed"]:
                trek.available_slots -= 1

    db.session.commit()

print("\nDemo Data Generated Successfully\n")

print("Admin")
print("username: admin")
print("password: admin123\n")

print("Staff")
print("username: staff1, staff2, ..., staff8")
print("password: staff123\n")

print("Users")
print("username: user1, user2, ..., user20")
print("password: user123")
