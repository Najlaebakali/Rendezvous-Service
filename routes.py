import requests
from flask import Blueprint, request, jsonify
from models import Appointment, db
from datetime import datetime
from client_grpc.Patient_Service import add_patient
from client_grpc.Protos import patient_pb2, patient_pb2_grpc
import grpc


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





# gRPC Config
PATIENT_SERVICE_HOST = 'localhost'
PATIENT_SERVICE_PORT = 5065

def get_patient_service_stub():
    channel = grpc.insecure_channel(f"{PATIENT_SERVICE_HOST}:{PATIENT_SERVICE_PORT}")
    return patient_pb2_grpc.PatientProtoStub(channel)

@routes.route('/appointments', methods=['POST'])
def create_appointment():
    data = request.json

    # Verify if the doctor exists by calling the User Service API
    doctor_id = data["doctor_id"]
    user_service_url = f"{USER_SERVICE_URL}/{doctor_id}/exists"
    try:
        response = requests.get(user_service_url)
        if response.status_code == 200:
            doctor_exists = response.json()  # Directly use the boolean response
            if not doctor_exists:
                return jsonify({"message": "Doctor not found"}), 404
        else:
            return jsonify({"message": "Error checking doctor existence"}), response.status_code
    except requests.RequestException as e:
        return jsonify({"message": f"Error communicating with User Service: {str(e)}"}), 500 

    # Call gRPC to add patient
    try:
        patient_data = patient_pb2.Patient(
            name=data["patient_name"],
            address=data.get("address", ""),
            email=data.get("email", ""),
            phoneNumber=data.get("phone_number", ""),
            gender=data.get("gender", "")
        )
        add_patient_request = patient_pb2.AddPatientRequest(patient=patient_data)
        stub = get_patient_service_stub()
        grpc_response = stub.AddPatient(add_patient_request)
        if grpc_response.message != "Create success":
            return jsonify({"message": "Failed to create patient via gRPC"}), 500
    except grpc.RpcError as e:
        return jsonify({"error": e.details(), "message": "gRPC call failed"}), 500
    
    # Simulate saving appointment to database (mocked)
    new_appointment = {
        "patient_name": data["patient_name"],
        "doctor_id": doctor_id,
        "appointment_date": data["appointment_date"],
        "notes": data.get("notes", ""),
        "is_cancelled": data.get("is_cancelled", False),
    }
    return jsonify({"message": "Appointment and patient created successfully!", "appointment": new_appointment}), 201

#CODE DOUAE




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



# Récupérer tous les rendez-vous d'un médecin spécifique par son ID
@routes.route("/appointments/medecin/<int:doctor_id>", methods=["GET"])
def get_appointments_by_doctor(doctor_id):
    appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
    if not appointments:
        return jsonify({"message": "No appointments found for this doctor"}), 404
    return jsonify([{
        "id": a.id,
        "patient_name": a.patient_name,
        "doctor_id": a.doctor_id,
        "appointment_date": a.appointment_date.strftime("%Y-%m-%d"),
        "notes": a.notes
    } for a in appointments])
