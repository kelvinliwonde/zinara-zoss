"""
ZINARA ZOSS — backend/services/zinara_integration.py
Wrapper around the ZINARA external API.
Falls back to mock data when ZINARA_API_URL is not set (dev / demo mode).
"""

import os
import requests
from datetime import date, timedelta
import random


class ZinaraIntegrationService:

    def __init__(self):
        self.api_url  = os.environ.get('ZINARA_API_URL', '')
        self.api_key  = os.environ.get('ZINARA_API_KEY', '')
        self.demo_mode = not self.api_url

    # ── Public methods ────────────────────────────────────────
    def lookup_vehicle(self, registration: str) -> dict:
        if self.demo_mode:
            return self._mock_vehicle(registration)
        try:
            resp = requests.post(
                f'{self.api_url}/vehicles/lookup',
                json={'registration': registration},
                headers=self._headers(),
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {'error': f'ZINARA service unavailable: {str(e)}'}

    def lookup_radio_license(self, license_number: str) -> dict:
        if self.demo_mode:
            return self._mock_radio(license_number)
        try:
            resp = requests.post(
                f'{self.api_url}/radio/lookup',
                json={'license_number': license_number},
                headers=self._headers(),
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {'error': f'ZINARA service unavailable: {str(e)}'}

    def health_check(self) -> dict:
        if self.demo_mode:
            return {'status': 'demo', 'message': 'Running in demo mode (ZINARA_API_URL not set)'}
        try:
            resp = requests.get(f'{self.api_url}/health', headers=self._headers(), timeout=5)
            resp.raise_for_status()
            return {'status': 'connected', 'message': 'ZINARA API is reachable'}
        except requests.RequestException as e:
            return {'status': 'error', 'message': str(e)}

    # ── Internal helpers ──────────────────────────────────────
    def _headers(self):
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type':  'application/json',
        }

    def _mock_vehicle(self, registration: str) -> dict:
        makes  = ['Toyota', 'Honda', 'Ford', 'Mazda', 'Nissan', 'Isuzu']
        models = ['Hilux', 'Fit', 'Ranger', 'CX-5', 'Navara', 'D-Max']
        expiry = date.today() + timedelta(days=random.randint(-30, 365))
        return {
            'registration':   registration,
            'make':           random.choice(makes),
            'model':          random.choice(models),
            'year':           random.randint(2010, 2023),
            'color':          random.choice(['White', 'Silver', 'Black', 'Blue', 'Red']),
            'engine_number':  f'ENG{random.randint(100000, 999999)}',
            'chassis_number': f'CH{random.randint(100000, 999999)}',
            'license_expiry': expiry.isoformat(),
            'status':         'active' if expiry >= date.today() else 'expired',
            'source':         'demo',
        }

    def _mock_radio(self, license_number: str) -> dict:
        expiry = date.today() + timedelta(days=random.randint(-30, 365))
        return {
            'license_number': license_number,
            'holder':         'Demo Holder',
            'frequency':      f'{random.uniform(88, 108):.1f} MHz',
            'expiry':         expiry.isoformat(),
            'status':         'active' if expiry >= date.today() else 'expired',
            'source':         'demo',
        }
