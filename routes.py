import requests
from flask import Blueprint, request, jsonify
from models import Appointment, db
from datetime import datetime

routes = Blueprint("routes", __name__)

# Configuration pour l'URL du service utilisateur
USER_SERVICE_URL = "http://localhost:8081/api/medecins"

# Route de la page d'accueil
@routes.route('/')
def home():
    return 'Bienvenue sur la page d\'accueil !'

# Récupérer tous les rendez-vous
@routes.route("/appointments", methods=["GET"])
def get_appointments():
    appointments = Appointment.query.all()
    return jsonify([{
        "id": a.id,
        "patient_name": a.patient_name,
        "doctor_id": a.doctor_id,  # Utiliser doctor_id
        "appointment_date": a.appointment_date,
        "notes": a.notes
    } for a in appointments])

# Créer un nouveau rendez-vous
@routes.route("/appointments", methods=["POST"])
def create_appointment():
    data = request.json

    # Vérifier si le médecin existe en appelant l'API REST du service utilisateur
    doctor_id = data["doctor_id"]
    response = requests.get(f"{USER_SERVICE_URL}/{doctor_id}/exists")
    if response.status_code != 200 or not response.json():
        return jsonify({"message": "Doctor not found"}), 404

    new_appointment = Appointment(
        patient_name=data["patient_name"],
        doctor_id=doctor_id,  # Utiliser doctor_id
        appointment_date=datetime.strptime(data["appointment_date"], "%Y-%m-%d"),
        notes=data.get("notes", ""),
        is_cancelled=data.get("is_cancelled", False)
    )
    db.session.add(new_appointment)
    db.session.commit()
    return jsonify({"message": "Appointment created!"}), 201

# Récupérer un rendez-vous spécifique par ID
@routes.route("/appointments/<int:id>", methods=["GET"])
def get_appointment(id):
    appointment = Appointment.query.get(id)
    if appointment is None:
        return jsonify({"message": "Appointment not found"}), 404
    return jsonify({
        "id": appointment.id,
        "patient_name": appointment.patient_name,
        "doctor_id": appointment.doctor_id,  # Utiliser doctor_id
        "appointment_date": appointment.appointment_date,
        "notes": appointment.notes
    })

# Mettre à jour un rendez-vous
@routes.route("/appointments/<int:id>", methods=["PUT"])
def update_appointment(id):
    appointment = Appointment.query.get(id)
    if appointment is None:
        return jsonify({"message": "Appointment not found"}), 404

    data = request.json
    appointment.patient_name = data.get("patient_name", appointment.patient_name)
    appointment.doctor_id = data.get("doctor_id", appointment.doctor_id)  # Utiliser doctor_id
    appointment.appointment_date = datetime.strptime(data.get("appointment_date", appointment.appointment_date.strftime("%Y-%m-%d")), "%Y-%m-%d")
    appointment.notes = data.get("notes", appointment.notes)

    db.session.commit()
    return jsonify({"message": "Appointment updated!"})

# Supprimer un rendez-vous
@routes.route("/appointments/<int:id>", methods=["DELETE"])
def delete_appointment(id):
    appointment = Appointment.query.get(id)
    if appointment is None:
        return jsonify({"message": "Appointment not found"}), 404

    db.session.delete(appointment)
    db.session.commit()
    return jsonify({"message": "Appointment deleted!"})
