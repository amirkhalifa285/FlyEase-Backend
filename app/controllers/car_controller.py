# import requests
# import os
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from ..models.car import Car
# from datetime import datetime
# from ..auth.amadeus_auth import get_amadeus_access_token


# async def fetch_and_save_cars(db: AsyncSession, start_location: dict, end_location: dict, date_time: str, passengers: list):
#     """
#     Fetch cars using the Amadeus Transfer Search API and save them to the database.
#     """
#     try:
#         # Get the access token
#         access_token = await get_amadeus_access_token()

#         # Prepare the API request
#         headers = {
#             "Authorization": f"Bearer {access_token}",
#             "Content-Type": "application/json",
#         }
#         payload = {
#             "start": {
#                 "pickup": {"location": start_location},
#                 "dateTime": date_time,
#             },
#             "end": {
#                 "dropOff": {"location": end_location},
#             },
#             "passengers": passengers,
#         }

#         # Fetch cars from Amadeus API
#         response = requests.post("test.api.amadeus.com/v1/shopping/transfer-offers", json=payload, headers=headers)
#         if response.status_code != 200:
#             raise Exception(f"Failed to fetch cars: {response.text}")

#         data = response.json()
#         transfer_offers = data.get("data", [])

#         # Save cars to the database
#         for offer in transfer_offers:
#             existing_car = await db.execute(select(Car).where(Car.offer_id == offer["id"]))
#             if existing_car.scalar():
#                 continue

#             start_loc = offer.get("start", {}).get("pickup", {}).get("location", {})
#             end_loc = offer.get("end", {}).get("dropOff", {}).get("location", {})
#             new_car = Car(
#                 offer_id=offer["id"],
#                 name=offer["vehicle"]["name"],
#                 vehicle_type=offer["vehicle"]["type"],
#                 location=start_loc.get("latitude", "") + ", " + start_loc.get("longitude", ""),
#                 price=float(offer["price"]["amount"]),
#                 currency=offer["price"]["currency"],
#                 start_location=start_loc,
#                 end_location=end_loc,
#                 start_time=datetime.fromisoformat(offer.get("start", {}).get("dateTime", "")),
#                 end_time=datetime.fromisoformat(offer.get("end", {}).get("dateTime", "")),
#                 passengers=passengers,
#                 providers=offer.get("provider", {}),
#             )
#             db.add(new_car)

#         await db.commit()
#     except Exception as e:
#         raise Exception(f"Error fetching or saving cars: {str(e)}")