# import requests
# import os
# from fastapi import HTTPException

# AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
# AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")
# BASE_URL = "https://test.api.amadeus.com"

# async def get_access_token():
#     """
#     Retrieve an access token from Amadeus API.
#     """
#     url = f"{BASE_URL}/v1/security/oauth2/token"
#     payload = {
#         "grant_type": "client_credentials",
#         "client_id": AMADEUS_API_KEY,
#         "client_secret": AMADEUS_API_SECRET,
#     }
#     headers = {"Content-Type": "application/x-www-form-urlencoded"}

#     try:
#         response = requests.post(url, data=payload, headers=headers)
#         response.raise_for_status()
#         return response.json()["access_token"]
#     except requests.exceptions.RequestException as e:
#         raise HTTPException(status_code=500, detail=f"Error obtaining access token: {str(e)}")

# async def fetch_hotels(city_code: str):
#     """
#     Fetch hotel offers from Amadeus API for a given city code.
#     """
#     token = await get_access_token()
#     url = f"{BASE_URL}/v2/shopping/hotel-offers"
#     headers = {"Authorization": f"Bearer {token}"}
#     params = {"cityCode": city_code, "adults": 1, "radius": 10, "radiusUnit": "KM"}

#     try:
#         response = requests.get(url, headers=headers, params=params)
#         response.raise_for_status()
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching hotels: {str(e)}")
