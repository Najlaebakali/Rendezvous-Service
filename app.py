from flask import Flask
from flask_migrate import Migrate
from models import db
import config
import routes

app = Flask(__name__)

# Configuration de la base de données
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}/{config.DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialisation de la base de données et de Flask-Migrate
db.init_app(app)
migrate = Migrate(app, db)

# Enregistrement du blueprint
app.register_blueprint(routes.routes)

if __name__ == "__main__":
    app.run(debug=True)
