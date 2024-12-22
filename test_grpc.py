import grpc
from client_grpc.Protos import patient_pb2, patient_pb2_grpc

def test_grpc():
    try:
        # Open channel
        channel = grpc.insecure_channel("localhost:5065")
        stub = patient_pb2_grpc.PatientProtoStub(channel)
        
        # Prepare request
        request = patient_pb2.AddPatientRequest(
            patient=patient_pb2.Patient(
                name="John Doe",
                address="123 Main St",
                email="johndoe@example.com",
                phoneNumber="123456789",
                gender="Male"
            )
        )
        
        # Send gRPC request
        response = stub.AddPatient(request)
        print(f"Response: {response.message}")
    except grpc.RpcError as e:
        print(f"gRPC Error: {e.code()} - {e.details()}")

if __name__ == "__main__":
    print("Starting gRPC test...")
    test_grpc()
