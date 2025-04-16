import uvicorn
import logging

from fastapi import FastAPI, Depends
from fastapi_keycloak_middleware import (
    CheckPermissions,
    AuthorizationMethod,
    KeycloakConfiguration,
    setup_keycloak_middleware,
)
from fastapi.middleware.cors import CORSMiddleware

from starlette.config import Config

config = Config(".env")

API_APP_KEYCLOAK_URL: str = config("API_APP_KEYCLOAK_URL", cast=str)
API_APP_KEYCLOAK_REALM: str = config("API_APP_KEYCLOAK_REALM", cast=str)
API_APP_KEYCLOAK_CLIENT_ID: str = config("API_APP_KEYCLOAK_CLIENT_ID", cast=str)
API_APP_KEYCLOAK_CLIENT_SECRET: str = config("API_APP_KEYCLOAK_CLIENT_SECRET", cast=str)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

keycloakConfig = KeycloakConfiguration(
    url=API_APP_KEYCLOAK_URL,
    realm=API_APP_KEYCLOAK_REALM,
    client_id=API_APP_KEYCLOAK_CLIENT_ID,
    client_secret=API_APP_KEYCLOAK_CLIENT_SECRET,
    authorization_method=AuthorizationMethod.CLAIM,
    authorization_claim="realm_access"
)


async def scope_mapper(claim_auth: dict):
    permissions = []
    try:
        permissions = claim_auth["roles"]
    except KeyError:
        logging.warning("Unknown roles")
    return permissions


setup_keycloak_middleware(
    app,
    keycloak_configuration=keycloakConfig,
    scope_mapper=scope_mapper,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/reports", dependencies=[Depends(CheckPermissions(["prothetic_user"]))])
def get_reports():
    return [
        {"title": "cheese", "price": 19.9, "quantity": 9, "availability": True},
        {"title": "cabbage", "price": 45.5, "quantity": 6, "availability": True},
        {"title": "carrots", "price": 53.7, "quantity": 12, "availability": True},
        {"title": "tomato", "price": 40, "quantity": 0, "availability": False},
        {"title": "beets", "price": 37.7, "quantity": 7, "availability": True},
        {"title": "mangoes", "price": 240.0, "quantity": 0, "availability": False},
        {"title": "onions", "price": 19.2, "quantity": 2, "availability": True},
    ]


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
