from flask_eureka import Eureka
import os

def configure_eureka(app):
    # Créer une instance de Eureka
    eureka = Eureka(app, 
                    name=os.getenv("SERVICE_NAME"), 
                    host_name=os.getenv("EUREKA_INSTANCE_HOSTNAME"), 
                    port=int(os.getenv("EUREKA_INSTANCE_PORT")))

    # Enregistrer le service auprès de Eureka
    eureka.register_service(
        name=os.getenv("SERVICE_NAME")
    )

    # Ajouter le blueprint par défaut de Eureka
    from flask_eureka.eureka import eureka_bp
    app.register_blueprint(eureka_bp)
