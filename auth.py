import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FIREBASE_API_KEY")


def _firebase_request(url: str, payload: dict):
    response = requests.post(url, json=payload, timeout=15)
    data = response.json()

    if response.status_code != 200:
        message = data.get("error", {}).get("message", "Authentication failed")
        raise ValueError(message)

    return data


def sign_up(email: str, password: str):
    if not API_KEY:
        raise ValueError("FIREBASE_API_KEY is not set")

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    }
    return _firebase_request(url, payload)


def sign_in(email: str, password: str):
    if not API_KEY:
        raise ValueError("FIREBASE_API_KEY is not set")

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    }
    return _firebase_request(url, payload)
