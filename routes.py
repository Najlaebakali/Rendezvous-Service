import requests
from flask import Blueprint, request, jsonify
from models import Appointment, db
from datetime import datetime
from client_grpc.Patient_Service import add_patient
from client_grpc.Patient_Service import get_patient_details
from client_grpc.Patient_Service import update_patient
from client_grpc.Protos import patient_pb2, patient_pb2_grpc
import grpc
from flasgger import Swagger, swag_from


routes = Blueprint("routes", __name__)

# Configuration pour l'URL du service utilisateur
USER_SERVICE_URL = "http://localhost:8081/api/medecins"

# Route de la page d'accueil
@routes.route('/')
@swag_from({
    'tags': ['Accueil'],
    'responses': {
        200: {
            'description': "Bienvenue sur la page d'accueil"
        }
    }
})
def home():
    return 'Bienvenue sur la page d\'accueil !'

# Récupérer tous les rendez-vous
@routes.route("/appointments", methods=["GET"])
@swag_from({
    'tags': ['Appointments'],
    'summary': 'Récupérer tous les rendez-vous',
    'responses': {
        200: {
            'description': "Liste de tous les rendez-vous",
            'examples': {
                'application/json': [
                    {
                        "id": 1,
                        "patient": {
                            "id": 123,
                            "name": "John Doe",
                            "address": "123 Main St",
                            "email": "john.doe@example.com",
                            "phone_number": "123-456-7890",
                            "gender": "M"
                        },
                        "doctor_id": 10,
                        "appointment_date": "2024-01-01 10:00:00",
                        "notes": "Follow-up visit"
                    }
                ]
            }
        }
    }
})
def get_appointments():
    # Récupérer tous les rendez-vous depuis la base de données
    appointments = Appointment.query.all()
    appointments_list = []

    for a in appointments:
        # Utiliser l'ID du patient dans le rendez-vous pour récupérer les détails du patient via gRPC
        patient_details = get_patient_details(a.patient_id)
        
        if patient_details is None:
            continue  # Si le patient n'est pas trouvé, on passe à l'élément suivant

        # Formater la date du rendez-vous pour un format lisible
        appointment_date = a.appointment_date.strftime("%Y-%m-%d %H:%M:%S")

        # Ajouter les détails du rendez-vous et du patient à la liste
        appointments_list.append({
            "id": a.id,
            "patient": {
                "id": patient_details.patient.id,  # Accéder à l'ID du patient via 'patient'
                "name": patient_details.patient.name,  # Accéder au nom du patient via 'patient'
                "address": patient_details.patient.address,  # Accéder à l'adresse via 'patient'
                "email": patient_details.patient.email,  # Accéder à l'email via 'patient'
                "phone_number": patient_details.patient.phoneNumber,  # Accéder au téléphone via 'patient'
                "gender": patient_details.patient.gender  # Accéder au genre via 'patient'
            },
            "doctor_id": a.doctor_id,
            "appointment_date": appointment_date,
            "notes": a.notes
        })
    
    # Retourner la liste des rendez-vous au format JSON
    return jsonify(appointments_list)




'''créer un rendez-vous, en appelant d'abord les services externes (gRPC et API), puis en enregistrant les données dans la base de données.'''


# gRPC Config
PATIENT_SERVICE_HOST = 'localhost'
PATIENT_SERVICE_PORT = 5065

def get_patient_service_stub():
    channel = grpc.insecure_channel(f"{PATIENT_SERVICE_HOST}:{PATIENT_SERVICE_PORT}")
    return patient_pb2_grpc.PatientProtoStub(channel)

