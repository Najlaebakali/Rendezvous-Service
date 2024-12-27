import sys
import os
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from flask import Flask
from flask_migrate import Migrate
from models import db
import config
import routes 
#from routes import routes
from flask_cors import CORS
from py_eureka_client import eureka_client
from flasgger import Swagger

# Charger la configuration à partir du Config Server
config_server_url = os.getenv('CONFIG_SERVER_URL', 'http://localhost:9999')
service_name = os.getenv('SERVICE_NAME', 'rendezvous-service')

# Interroger le Config Server pour récupérer la configuration du service
response = requests.get(f"{config_server_url}/{service_name}/{os.getenv('PROFILE')}")
config_data = response.json()

# Extraire les configurations depuis la source correcte
property_sources = config_data.get('propertySources', [])
if property_sources:
    source = property_sources[0]['source']
    DB_HOST = source.get('spring.datasource.url', 'localhost')
    DB_USER = source.get('spring.datasource.username', 'root')
    DB_PASSWORD = source.get('spring.datasource.password', '')
    DB_NAME = source.get('spring.datasource.dbname', 'gestion_rendezvous')
else:
    raise Exception("Unable to fetch configuration from Config Server")

# Charger la configuration dans l'application Flask
app = Flask(__name__)
Swagger(app)
CORS(app)

# Configuration de la base de données depuis le Config Server
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

eureka_server = source.get('DISCOVERY_SERVICE_URL', 'http://localhost:8761/eureka')
# Configuration de Eureka pour l'enregistrement du service
eureka_client.init(
    app_name=service_name,
    eureka_server=eureka_server,
    instance_port=5000,
    instance_host='localhost'
)

# Initialisation de la base de données et de Flask-Migrate
db.init_app(app)
migrate = Migrate(app, db)

# Enregistrement du blueprint
app.register_blueprint(routes.routes)

if __name__ == "__main__":
    app.run(debug=True)
