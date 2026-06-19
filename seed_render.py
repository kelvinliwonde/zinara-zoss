"""
ZINARA ZOSS — seed_render.py (corrected)
Generates 100 fake users with vehicles, radio licenses, and applications.
Column names match backend/models.py exactly.
Run locally:
    $env:DATABASE_URL = "your-render-postgres-url"
    python seed_render.py
"""
import random
import os
from datetime import datetime, timedelta
from backend.app import app
from backend.models import db, User, Vehicle, RadioLicense, Application

ZIM_NAMES = [
    "Tendai Moyo", "Chipo Ncube", "Farai Dube", "Rudo Sibanda", "Takunda Muzenda",
    "Nyaradzo Chikwava", "Tafadzwa Makoni", "Kudzai Murewa", "Anesu Mhaka", "Rutendo Chikwanha",
    "Tinashe Moyo", "Chiedza Ndlovu", "Tafara Ngwenya", "Rumbidzai Mupfumi", "Kudakwashe Madziva",
    "Tanaka Bhebhe", "Nyasha Dube", "Munashe Mhlanga", "Tariro Chirisa", "Tafadzwa Nyathi",
]

VEHICLE_MAKES = ["Toyota", "Nissan", "Honda", "Ford", "Mercedes", "BMW", "Volkswagen", "Mazda"]
VEHICLE_MODELS = {
    "Toyota": ["Corolla", "Camry", "Hilux", "Fortuner", "Land Cruiser"],
    "Nissan": ["Sentra", "Altima", "Navara", "Patrol"],
    "Honda": ["Civic", "Accord", "CR-V"],
    "Ford": ["Fiesta", "Focus", "Ranger"],
    "Mercedes": ["C-Class", "E-Class"],
    "BMW": ["3 Series", "X3"],
    "Volkswagen": ["Golf", "Polo"],
    "Mazda": ["3", "CX-5"],
}
VEHICLE_TYPES = ["Car", "Kombi", "Bus", "Truck", "Motorcycle"]
VEHICLE_COLORS = ["White", "Black", "Silver", "Red", "Blue", "Green"]
INSURANCE_PROVIDERS = ["Nyaradzo Insurance", "Old Mutual", "Alliance Insurance", "Zimre", "FBC Insurance"]

RADIO_MAKES = ["Sony", "Panasonic", "Pioneer", "Kenwood", "JVC"]
RADIO_TYPES = ["AM", "FM", "Shortwave"]

used_emails = set()


def generate_national_id():
    prefix = random.choice(['63', '45', '28', '72', '34'])
    number = f"{random.randint(100000, 999999)}"
    letter = random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L'])
    return f"{prefix}-{number}{letter}"


def generate_phone():
    prefixes = ['071', '073', '077', '078']
    return f"{random.choice(prefixes)}{random.randint(1000000, 9999999)}"


def generate_vehicle_registration():
    letters = ''.join(random.choices('ABCDEFGHJKLMNOPRSTUVWXYZ', k=3))
    numbers = f"{random.randint(1000, 9999)}"
    return f"{letters} {numbers}"


def generate_radio_serial():
    return f"RADIO-{random.randint(100000, 999999)}"


def generate_email(name):
    domains = ['gmail.com', 'yahoo.com', 'zimweb.co.zw']
    first, last = name.lower().split(' ')
    for _ in range(100):
        email = f"{first}.{last}{random.randint(1, 999)}@{random.choice(domains)}"
        if email not in used_emails:
            used_emails.add(email)
            return email
    return f"{first}.{last}{random.randint(1, 9999)}@gmail.com"