@routes.route('/appointments', methods=['POST'])
@swag_from({
    'tags': ['Appointments'],
    'summary': 'Créer un rendez-vous',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'patient_name': {'type': 'string'},
                    'address': {'type': 'string'},
                    'email': {'type': 'string'},
                    'phone_number': {'type': 'string'},
                    'gender': {'type': 'string'},
                    'doctor_id': {'type': 'integer'},
                    'appointment_date': {'type': 'string', 'format': 'date'},
                    'notes': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': "Rendez-vous créé avec succès",
        },
        400: {
            'description': "Erreur dans les données fournies"
        }
    }
})
def create_appointment():
    data = request.json

    # Vérifier si le médecin existe en appelant l'API du service utilisateur
    doctor_id = data["doctor_id"]
    user_service_url = f"{USER_SERVICE_URL}/{doctor_id}/exists"
    try:
        response = requests.get(user_service_url)
        if response.status_code != 200:
            return jsonify({"message": "Error checking doctor existence", "error": response.json()}), response.status_code
        doctor_exists = response.json()
        if not doctor_exists:
            return jsonify({"message": "Doctor not found"}), 404
    except requests.RequestException as e:
        return jsonify({"message": f"Error communicating with User Service: {str(e)}"}), 500

    # Préparer les données du patient pour gRPC
    patient_data = patient_pb2.Patient(
        name=data.get("patient_name", ""),
        address=data.get("address", ""),
        email=data.get("email", ""),
        phoneNumber=data.get("phone_number", ""),
        gender=data.get("gender", "")
    )

    # Appeler le service gRPC via Patient_Service.py
    grpc_response, grpc_error = add_patient(patient_data)
    if grpc_error:
        return jsonify({"error": grpc_error, "message": "gRPC call failed"}), 500

    # Extraire le patientId à partir de la réponse gRPC
    patient_id = grpc_response.patientId

    # Convertir la date du rendez-vous
    try:
        appointment_date = datetime.strptime(data["appointment_date"], "%Y-%m-%d")
    except ValueError:
        return jsonify({"message": "Invalid date format. Expected format: YYYY-MM-DD"}), 400

    # Enregistrer le rendez-vous dans la base de données
    try:
        new_appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            notes=data.get("notes", ""),
            is_cancelled=data.get("is_cancelled", False),
        )
        db.session.add(new_appointment)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": f"Database error: {str(e)}"}), 500

    # Retourner la réponse avec les détails du patient et du rendez-vous
    return jsonify({
        "message": "Appointment and patient created successfully!",
        "appointment": {
            "id": new_appointment.id,
            "patient_id": new_appointment.patient_id,
            "doctor_id": new_appointment.doctor_id,
            "appointment_date": new_appointment.appointment_date.strftime("%Y-%m-%d"),
            "notes": new_appointment.notes,
            "is_cancelled": new_appointment.is_cancelled,
        },
        "patient": {
            "id": patient_id,
            "name": data["patient_name"],
            "address": data.get("address", ""),
            "email": data.get("email", ""),
            "phone_number": data.get("phone_number", ""),
            "gender": data.get("gender", "")
        }
    }), 201
#CODE DOUAE




# Récupérer un rendez-vous spécifique par ID
@routes.route("/appointments/<int:id>", methods=["GET"])
@swag_from({
    'responses': {
        200: {
            'description': 'Details of the appointment',
            'examples': {
                'application/json': {
                    "id": 1,
                    "patient": {
                        "id": 1,
                        "name": "John Doe",
                        "address": "123 Street",
                        "email": "john.doe@example.com",
                        "phone_number": "1234567890",
                        "gender": "male"
                    },
                    "doctor_id": 1,
                    "appointment_date": "2023-01-01 09:00:00",
                    "notes": "Follow-up appointment"
                }
            }
        },
        404: {
            'description': 'Appointment not found',
            'examples': {
                'application/json': {
                    "message": "Appointment not found"
                }
            }
        }
    },
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the appointment to retrieve'
        }
    ]
})

def get_appointment(id):
    # Récupérer le rendez-vous depuis la base de données
    appointment = Appointment.query.get(id)
    
    # Si le rendez-vous n'existe pas, renvoyer un message d'erreur
    if appointment is None:
        return jsonify({"message": "Appointment not found"}), 404

    # Utiliser l'ID du patient dans le rendez-vous pour récupérer les détails du patient via gRPC
    patient_details = get_patient_details(appointment.patient_id)
    
    # Si les détails du patient ne sont pas trouvés, renvoyer une erreur
    if patient_details is None:
        return jsonify({"message": "Patient details not found"}), 404

    # Déboguer en affichant la réponse complète (facultatif, pour vérifier la structure de `patient_details`)
    print(patient_details)

    # Formater la date de l'appoitment pour un format plus lisible
    appointment_date = appointment.appointment_date.strftime("%Y-%m-%d %H:%M:%S")

    # Retourner la réponse avec les détails du rendez-vous et du patient
    return jsonify({
        "id": appointment.id,
        "patient": {
            "id": patient_details.patient.id,  # Accéder au champ 'id' du patient
            "name": patient_details.patient.name,
            "address": patient_details.patient.address,
            "email": patient_details.patient.email,
            "phone_number": patient_details.patient.phoneNumber,  
            "gender": patient_details.patient.gender
        },
        "doctor_id": appointment.doctor_id,
        "appointment_date": appointment_date,
        "notes": appointment.notes
    })

