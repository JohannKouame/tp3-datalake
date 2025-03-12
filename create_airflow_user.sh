#!/bin/bash

# Attendre que le conteneur soit prêt avant d'exécuter la commande
echo "Attente de l'initialisation d'Airflow..."
sleep 20

# Créer l'utilisateur dans Airflow
docker-compose exec airflow-webserver airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
