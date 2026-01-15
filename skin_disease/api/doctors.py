import random

SPECIALTIES = ["dermatologist", "oncologist", "general"]

def get_doctors_for_hospital(hospital_name, base_lat, base_lon):
    doctors = []

    for i in range(3):
        doctors.append({
            "id": f"{hospital_name[:3]}-{i}",
            "name": f"Dr. {random.choice(['Amit', 'Sarah', 'Ravi', 'Emily'])}",
            "specialty": random.choice(SPECIALTIES),
            "rating": round(random.uniform(4.0, 4.9), 1),
            "experience_years": random.randint(5, 25),
            "distance_km": round(random.uniform(0.5, 5), 1),
        })

    return doctors
