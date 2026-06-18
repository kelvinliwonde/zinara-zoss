# ============================================================
# ZINARA Integration Service
# Simulates connection to ZINARA's real backend
# ============================================================

import random
import json
from datetime import datetime, timedelta
import time
import hashlib

# FIXED: Changed from 'from models import...' to 'from backend.models import...'
from backend.models import db, Vehicle, RadioLicense, RenewalApplication, Payment

class ZINARAIntegration:
    """Simulates ZINARA's real backend integration"""
    
    # Simulated ZINARA database of approved vehicles
    ZINARA_VEHICLE_DB = {
        "ABC 1234": {"make": "Toyota", "model": "Corolla", "year": 2020, "status": "active"},
        "DEF 5678": {"make": "Honda", "model": "Civic", "year": 2019, "status": "active"},
        "GHI 9012": {"make": "Ford", "model": "Ranger", "year": 2021, "status": "active"},
        "JKL 3456": {"make": "Nissan", "model": "Navara", "year": 2018, "status": "active"},
        "MNO 7890": {"make": "Mercedes", "model": "C-Class", "year": 2022, "status": "active"},
    }
    
    @staticmethod
    def check_vehicle_status(registration_number):
        """
        Check if a vehicle is registered and active in ZINARA's system
        Returns: dict with status, make, model, year
        """
        # Simulate API call delay
        time.sleep(0.5)  # Simulate network latency
        
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
            # Simulate checking against a larger database
            # In real scenario, this would be an API call to ZINARA
            if random.random() > 0.2:  # 80% chance of being found
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
        """
        Check radio license status with ZBC (Zimbabwe Broadcasting Corporation)
        Returns: dict with status
        """
        time.sleep(0.3)  # Simulate API call
        
        # Simulate ZBC database check
        if random.random() > 0.15:  # 85% chance radio license is valid
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
        """
        Submit renewal application to ZINARA's backend
        Returns: dict with reference number and status
        """
        time.sleep(1.0)  # Simulate processing time
        
        # Generate ZINARA reference number
        ref_number = f"ZIN-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        
        # Simulate approval decision (90% approval rate)
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
        """
        Check the status of a submitted application with ZINARA
        Returns: dict with current status
        """
        time.sleep(0.4)
        
        # Simulate different statuses
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
        """
        Simulate payment processing through ZINARA's payment gateway
        Returns: dict with payment confirmation
        """
        time.sleep(0.8)
        
        # Generate payment reference
        payment_ref = f"PAY-{datetime.now().strftime('%Y%m%d')}-{random.randint(10000, 99999)}"
        
        # Simulate payment success (98% success rate)
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
        """
        Generate a digital license from ZINARA
        Returns: dict with license details and QR code data
        """
        time.sleep(0.6)
        
        # Generate unique license number
        license_number = f"LIC-{datetime.now().strftime('%Y%m%d')}-{random.randint(10000, 99999)}"
        
        # Generate QR code data
        qr_data = {
            "license_number": license_number,
            "owner": user_data.get("full_name", ""),
            "vehicle": vehicle_data.get("registration_number", ""),
            "issued_date": datetime.now().isoformat(),
            "expiry_date": (datetime.now() + timedelta(days=365)).isoformat(),
            "verification_url": f"https://verify.zinara.co.zw/{license_number}"
        }
        
        # Create a hash for verification
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
        """
        Get real-time data from ZINARA (simulated)
        Returns: dict with system status and metrics
        """
        return {
            "system_status": "operational",
            "queue_size": random.randint(0, 50),
            "average_processing_time": f"{random.randint(2, 10)} minutes",
            "total_applications_today": random.randint(200, 800),
            "system_uptime": "99.8%",
            "last_maintenance": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
        }