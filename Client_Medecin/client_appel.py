import requests

def check_doctor_availability(doctor_id, appointment_date, appointment_time):
    url = "http://medecin-service/availability/check"
    data = {
        "doctor_id": doctor_id,
        "appointment_date": appointment_date,
        "appointment_time": appointment_time
    }
    response = requests.post(url, json=data)

    if response.status_code == 200:
        return response.json().get('available', False)
    return False
