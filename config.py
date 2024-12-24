import os
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration du service Spring Cloud Config
CONFIG_SERVICE_URL = os.getenv('CONFIG_SERVICE_URL', 'http://localhost:9999')
APPLICATION_NAME = os.getenv('SERVICE_NAME', 'rendezvous-service')
PROFILE = os.getenv('PROFILE', 'default')

# Lire les configurations depuis Spring Cloud Config
config_url = f"{CONFIG_SERVICE_URL}/{APPLICATION_NAME}/{PROFILE}"
response = requests.get(config_url)
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

# Construire la chaîne de connexion complète en fonction de la présence d'un mot de passe
if DB_PASSWORD:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
else:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}@{DB_HOST}/{DB_NAME}"


"""DB_HOST = "localhost"
DB_USER = "root"  
DB_PASSWORD = "" 
DB_NAME = "gestion_rendezvous"


import os
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration du service Spring Cloud Config
CONFIG_SERVICE_URL = os.getenv('CONFIG_SERVICE_URL', 'http://localhost:9999')
APPLICATION_NAME = os.getenv('SERVICE_NAME', 'rendezvous-service')
PROFILE = os.getenv('spring.profiles.active', 'default')

# Lire les configurations depuis Spring Cloud Config
config_url = f"{CONFIG_SERVICE_URL}/{APPLICATION_NAME}/{PROFILE}"
response = requests.get(config_url)
config_data = response.json()

# Extraire les configurations depuis la source correcte
property_sources = config_data.get('propertySources', [])
if property_sources:
    source = property_sources[0]['source']
    full_url = source.get('spring.datasource.url', 'mysql://localhost:3306/gestion_rendezvous')
    DB_HOST = full_url.split('@')[-1].split('/')[0]
    DB_NAME = full_url.split('/')[-1]
    DB_USER = source.get('spring.datasource.username', 'root')
    DB_PASSWORD = source.get('spring.datasource.password', '')
else:
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = ''
    DB_NAME = 'gestion_rendezvous'

# Construire l'URL SQLAlchemy
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

"""