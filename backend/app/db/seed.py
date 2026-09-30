import sys
from pathlib import Path
from datetime import datetime, date, timezone

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy.orm import Session
from backend.app.db.config import Base, engine, SessionLocal
from backend.app.db.models import User, Farm, Crop, WeatherData, SoilData, Prediction, ChatMessage
from backend.app.auth.security import get_password_hash

def seed_initial_accounts(db: Session = None):
    """
    Idempotently seeds required administrator and farmer accounts into the database.
    Ensures Two distinct Administrator accounts:
    1. Admin 1: admin1@yieldsense.com
    2. Admin 2: admin2@yieldsense.com
    Plus primary farmers and testing accounts.
    """
    close_db_after = False
    if db is None:
        db = SessionLocal()
        close_db_after = True

    try:
        # Create all tables if not present
        Base.metadata.create_all(bind=engine)

        accounts_to_seed = [
            # Two Administrator accounts
            {
                "email": "admin1@yieldsense.com",
                "name": "Admin One (Lead System Admin)",
                "password": "Admin1@2026!",
                "role": "Administrator",
                "farms": []
            },
            {
                "email": "admin2@yieldsense.com",
                "name": "Admin Two (Operations & Verification Admin)",
                "password": "Admin2@2026!",
                "role": "Administrator",
                "farms": []
            },
            # Backward-compatible admin accounts for tests
            {
                "email": "admin@yieldsense.com",
                "name": "YieldSense Administrator",
                "password": "adminpassword123",
                "role": "Administrator",
                "farms": []
            },
            {
                "email": "admin@test.com",
                "name": "Test System Administrator",
                "password": "adminpassword123",
                "role": "Administrator",
                "farms": []
            },
            {
                "email": "m3_admin@test.com",
                "name": "M3 Super Admin",
                "password": "adminpassword123",
                "role": "Administrator",
                "farms": []
            },
            {
                "email": "m3_admin1@test.com",
                "name": "M3 Admin One",
                "password": "adminpassword123",
                "role": "Administrator",
                "farms": []
            },
            {
                "email": "m3_admin2@test.com",
                "name": "M3 Admin Two",
                "password": "adminpassword123",
                "role": "Administrator",
                "farms": []
            },
            # Real Farmer accounts
            {
                "email": "farmer1@yieldsense.com",
                "name": "Ramesh Patel",
                "password": "Farmer1@2026!",
                "role": "Farmer",
                "farms": [
                    {
                        "farm_name": "Green Acres Farm",
                        "location": "Ludhiana, Punjab",
                        "area": 25.5,
                        "soil_type": "Loamy",
                        "crops": [
                            {"crop_name": "Wheat", "season": "Rabi", "historical_yield": 4200.0},
                            {"crop_name": "Rice", "season": "Kharif", "historical_yield": 3800.0}
                        ],
                        "soil": {"nitrogen": 85.0, "phosphorus": 45.0, "potassium": 50.0, "ph": 6.8},
                        "weather": {"temperature": 26.5, "rainfall": 140.0, "humidity": 65.0},
                        "prediction": {
                            "state": "Punjab", "crop": "Wheat", "soil_type": "Loamy",
                            "fertilizer": "DAP", "predicted_yield_kg": 4350.0, "status": "Optimized"
                        }
                    }
                ]
            },
            {
                "email": "farmer2@yieldsense.com",
                "name": "Sunita Sharma",
                "password": "Farmer2@2026!",
                "role": "Farmer",
                "farms": [
                    {
                        "farm_name": "Surya Krishi Kendra",
                        "location": "Nashik, Maharashtra",
                        "area": 18.0,
                        "soil_type": "Black",
                        "crops": [
                            {"crop_name": "Soybean", "season": "Kharif", "historical_yield": 2400.0},
                            {"crop_name": "Cotton", "season": "Kharif", "historical_yield": 1900.0}
                        ],
                        "soil": {"nitrogen": 70.0, "phosphorus": 55.0, "potassium": 48.0, "ph": 7.2},
                        "weather": {"temperature": 29.0, "rainfall": 110.0, "humidity": 58.0},
                        "prediction": {
                            "state": "Maharashtra", "crop": "Soybean", "soil_type": "Black",
                            "fertilizer": "Urea", "predicted_yield_kg": 2650.0, "status": "High Productivity"
                        }
                    }
                ]
            }
        ]

        for acc in accounts_to_seed:
            existing = db.query(User).filter(User.email == acc["email"]).first()
            if not existing:
                user = User(
                    name=acc["name"],
                    email=acc["email"],
                    password_hash=get_password_hash(acc["password"]),
                    role=acc["role"]
                )
                db.add(user)
                db.commit()
                db.refresh(user)

                # Seed associated farms/crops/predictions if any
                for f_data in acc.get("farms", []):
                    farm = Farm(
                        user_id=user.id,
                        farm_name=f_data["farm_name"],
                        location=f_data["location"],
                        area=f_data["area"],
                        soil_type=f_data["soil_type"]
                    )
                    db.add(farm)
                    db.commit()
                    db.refresh(farm)

                    for c_data in f_data.get("crops", []):
                        crop = Crop(
                            farm_id=farm.id,
                            crop_name=c_data["crop_name"],
                            season=c_data["season"],
                            historical_yield=c_data.get("historical_yield")
                        )
                        db.add(crop)

                    if "soil" in f_data:
                        s = f_data["soil"]
                        db.add(SoilData(
                            farm_id=farm.id,
                            nitrogen=s["nitrogen"],
                            phosphorus=s["phosphorus"],
                            potassium=s["potassium"],
                            ph=s["ph"]
                        ))

                    if "weather" in f_data:
                        w = f_data["weather"]
                        db.add(WeatherData(
                            farm_id=farm.id,
                            temperature=w["temperature"],
                            rainfall=w["rainfall"],
                            humidity=w["humidity"],
                            date=date.today()
                        ))

                    if "prediction" in f_data:
                        p = f_data["prediction"]
                        db.add(Prediction(
                            user_id=user.id,
                            farm_id=farm.id,
                            crop_id=crop.id if 'crop' in locals() else None,
                            state=p["state"],
                            crop=p["crop"],
                            soil_type=p["soil_type"],
                            fertilizer=p["fertilizer"],
                            n=f_data["soil"]["nitrogen"],
                            p=f_data["soil"]["phosphorus"],
                            k=f_data["soil"]["potassium"],
                            rainfall_mm=f_data["weather"]["rainfall"],
                            temperature_c=f_data["weather"]["temperature"],
                            soil_ph=f_data["soil"]["ph"],
                            year=2026,
                            predicted_yield_kg=p["predicted_yield_kg"],
                            predicted_yield_tons=round(p["predicted_yield_kg"] / 1000.0, 3),
                            productivity_category=p.get("status", "Optimized"),
                            recommendation_summary="Maintain balanced soil nutrition and scheduled watering.",
                            model_name="LinearRegression"
                        ))

                    db.commit()
            else:
                # Update password hash and role
                existing.password_hash = get_password_hash(acc["password"])
                existing.role = acc["role"]
                db.commit()

                # If existing user has no farms but has farms defined in seed, add them
                if acc.get("farms") and not existing.farms:
                    for f_data in acc.get("farms", []):
                        farm = Farm(
                            user_id=existing.id,
                            farm_name=f_data["farm_name"],
                            location=f_data["location"],
                            area=f_data["area"],
                            soil_type=f_data["soil_type"]
                        )
                        db.add(farm)
                        db.commit()
                        db.refresh(farm)

                        for c_data in f_data.get("crops", []):
                            crop = Crop(
                                farm_id=farm.id,
                                crop_name=c_data["crop_name"],
                                season=c_data["season"],
                                historical_yield=c_data.get("historical_yield")
                            )
                            db.add(crop)

                        if "soil" in f_data:
                            s = f_data["soil"]
                            db.add(SoilData(
                                farm_id=farm.id,
                                nitrogen=s["nitrogen"],
                                phosphorus=s["phosphorus"],
                                potassium=s["potassium"],
                                ph=s["ph"]
                            ))

                        if "weather" in f_data:
                            w = f_data["weather"]
                            db.add(WeatherData(
                                farm_id=farm.id,
                                temperature=w["temperature"],
                                rainfall=w["rainfall"],
                                humidity=w["humidity"],
                                date=date.today()
                            ))

                        if "prediction" in f_data:
                            p = f_data["prediction"]
                            db.add(Prediction(
                                user_id=existing.id,
                                farm_id=farm.id,
                                crop_id=crop.id if 'crop' in locals() else None,
                                state=p["state"],
                                crop=p["crop"],
                                soil_type=p["soil_type"],
                                fertilizer=p["fertilizer"],
                                n=f_data["soil"]["nitrogen"],
                                p=f_data["soil"]["phosphorus"],
                                k=f_data["soil"]["potassium"],
                                rainfall_mm=f_data["weather"]["rainfall"],
                                temperature_c=f_data["weather"]["temperature"],
                                soil_ph=f_data["soil"]["ph"],
                                year=2026,
                                predicted_yield_kg=p["predicted_yield_kg"],
                                predicted_yield_tons=round(p["predicted_yield_kg"] / 1000.0, 3),
                                productivity_category=p.get("status", "Optimized"),
                                recommendation_summary="Maintain balanced soil nutrition and scheduled watering.",
                                model_name="LinearRegression"
                            ))

                        db.commit()

                # If existing user has farms but no predictions and seed has predictions, add them
                elif acc.get("farms") and not existing.predictions:
                    for f_data in acc.get("farms", []):
                        if "prediction" in f_data and existing.farms:
                            f_inst = existing.farms[0]
                            p = f_data["prediction"]
                            db.add(Prediction(
                                user_id=existing.id,
                                farm_id=f_inst.id,
                                state=p["state"],
                                crop=p["crop"],
                                soil_type=p["soil_type"],
                                fertilizer=p["fertilizer"],
                                n=f_data["soil"]["nitrogen"],
                                p=f_data["soil"]["phosphorus"],
                                k=f_data["soil"]["potassium"],
                                rainfall_mm=f_data["weather"]["rainfall"],
                                temperature_c=f_data["weather"]["temperature"],
                                soil_ph=f_data["soil"]["ph"],
                                year=2026,
                                predicted_yield_kg=p["predicted_yield_kg"],
                                predicted_yield_tons=round(p["predicted_yield_kg"] / 1000.0, 3),
                                productivity_category=p.get("status", "Optimized"),
                                recommendation_summary="Maintain balanced soil nutrition and scheduled watering.",
                                model_name="LinearRegression"
                            ))
                            db.commit()

        print("Database seed completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        if close_db_after:
            db.close()

if __name__ == "__main__":
    seed_initial_accounts()
