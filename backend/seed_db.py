import os
import sys

# Set the database URL
os.environ['DATABASE_URL'] = 'postgresql://zinara_user:02UdcFjxHtFy2yaZCEAWK1pwV6KPwyjT@dpg-d8pv0t4vikkc73a192dg-a.oregon-postgres.render.com:5432/zinara'

# Import app and db
from app import app
from models import db

# Import the seed module
import importlib.util
spec = importlib.util.spec_from_file_location("seed", "../data/seed.py")
seed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seed)

# Run the seed
with app.app_context():
    db.create_all()
    seed.generate_fake_data()
    print("✅ Seeding complete!")