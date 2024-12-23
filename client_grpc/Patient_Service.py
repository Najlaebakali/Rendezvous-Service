import grpc
from client_grpc.Protos import patient_pb2, patient_pb2_grpc

# Adresse du service PatientService
PATIENT_SERVICE_HOST = 'localhost'
PATIENT_SERVICE_PORT = 5065

# Fonction pour établir la connexion gRPC
def get_patient_service_stub():
    channel = grpc.insecure_channel(f"{PATIENT_SERVICE_HOST}:{PATIENT_SERVICE_PORT}")
    return patient_pb2_grpc.PatientProtoStub(channel)



# Fonction pour ajouter un patient via gRPC
def add_patient(patient_data):
    # Création de la requête gRPC
    request_patient = patient_pb2.AddPatientRequest(patient=patient_data)
    patient_stub = get_patient_service_stub()
    try:
        # Exécuter l'appel RPC
        response = patient_stub.AddPatient(request_patient)
        return response, None  # Retourner l'objet de réponse complet
    except grpc.RpcError as e:
        return None, e.details()  # Retourner le détail de l'erreur




# Fonction pour obtenir les détails du patient par son ID
def get_patient_details(patient_id):
    patient_stub = get_patient_service_stub()
    try:
        # Demande gRPC pour récupérer les informations du patient
        request = patient_pb2.GetPatientByIdRequest(id=patient_id)
        response = patient_stub.GetPatientById(request)
        return response  # Cette réponse contient les détails du patient
    except grpc.RpcError as e:
        return None  # En cas d'erreur, vous pouvez gérer l'erreur ici
    



def update_patient(patient_data):
    # Création de la requête gRPC pour la mise à jour du patient
    request_patient = patient_pb2.UpdatePatientRequest(patient=patient_data)
    patient_stub = get_patient_service_stub()
    try:
        # Exécuter l'appel RPC
        response = patient_stub.UpdatePatient(request_patient)
        return response, None  # Retourner l'objet de réponse complet
    except grpc.RpcError as e:
        return None, e.details()  # Retourner le détail de l'erreur



    # Fonction pour obtenir un patient par email
def get_patient_by_email(email):
    patient_stub = get_patient_service_stub()
    try:
        # Demande gRPC pour récupérer les informations du patient par email
        request = patient_pb2.GetPatientByEmailRequest(email=email)
        response = patient_stub.GetPatientByEmail(request)
        if response.patient:
            return response.patient  # Retourner les détails du patient
        else:
            return None  # Patient non trouvé
    except grpc.RpcError as e:
        return None  # En cas d'erreur, vous pouvez gérer l'erreur ici
    

def check_patient_exists(email):
    patient_stub = get_patient_service_stub()
    try:
        request = patient_pb2.PatientEmail(email=email)
        response = patient_stub.CheckPatientExists(request)

        return response.exists
    except grpc.RpcError as e:
        return None


""" #Ce fichier gère la communication avec le service gRPC PatientService pour ajouter un patient.

#Connexion au service Patient (gRPC) :

Une fonction get_patient_service_stub() établit la connexion au service gRPC avec l'adresse et le port spécifiés.
Elle retourne un stub permettant d'interagir avec le service gRPC.
Ajout d'un patient via gRPC :

La fonction add_patient(patient_data) :
Prépare les données du patient sous la forme d'une requête gRPC (AddPatientRequest).
Envoie la requête via le stub gRPC.
Gère les réponses ou erreurs et retourne un message de succès ou une erreur.
 """