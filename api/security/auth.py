# Authentification (token JWT, OAuth2, etc.)

import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from api.security.users import fake_users_db
#from users import fake_users_db

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

# Clé secrète utilisée pour signer les tokens JWT
SECRET_KEY = os.getenv("SECRET_KEY")

# Algorithme utilisé pour signer les tokens
ALGORITHM = "HS256"

# Durée de validité des tokens (en minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 1000

# Crée un schéma OAuth2 pour extraire le token Bearer des requêtes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Vérifie si un utilisateur existe et si le mot de passe est correct
def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or user["password"] != password:
        return False
    return user

# Crée un token JWT contenant des données (ex : username)
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    # Définit la date d’expiration du token
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    # Encode et signe le token avec la clé secrète
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Décode le token JWT fourni et vérifie s'il est valide
# 1. Lit le token envoyé dans l’en-tête HTTP
# 2. Décode le token 
# 3. Récupère le sub (subject) qui contient le nom d’utilisateur
# 4. Retourne un dictionnaire utilisateur minimal
async def get_current_user(token: str = Depends(oauth2_scheme)):   
    credentials_exception = HTTPException (
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou manquant",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Décode le token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        # Vérifie que l'utilisateur existe bien
        if username is None:
            raise credentials_exception
        return {"username": username}
    except JWTError:
        raise credentials_exception


# 🎯 Partie interactive
if __name__ == "__main__":
    print("=== AUTHENTIFICATION UTILISATEUR ===")

    username = input("🧑 Entrez votre nom d'utilisateur : ").strip().lower()
    password = input("🔒 Entrez votre mot de passe : ").strip()

    user = authenticate_user(username, password)

    if not user:
        print("\n❌ Échec de l'authentification. Nom d'utilisateur ou mot de passe incorrect.")
    else:
        print(f"\n✅ Bienvenue {user['username']} !")

        token = create_access_token(data={"sub": user["username"]})
        print(f"\n🎫 Voici votre token d'accès (JWT) :\n{token}\n")

        # Décodage pour afficher les infos contenues dans le token
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"📦 Payload décodé :\n{decoded}")