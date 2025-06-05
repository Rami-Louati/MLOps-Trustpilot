# api/api.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta
from api.security.auth import authenticate_user, create_access_token, get_current_user

from fastapi import FastAPI
from api.schemas import TextInput, LabelPrediction, ScorePrediction, Token
from api.utils import load_model_and_vectorizer


# Création de l'application FastAPI
api = FastAPI(title="API de prédiction d'avis clients")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Chargement des modèles via la fonction utilitaire
label_model, label_vectorizer = load_model_and_vectorizer("random_forest")
score_model, score_vectorizer = load_model_and_vectorizer("linear_regression")


@api.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur ou mot de passe incorrect")
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@api.get("/")
def home():
    return {"message": "Bienvenue sur l'API de prédiction Trustpilot !"}

@api.post("/predict-label", response_model=LabelPrediction)
def predict_label(data: TextInput, user: dict = Depends(get_current_user)):
    text_vectorized = label_vectorizer.transform([data.text])
    prediction = label_model.predict(text_vectorized)[0]
    return LabelPrediction(label=prediction)

@api.post("/predict-score", response_model=ScorePrediction)
def predict_score(data: TextInput, user: dict = Depends(get_current_user)):
    text_vectorized = score_vectorizer.transform([data.text])
    raw_score = score_model.predict(text_vectorized)[0]
    clipped_score = max(0, min(5, raw_score))
    return ScorePrediction(score=round(clipped_score, 2))
