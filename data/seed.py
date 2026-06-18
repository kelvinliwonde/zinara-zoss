import random
import sqlite3
from datetime import datetime, timedelta
import bcrypt

# Zimbabwean names
ZIM_NAMES = [
    "Tendai Moyo", "Chipo Ncube", "Farai Dube", "Rudo Sibanda", "Takunda Muzenda",
    "Nyaradzo Chikwava", "Tafadzwa Makoni", "Kudzai Murewa", "Anesu Mhaka", "Rutendo Chikwanha",
    "Tinashe Moyo", "Chiedza Ndlovu", "Tafara Ngwenya", "Rumbidzai Mupfumi", "Kudakwashe Madziva",
    "Tanaka Bhebhe", "Nyasha Dube", "Munashe Mhlanga", "Tariro Chirisa", "Tafadzwa Nyathi"
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
    "Mazda": ["3", "CX-5"]
}
VEHICLE_TYPES = ["Car", "Kombi", "Bus", "Truck", "Motorcycle"]
VEHICLE_COLORS = ["White", "Black", "Silver", "Red", "Blue", "Green"]
INSURANCE_PROVIDERS = ["Nyaradzo Insurance", "Old Mutual", "Alliance Insurance", "Zimre", "FBC Insurance"]

RADIO_MAKES = ["Sony", "Panasonic", "Pioneer", "Kenwood", "JVC"]
RADIO_TYPES = ["AM", "FM", "Shortwave"]

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
    return f"{first}.{last}{random.randint(1, 99)}@{random.choice(domains)}"

