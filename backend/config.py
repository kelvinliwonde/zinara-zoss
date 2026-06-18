import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Application
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
    
    # Database - Works for both local SQLite and Render PostgreSQL
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        # Use PostgreSQL on Render
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Fallback to SQLite locally
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DB_PATH = os.path.join(BASE_DIR, '..', 'data', 'zinara.db')
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # License Fees
    VEHICLE_LICENSE_FEE = 50.00
    RADIO_LICENSE_FEE = 15.00
    PENALTY_PER_DAY = 0.50
    MAX_PENALTY_DAYS = 90
    
    # CORS - Allow local and production
    CORS_ORIGINS = [
        'http://localhost:3000',
        'http://localhost:5000',
        'http://127.0.0.1:5000',
        'http://127.0.0.1:5500',
        'https://zinaraz-zoss.onrender.com',
        'https://zinara-zoss.onrender.com',
        'https://*.onrender.com'
    ]