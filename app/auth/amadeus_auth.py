import requests
import os
import time

AMADEUS_TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
_access_token = None
_token_expiry = 0


def get_amadeus_access_token():
    """
    Manage and return a valid Amadeus access token.
    Fetch a new token if expired or not available.
    """
    global _access_token, _token_expiry

    current_time = time.time()

    # Check if token exists and is still valid
    if _access_token and current_time < _token_expiry:
        return _access_token

    # Fetch a new token
    payload = {
        "grant_type": "client_credentials",
        "client_id": os.getenv("AMADEUS_CLIENT_ID"),
        "client_secret": os.getenv("AMADEUS_CLIENT_SECRET"),
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(AMADEUS_TOKEN_URL, data=payload, headers=headers)
    if response.status_code != 200:
        print("Token Fetch Error:", response.text)
        raise Exception(f"Failed to fetch access token: {response.text}")

    token_data = response.json()
    _access_token = token_data["access_token"]
    _token_expiry = current_time + token_data["expires_in"]

    print(f"New Token Fetched: {_access_token}")  # Debugging
    return _access_token
