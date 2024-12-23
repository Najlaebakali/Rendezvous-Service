from flask_eureka import Eureka
import os

def configure_eureka(app):
    # Ensure the host has a port (if necessary)
    host_name = os.getenv("EUREKA_INSTANCE_HOSTNAME")
    port = os.getenv("EUREKA_INSTANCE_PORT")

    # If there's no port in the host_name, append it
    if ':' not in host_name:
        host_name = f"{host_name}:{port}"

    # Create an instance of Eureka
    eureka = Eureka(app,
                    name=os.getenv("SERVICE_NAME"),
                    host_name=host_name,  # Updated to use host_name with port if necessary
                    port=int(os.getenv("EUREKA_INSTANCE_PORT")))

    # Register the service with Eureka
    eureka.register_service(
        name=os.getenv("SERVICE_NAME")
    )

    # Add the default Eureka blueprint
    from flask_eureka.eureka import eureka_bp
    app.register_blueprint(eureka_bp)