def seed():
    with app.app_context():
        print("🗑️  Clearing existing data...")
        Application.query.delete()
        RadioLicense.query.delete()
        Vehicle.query.delete()
        User.query.delete()
        db.session.commit()

        print("👤 Creating 100 users...")
        users = []
        for _ in range(100):
            name = random.choice(ZIM_NAMES)
            user = User(
                name=name,
                email=generate_email(name),
                role='citizen',
                id_number=generate_national_id(),
                phone=generate_phone(),
                is_active=True,
            )
            user.set_password("Password123")
            users.append(user)
        db.session.add_all(users)
        db.session.commit()
        print(f"   ✅ {len(users)} users created (all password: Password123)")

        print("🚗 Creating vehicles...")
        vehicles = []
        for user in users:
            for _ in range(random.randint(1, 3)):
                make = random.choice(VEHICLE_MAKES)
                model = random.choice(VEHICLE_MODELS[make])
                expiry = datetime.now().date() + timedelta(days=random.randint(-90, 365))
                vehicles.append(Vehicle(
                    user_id=user.id,
                    registration_number=generate_vehicle_registration(),
                    vehicle_type=random.choice(VEHICLE_TYPES),
                    make=make,
                    model=model,
                    year=random.randint(2000, 2024),
                    color=random.choice(VEHICLE_COLORS),
                    engine_number=f"ENG{random.randint(100000, 999999)}",
                    chassis_number=f"CHS{random.randint(100000, 999999)}",
                    seating_capacity=random.randint(2, 50),
                    tare_weight=float(random.randint(800, 3000)),
                    insurance_provider=random.choice(INSURANCE_PROVIDERS),
                    insurance_policy_number=f"POL{random.randint(100000, 999999)}",
                    insurance_expiry_date=(datetime.now().date() + timedelta(days=random.randint(1, 365))).isoformat(),
                    license_expiry=expiry,
                    status='active' if expiry >= datetime.now().date() else 'expired',
                    is_active=True,
                ))
        db.session.add_all(vehicles)
        db.session.commit()
        print(f"   ✅ {len(vehicles)} vehicles created")

        print("📻 Creating radio licenses...")
        radios = []
        for user in users:
            if random.random() > 0.3:
                for _ in range(random.randint(1, 2)):
                    expiry = datetime.now().date() + timedelta(days=random.randint(-90, 365))
                    radios.append(RadioLicense(
                        user_id=user.id,
                        radio_serial_number=generate_radio_serial(),
                        radio_make=random.choice(RADIO_MAKES),
                        radio_model=f"Model{random.randint(100, 999)}",
                        radio_type=random.choice(RADIO_TYPES),
                        installation_location=random.choice(['Harare', 'Bulawayo', 'Mutare', 'Gweru']),
                        license_expiry=expiry,
                        status='active' if expiry >= datetime.now().date() else 'expired',
                        is_active=True,
                    ))
        db.session.add_all(radios)
        db.session.commit()
        print(f"   ✅ {len(radios)} radio licenses created")

        print("📄 Creating applications...")
        applications = []
        for _ in range(200):
            user = random.choice(users)
            user_vehicles = [v for v in vehicles if v.user_id == user.id]
            user_radios = [r for r in radios if r.user_id == user.id]
            app_type = random.choice(['vehicle', 'radio', 'both'])

            vehicle_id = random.choice(user_vehicles).id if user_vehicles and app_type in ('vehicle', 'both') else None
            radio_id = random.choice(user_radios).id if user_radios and app_type in ('radio', 'both') else None
            if not vehicle_id and not radio_id:
                continue

            fee = (50.0 if vehicle_id else 0) + (15.0 if radio_id else 0)
            applications.append(Application(
                user_id=user.id,
                vehicle_id=vehicle_id,
                radio_id=radio_id,
                type=app_type,
                amount=round(fee, 2),
                status=random.choice(['pending', 'verified', 'paid', 'completed']),
                notes=f"Renewal for {app_type} license",
            ))
        db.session.add_all(applications)
        db.session.commit()
        print(f"   ✅ {len(applications)} applications created")

        print("\n✅ Demo data seeded successfully!")
        print(f"   Users: {len(users)} | Vehicles: {len(vehicles)} | Radios: {len(radios)} | Applications: {len(applications)}")
        print("   All demo users have password: Password123")


if __name__ == "__main__":
    seed()
