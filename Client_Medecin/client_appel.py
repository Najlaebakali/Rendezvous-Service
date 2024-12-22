import requests

MEDECIN_SERVICE_URL = "http://localhost:8083/calendrier"

def check_doctor_availability(doctor_id, start_date, end_date):
    """
    Vérifie la disponibilité du médecin via le microservice Médecin
    """
    try:
        # Construire l'URL de l'API Médecin
        url = f"{MEDECIN_SERVICE_URL}/checkAvailability"
        params = {
            "doctorId": doctor_id,
            "startDate": start_date,
            "endDate": end_date
        }
        # Effectuer la requête GET
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()  # Retourne True ou False selon la réponse
        else:
            # Gestion des erreurs
            print(f"Erreur de l'API Médecin : {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion au service Médecin : {e}")
        return False
