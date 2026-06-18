import random
import json
from datetime import datetime, timedelta
import time
import hashlib

# CRITICAL FIX: Correct import
from backend.models import db, Vehicle, RadioLicense, RenewalApplication, Payment

class ZINARAIntegration:
    
    ZINARA_VEHICLE_DB = {
        "ABC 1234": {"make": "Toyota", "model": "Corolla", "year": 2020, "status": "active"},
        "DEF 5678": {"make": "Honda", "model": "Civic", "year": 2019, "status": "active"},
        "GHI 9012": {"make": "Ford", "model": "Ranger", "year": 2021, "status": "active"},
        "JKL 3456": {"make": "Nissan", "model": "Navara", "year": 2018, "status": "active"},
        "MNO 7890": {"make": "Mercedes", "model": "C-Class", "year": 2022, "status": "active"},
    }
    
    @staticmethod
    def check_vehicle_status(registration_number):
        time.sleep(0.5)
        vehicle = ZINARAIntegration.ZINARA_VEHICLE_DB.get(registration_number.upper())
        if vehicle:
            return {
                "success": True,
                "status": vehicle["status"],
                "make": vehicle["make"],
                "model": vehicle["model"],
                "year": vehicle["year"],
                "message": "Vehicle found in ZINARA database"
            }
        else:
            if random.random() > 0.2:
                return {
                    "success": True,
                    "status": "active",
                    "make": random.choice(["Toyota", "Honda", "Nissan", "Ford", "BMW"]),
                    "model": random.choice(["Sedan", "SUV", "Truck", "Hatchback"]),
                    "year": random.randint(2010, 2024),
                    "message": "Vehicle verified with ZINARA"
                }
            else:
                return {
                    "success": False,
                    "status": "not_found",
                    "message": "Vehicle not found in ZINARA database. Please register at ZINARA office."
                }
    
    @staticmethod
    def check_radio_license(radio_serial):
        time.sleep(0.3)
        if random.random() > 0.15:
            return {
                "success": True,
                "status": "valid",
                "expiry_date": (datetime.now() + timedelta(days=random.randint(30, 365))).isoformat(),
                "message": "Radio license is valid"
            }
        else:
            return {
                "success": False,
                "status": "invalid",
                "message": "Radio license not found or expired. Please renew with ZBC."
            }
    
    @staticmethod
    def submit_application(application_data):
        time.sleep(1.0)
        ref_number = f"ZIN-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        approved = random.random() > 0.1
        return {
            "success": True,
            "reference_number": ref_number,
            "status": "approved" if approved else "pending_review",
            "estimated_processing_time": "2-3 business days",
            "message": "Application submitted to ZINARA successfully" if approved else "Application requires manual review",
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def check_application_status(reference_number):
        time.sleep(0.4)
        statuses = ["pending", "under_review", "approved", "completed", "rejected"]
        weights = [0.2, 0.3, 0.25, 0.2, 0.05]
        current_status = random.choices(statuses, weights=weights)[0]
        return {
            "success": True,
            "reference_number": reference_number,
            "status": current_status,
            "status_message": f"Application is {current_status.replace('_', ' ')}",
            "last_updated": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
            "estimated_completion": (datetime.now() + timedelta(days=random.randint(1, 5))).isoformat()
        }
    
    @staticmethod
    def process_payment(application_id, amount, payment_method):
        time.sleep(0.8)
        payment_ref = f"PAY-{datetime.now().strftime('%Y%m%d')}-{random.randint(10000, 99999)}"
        success = random.random() > 0.02
        return {
            "success": success,
            "payment_reference": payment_ref,
            "amount": amount,
            "payment_method": payment_method,
            "status": "completed" if success else "failed",
            "transaction_id": f"TX-{random.randint(100000, 999999)}",
            "timestamp": datetime.now().isoformat(),
            "message": "Payment processed successfully" if success else "Payment failed. Please try again."
        }
    
    @staticmethod
    def generate_digital_license(application_id, user_data, vehicle_data):
        time.sleep(0.6)
        license_number = f"LIC-{datetime.now().strftime('%Y%m%d')}-{random.randint(10000, 99999)}"
        qr_data = {
            "license_number": license_number,
            "owner": user_data.get("full_name", ""),
            "vehicle": vehicle_data.get("registration_number", ""),
            "issued_date": datetime.now().isoformat(),
            "expiry_date": (datetime.now() + timedelta(days=365)).isoformat(),
            "verification_url": f"https://verify.zinara.co.zw/{license_number}"
        }
        hash_string = f"{license_number}{qr_data['owner']}{qr_data['vehicle']}{qr_data['expiry_date']}"
        verification_hash = hashlib.sha256(hash_string.encode()).hexdigest()[:16]
        return {
            "success": True,
            "license_number": license_number,
            "qr_code_data": json.dumps(qr_data),
            "verification_hash": verification_hash,
            "issued_date": datetime.now().isoformat(),
            "expiry_date": (datetime.now() + timedelta(days=365)).isoformat(),
            "digital_download_url": f"https://licenses.zinara.co.zw/{license_number}.pdf",
            "message": "Digital license generated successfully"
        }
    
    @staticmethod
    def get_real_time_data():
        return {
            "system_status": "operational",
            "queue_size": random.randint(0, 50),
            "average_processing_time": f"{random.randint(2, 10)} minutes",
            "total_applications_today": random.randint(200, 800),
            "system_uptime": "99.8%",
            "last_maintenance": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
        }