def generate_fake_data():
    conn = sqlite3.connect('zinara.db')
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute('DELETE FROM audit_logs')
    cursor.execute('DELETE FROM payments')
    cursor.execute('DELETE FROM renewal_applications')
    cursor.execute('DELETE FROM radio_licenses')
    cursor.execute('DELETE FROM vehicles')
    cursor.execute('DELETE FROM users')
    
    users = []
    vehicles = []
    radio_licenses = []
    applications = []
    payments = []
    
    # Generate 100 users
    for i in range(100):
        name = random.choice(ZIM_NAMES)
        password = bcrypt.hashpw("Password123".encode('utf-8'), bcrypt.gensalt())
        user = (
            generate_national_id(),
            name,
            generate_email(name),
            generate_phone(),
            password.decode('utf-8'),
            'citizen',
            1,
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
            1
        )
        users.append(user)
        
        # Generate 1-3 vehicles per user
        for v in range(random.randint(1, 3)):
            make = random.choice(VEHICLE_MAKES)
            model = random.choice(VEHICLE_MODELS[make])
            year = random.randint(2000, 2024)
            expiry_date = datetime.now().date() + timedelta(days=random.randint(-90, 365))
            last_renewal = expiry_date - timedelta(days=random.randint(300, 400))
            vehicle = (
                i + 1,
                generate_vehicle_registration(),
                random.choice(VEHICLE_TYPES),
                make,
                model,
                year,
                f"ENG{random.randint(100000, 999999)}",
                f"CHS{random.randint(100000, 999999)}",
                random.choice(VEHICLE_COLORS),
                random.randint(2, 50),
                random.randint(800, 3000),
                random.choice(INSURANCE_PROVIDERS),
                f"POL{random.randint(100000, 999999)}",
                (datetime.now().date() + timedelta(days=random.randint(1, 365))).isoformat(),
                last_renewal.isoformat(),
                expiry_date.isoformat(),
                1
            )
            vehicles.append(vehicle)
        
        # Generate radio licenses
        if random.random() > 0.3:
            for r in range(random.randint(1, 2)):
                expiry_date = datetime.now().date() + timedelta(days=random.randint(-90, 365))
                radio = (
                    i + 1,
                    generate_radio_serial(),
                    random.choice(RADIO_MAKES),
                    f"Model{random.randint(100, 999)}",
                    random.choice(RADIO_TYPES),
                    random.choice(['Harare', 'Bulawayo', 'Mutare', 'Gweru']),
                    (expiry_date - timedelta(days=random.randint(300, 400))).isoformat(),
                    expiry_date.isoformat(),
                    1
                )
                radio_licenses.append(radio)
    
    # Insert users
    cursor.executemany('''
        INSERT INTO users (national_id, full_name, email, phone, password_hash, role, is_verified, created_at, updated_at, last_login, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', users)
    conn.commit()
    
    # Get user IDs
    cursor.execute('SELECT id FROM users')
    user_ids = [row[0] for row in cursor.fetchall()]
    
    # Insert vehicles
    updated_vehicles = []
    for i, vehicle in enumerate(vehicles):
        user_id = user_ids[i % len(user_ids)]
        updated_vehicles.append((user_id,) + vehicle[1:])
    
    cursor.executemany('''
        INSERT INTO vehicles (user_id, registration_number, vehicle_type, make, model, year, engine_number, chassis_number, color, seating_capacity, tare_weight, insurance_provider, insurance_policy_number, insurance_expiry_date, last_renewal_date, expiry_date, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', updated_vehicles)
    conn.commit()
    
    # Insert radio licenses
    updated_radios = []
    for i, radio in enumerate(radio_licenses):
        user_id = user_ids[i % len(user_ids)]
        updated_radios.append((user_id,) + radio[1:])
    
    cursor.executemany('''
        INSERT INTO radio_licenses (user_id, radio_serial_number, radio_make, radio_model, radio_type, installation_location, last_renewal_date, expiry_date, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', updated_radios)
    conn.commit()
    
    # Generate applications
    cursor.execute('SELECT id, user_id FROM vehicles')
    vehicle_data = cursor.fetchall()
    cursor.execute('SELECT id, user_id FROM radio_licenses')
    radio_data = cursor.fetchall()
    
    for i in range(200):
        user_id = random.choice(user_ids)
        app_type = random.choice(['vehicle', 'radio', 'both'])
        
        vehicle_id = None
        radio_id = None
        fee = 50.00
        penalty = 0.00
        
        if app_type in ['vehicle', 'both']:
            matching = [v[0] for v in vehicle_data if v[1] == user_id]
            if matching:
                vehicle_id = random.choice(matching)
                fee = 50.00
                penalty = random.choice([0, 5, 10, 15])
        
        if app_type in ['radio', 'both']:
            matching = [r[0] for r in radio_data if r[1] == user_id]
            if matching:
                radio_id = random.choice(matching)
                fee += 15.00
        
        if not vehicle_id and not radio_id:
            continue
        
        total = fee + penalty
        status = random.choice(['pending', 'verified', 'paid', 'completed'])
        
        app_date = datetime.now() - timedelta(days=random.randint(1, 30))
        app = (
            user_id,
            vehicle_id,
            radio_id,
            app_type,
            status,
            round(fee, 2),
            round(penalty, 2),
            round(total, 2),
            app_date.isoformat(),
            app_date.isoformat() if status in ['verified', 'paid', 'completed'] else None,
            (app_date + timedelta(minutes=random.randint(5, 60))).isoformat() if status in ['paid', 'completed'] else None,
            (app_date + timedelta(minutes=random.randint(10, 120))).isoformat() if status == 'completed' else None,
            '',
            '',
            f"Renewal for {app_type} license"
        )
        applications.append(app)
    
    if applications:
        cursor.executemany('''
            INSERT INTO renewal_applications (user_id, vehicle_id, radio_license_id, application_type, status, fee_amount, penalty_fee, total_amount, application_date, verification_date, payment_date, completion_date, qr_code, digital_license_path, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', applications)
        conn.commit()
    
    # Generate payments
    cursor.execute('SELECT id, user_id FROM renewal_applications WHERE status IN ("paid", "completed")')
    app_ids = cursor.fetchall()
    
    for app_id, user_id in app_ids:
        if random.random() > 0.2:
            payment_method = random.choice(['ecocash', 'telecash', 'onecard'])
            payment_reference = f"ZIN{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
            amount = round(random.uniform(30, 150), 2)
            payment = (
                app_id,
                user_id,
                payment_method,
                payment_reference,
                amount,
                'completed',
                f"TX{random.randint(100000, 999999)}",
                (datetime.now() - timedelta(minutes=random.randint(1, 60))).isoformat(),
                (datetime.now() - timedelta(minutes=random.randint(1, 120))).isoformat(),
                '{"status": "success"}'
            )
            payments.append(payment)
    
    if payments:
        cursor.executemany('''
            INSERT INTO payments (application_id, user_id, payment_method, payment_reference, amount, status, transaction_id, payment_date, settlement_date, gateway_response)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', payments)
    
    conn.commit()
    conn.close()
    print("✅ Fake data generated successfully!")
    print(f"   - Users: {len(users)}")
    print(f"   - Vehicles: {len(vehicles)}")
    print(f"   - Radio Licenses: {len(radio_licenses)}")
    print(f"   - Applications: {len(applications)}")
    print(f"   - Payments: {len(payments)}")

if __name__ == "__main__":
    generate_fake_data()