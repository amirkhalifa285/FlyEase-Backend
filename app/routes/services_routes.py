# from fastapi import APIRouter, Depends, HTTPException
# from app.controllers.service_controller import fetch_hotels

# router = APIRouter()

# @router.get("/services/hotels")
# async def get_hotels(city_code: str):
#     """
#     Fetch hotel offers for a specific city code.
#     """
#     try:
#         return await fetch_hotels(city_code)
#     except HTTPException as e:
#         raise HTTPException(status_code=e.status_code, detail=e.detail)
