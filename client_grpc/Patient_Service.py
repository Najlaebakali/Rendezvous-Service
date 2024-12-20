import grpc
from client_grpc.Protos import patient_pb2, patient_pb2_grpc



# Adresse du service PatientService
PATIENT_SERVICE_HOST = 'localhost'
PATIENT_SERVICE_PORT = 5065

# Connexion au service gRPC
def get_patient_service_stub():
    channel = grpc.insecure_channel(f"{PATIENT_SERVICE_HOST}:{PATIENT_SERVICE_PORT}")
    stub = patient_pb2_grpc.PatientServiceStub(channel)
    return stub

def add_patient(patient_data):
     # Exécuter l'appel RPC
    patient_stub = get_patient_service_stub()
    try:
        response = patient_stub.AddPatient(request_patient)
        return response.success, None
    except grpc.RpcError as e:
        return False, e.details()

    