@routes.route('/appointments/<int:appointment_id>', methods=['PUT'])
@swag_from({
    'responses': {
        200: {
            'description': 'Appointment updated successfully!',
            'examples': {
                'application/json': {
                    "message": "Appointment updated successfully!",
                    "appointment": {
                        "id": 1,
                        "patient_id": 1,
                        "doctor_id": 1,
                        "appointment_date": "2023-01-01",
                        "notes": "Updated notes",
                        "is_cancelled": False,
                    },
                    "patient": {
                        "id": 1,
                        "name": "John Doe",
                        "address": "123 Street",
                        "email": "john.doe@example.com",
                        "phone_number": "1234567890",
                        "gender": "male",
                    }
                }
            }
        },
        404: {
            'description': 'Appointment not found',
            'examples': {
                'application/json': {
                    "message": "Appointment not found"
                }
            }
        },
        500: {
            'description': 'Database error or gRPC call failed',
            'examples': {
                'application/json': {
                    "message": "Database error: <error details>",
                    "error": "gRPC call failed"
                }
            }
        }
    },
    'parameters': [
        {
            'name': 'appointment_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the appointment to update'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'doctor_id': {'type': 'integer'},
                    'patient_name': {'type': 'string'},
                    'address': {'type': 'string'},
                    'email': {'type': 'string'},
                    'phone_number': {'type': 'string'},
                    'gender': {'type': 'string'},
                    'appointment_date': {'type': 'string'},
                    'notes': {'type': 'string'},
                    'is_cancelled': {'type': 'boolean'}
                },
                'example': {
                    'doctor_id': 1,
                    'patient_name': 'John Doe',
                    'address': '123 Street',
                    'email': 'john.doe@example.com',
                    'phone_number': '1234567890',
                    'gender': 'male',
                    'appointment_date': '2023-01-01',
                    'notes': 'Follow-up appointment',
                    'is_cancelled': False
                }
            }
        }
    ]
})

def update_appointment(appointment_id):
    data = request.json

    # Try to retrieve the appointment by its ID
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return jsonify({"message": "Appointment not found"}), 404

    # Initialize patient_details with the current appointment's patient details
    patient_details = None

    # Verify if the doctor exists by calling the User Service API
    doctor_id = data.get("doctor_id", appointment.doctor_id)
    user_service_url = f"{USER_SERVICE_URL}/{doctor_id}/exists"
    try:
        response = requests.get(user_service_url)
        if response.status_code != 200:
            return jsonify({"message": "Error checking doctor existence", "error": response.json()}), response.status_code
        doctor_exists = response.json()
        if not doctor_exists:
            return jsonify({"message": "Doctor not found"}), 404
    except requests.RequestException as e:
        return jsonify({"message": f"Error communicating with User Service: {str(e)}"}), 500

    # Update patient information if provided
    patient_id = appointment.patient_id
    if "name" in data:  # Check if patient data is being updated
        # Create a gRPC patient update request
        patient_data = patient_pb2.Patient(
            name=data.get("name", appointment.patient.name),
            address=data.get("address", appointment.patient.address),
            email=data.get("email", appointment.patient.email),
            phoneNumber=data.get("phoneNumber", appointment.patient.phoneNumber),
            gender=data.get("gender", appointment.patient.gender),
        )

        grpc_response, grpc_error = update_patient(patient_data)
        if grpc_error:
            return jsonify({"error": grpc_error, "message": "gRPC call failed"}), 500

        # Update the local patient details
        patient_details = get_patient_details(patient_id)
        if patient_details:
            patient_details.patient.name = grpc_response.name
            patient_details.patient.address = grpc_response.address
            patient_details.patient.email = grpc_response.email
            patient_details.patient.phoneNumber = grpc_response.phoneNumber
            db.session.commit()
    else:
        # Use existing patient details if no update is performed
        patient_details = get_patient_details(patient_id)

    # Update the appointment details
    appointment.appointment_date = data.get("appointment_date", appointment.appointment_date)
    appointment.notes = data.get("notes", appointment.notes)
    appointment.is_cancelled = data.get("is_cancelled", appointment.is_cancelled)

    try:
        db.session.commit()
    except Exception as e:
        return jsonify({"message": f"Database error: {str(e)}"}), 500

    # Return the response with updated details
    return jsonify({
        "message": "Appointment updated successfully!",
        "appointment": {
            "id": appointment.id,
            "patient_id": patient_details.patient.id,
            "doctor_id": appointment.doctor_id,
            "appointment_date": appointment.appointment_date.strftime("%Y-%m-%d"),
            "notes": appointment.notes,
            "is_cancelled": appointment.is_cancelled,
        },
        "patient": {
            "id": patient_details.patient.id,
            "name": data.get("patient_name", patient_details.patient.name),
            "address": data.get("address", patient_details.patient.address),
            "email": data.get("email", patient_details.patient.email),
            "phone_number": data.get("phone_number", patient_details.patient.phoneNumber),
            "gender": data.get("gender", patient_details.patient.gender),
        }
    }), 200


