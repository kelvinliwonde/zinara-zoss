import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.append(os.path.dirname(__file__))

# Set the database URL
os.environ['DATABASE_URL'] = 'postgresql://zinara_user:02UdcFjxHtFy2yaZCEAWK1pwV6KPwyjT@dpg-d8pv0t4vikkc73a192dg-a.oregon-postgres.render.com:5432/zinara'

# Import app and db
from backend.app import app
from backend.models import db
import data.seed

# Create tables and seed
with app.app_context():
    db.create_all()
    data.seed.generate_fake_data()
    print("✅ Seeding complete!")