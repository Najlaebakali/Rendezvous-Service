# Utiliser une image officielle de Python 3.12 slim
FROM python:3.12-slim

# Installer les dépendances nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libmariadb-dev \
    libmariadb-dev-compat \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail dans le conteneur
WORKDIR /usr/src/app

# Copier le fichier requirements.txt et installer les dépendances Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copier tous les fichiers de l'application dans le répertoire de travail
COPY . .

# Exposer le port utilisé par votre application Flask
EXPOSE 5000

# Définir la commande par défaut pour démarrer l'application
CMD ["python", "app.py"]