# Supprimer un rendez-vous
@routes.route("/appointments/<int:id>", methods=["DELETE"])
@swag_from({
    'responses': {
        200: {
            'description': 'Appointment deleted',
            'examples': {
                'application/json': {
                    "message": "Appointment deleted!"
                }
            }
        },
        404: {
            'description': 'Appointment not found',
            'examples': {
                'application/json': {
                    "message": "Appointment not found"
                }
            }
        }
    },
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the appointment to delete'
        }
    ]
})
def delete_appointment(id):
    appointment = Appointment.query.get(id)
    if appointment is None:
        return jsonify({"message": "Appointment not found"}), 404

    db.session.delete(appointment)
    db.session.commit()
    return jsonify({"message": "Appointment deleted!"})



# Récupérer tous les rendez-vous d'un médecin spécifique par son ID
@routes.route("/appointments/medecin/<int:doctor_id>", methods=["GET"])
@swag_from({
    'responses': {
        200: {
            'description': 'List of appointments for a specific doctor',
            'examples': {
                'application/json': [
                    {
                        "id": 1,
                        "patient": {
                            "id": 1,
                            "name": "John Doe",
                            "address": "123 Street",
                            "email": "john.doe@example.com",
                            "phone_number": "1234567890",
                            "gender": "male"
                        },
                        "doctor_id": 1,
                        "appointment_date": "2023-01-01",
                        "notes": "Follow-up appointment"
                    }
                ]
            }
        },
        404: {
            'description': 'No appointments found for this doctor',
            'examples': {
                'application/json': {
                    "message": "No appointments found for this doctor"
                }
            }
        }
    },
    'parameters': [
        {
            'name': 'doctor_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the doctor'
        }
    ]
})
def get_appointments_by_doctor(doctor_id):
    appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
    if not appointments:
        return jsonify({"message": "No appointments found for this doctor"}), 404

    appointments_list = []
    for a in appointments:
        patient_details = get_patient_details(a.patient_id)
        if patient_details is None:
            continue  # Si le patient n'est pas trouvé, on passe à l'élément suivant
        
        appointments_list.append({
            "id": a.id,
            "patient": {
                "id": patient_details.patient.id,
                "name": patient_details.patient.name,
                "address": patient_details.patient.address,
                "email": patient_details.patient.email,
                "phone_number": patient_details.patient.phoneNumber,  # Attention à la casse : 'phoneNumber'
                "gender": patient_details.patient.gender
            },
            "doctor_id": a.doctor_id,
            "appointment_date": a.appointment_date.strftime("%Y-%m-%d"),
            "notes": a.notes
        })
    
    return jsonify(appointments_list)

