import sys
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from flask import Flask
from flask_migrate import Migrate
from models import db
import config
import routes
from flask_cors import CORS
from eureka_config import configure_eureka
from flasgger import Swagger, swag_from

app = Flask(__name__)
Swagger(app)
CORS(app)  # This enables CORS for all routes

# Configuration de la base de données
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}/{config.DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialisation de la base de données et de Flask-Migrate
db.init_app(app)
migrate = Migrate(app, db)

# Enregistrement du blueprint
app.register_blueprint(routes.routes)

# Configuration de Eureka
configure_eureka(app)

if __name__ == "__main__":
    app.run(debug=True)
