"""
ZINARA ZOSS — backend/config.py
"""

import os
from datetime import timedelta


class Config:
    # ── Security ──────────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY', 'zinara-zoss-secret-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'zinara-jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # ── Database ──────────────────────────────────────────────
    # Render provides DATABASE_URL; fall back to local SQLite for dev
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///zinara.db'
    )
    # Render Postgres URLs start with postgres://, SQLAlchemy needs postgresql://
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── CORS ──────────────────────────────────────────────────
    CORS_ORIGINS = os.environ.get(
        'CORS_ORIGINS',
        'http://localhost:5000,http://localhost:3000,https://zinaraz-zoss.onrender.com'
    ).split(',')

    # ── Environment ───────────────────────────────────────────
    ENVIRONMENT = os.environ.get('FLASK_ENV', 'production')
    DEBUG = ENVIRONMENT == 'development'
