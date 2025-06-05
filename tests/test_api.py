from fastapi.testclient import TestClient
from api.api import api  
from dotenv import load_dotenv
import os

# Charger les variables d'environnement depuis .env
load_dotenv()

client = TestClient(api)

USERNAME = os.getenv("API_TEST_USERNAME")
PASSWORD = os.getenv("API_TEST_PASSWORD")

def get_token():
    response = client.post(
        "/token",
        data={"username": USERNAME, "password": PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue sur l'API de prédiction Trustpilot !"}

def test_predict_label():
    token = get_token()
    response = client.post(
        "/predict-label",
        json={"text": "Service rapide"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "label" in response.json()

def test_predict_score():
    token = get_token()
    response = client.post(
        "/predict-score",
        json={"text": "Produit excellent"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "score" in response.json()
    assert 0 <= response.json()["score"] <= 5
