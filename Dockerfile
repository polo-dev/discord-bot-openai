# Utilise la dernière version de Python 3.x
FROM python:3.12-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copie le fichier requirements.txt dans le conteneur
COPY requirements.txt .

# Installer les dépendances via pip
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier tout le contenu de ton projet dans le répertoire de travail
COPY . .

# Commande par défaut pour démarrer ton bot
CMD ["python", "main.py"]