# Supprimer un rendez-vous selon la date
@routes.route("/appointments/delete_by_date", methods=["DELETE"])
@swag_from({
    'responses': {
        200: {
            'description': 'Appointments deleted',
            'examples': {
                'application/json': {
                    "message": "N appointments deleted successfully."
                }
            }
        },
        400: {
            'description': 'Invalid date format or date not provided',
            'examples': {
                'application/json': {
                    "message": "Invalid date format. Please use 'YYYY-MM-DD'."
                }
            }
        },
        404: {
            'description': 'No appointments found for the specified date',
            'examples': {
                'application/json': {
                    "message": "No appointments found for the specified date."
                }
            }
        }
    },
    'parameters': [
        {
            'name': 'date',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Date of the appointments to delete (format: YYYY-MM-DD)'
        }
    ]
})
def delete_appointment_by_date():
    # Récupérer la date du rendez-vous à supprimer depuis les paramètres de la requête
    appointment_date_str = request.args.get('date')  # La date doit être passée en tant que paramètre de requête (format : "YYYY-MM-DD")
    
    if not appointment_date_str:
        return jsonify({"message": "Date is required"}), 400
    
    try:
        # Convertir la chaîne de date en objet datetime
        appointment_date = datetime.strptime(appointment_date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"message": "Invalid date format. Please use 'YYYY-MM-DD'."}), 400
    
    # Trouver les rendez-vous ayant cette date
    appointments_to_delete = Appointment.query.filter(Appointment.appointment_date == appointment_date).all()
    
    if not appointments_to_delete:
        return jsonify({"message": "No appointments found for the specified date."}), 404
    
    # Supprimer tous les rendez-vous trouvés
    for appointment in appointments_to_delete:
        db.session.delete(appointment)
    
    db.session.commit()  # Confirmer les suppressions

    return jsonify({"message": f"{len(appointments_to_delete)} appointments deleted successfully."}), 200


"""
Cette méthode permet de récupérer tous les rendez-vous associés à un patient spécifique, identifié par son ID. 
"""
@routes.route("/appointments/patient/<int:patient_id>", methods=["GET"])
@swag_from({
    'responses': {
        200: {
            'description': 'List of appointments for a specific patient',
            'examples': {
                'application/json': [
                    {
                        "id": 1,
                        "doctor_id": 1,
                        "start_time": "2023-01-01 09:00:00",
                        "end_time": "2023-01-01 10:00:00",
                        "notes": "Annual checkup",
                        "status": "scheduled",
                        "patient_id": 1
                    }
                ]
            }
        },
        404: {
            'description': 'No appointments found for this patient',
            'examples': {
                'application/json': {
                    "message": "No appointments found for this patient"
                }
            }
        }
    },
    'parameters': [
        {
            'name': 'patient_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the patient'
        }
    ]
})
def get_appointments_by_patient(patient_id):
    appointments = Appointment.query.filter_by(patient_id=patient_id).all()
    if not appointments:
        return jsonify({"message": "No appointments found for this patient"}), 404

    appointments_list = []
    for a in appointments:
        # Vérifier si le médecin existe en appelant l'API du service utilisateur
        doctor_id = a.doctor_id
        user_service_url = f"{USER_SERVICE_URL}/{doctor_id}/exists"
        try:
            response = requests.get(user_service_url)
            if response.status_code != 200:
                return jsonify({"message": "Error checking doctor existence", "error": response.json()}), response.status_code
            doctor_exists = response.json()
            if not doctor_exists:
                continue  # Si le médecin n'existe pas, on passe à l'élément suivant
        except requests.RequestException as e:
            return jsonify({"message": f"Error communicating with User Service: {str(e)}"}), 500
        
        # Formater la date de début et de fin du rendez-vous pour un format lisible
        start_time = a.start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_time = a.end_time.strftime("%Y-%m-%d %H:%M:%S")

        appointments_list.append({
            "id": a.id,
            "doctor_id": doctor_id,
            "start_time": start_time,
            "end_time": end_time,
            "notes": a.notes,
            "status": a.status,  # Inclure le statut du rendez-vous
            "patient_id": a.patient_id
        })
    
    return jsonify(appointments_list)