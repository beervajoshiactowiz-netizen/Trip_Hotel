from pydantic import BaseModel
from typing import List,Dict,Any

class TripHotel(BaseModel):
    Name:str
    Hotel_ID:int
    Phone_No:int
    Description:str
    Open_Year:int
    location:Dict[str,Any]
    Nearby_location:List[Dict[str,str]]
    Policy:List[Dict[str,str]]
    Hotel_Facilities:Dict[str,Any]
    Room:List[Dict[str,Any]]
    Reviews:List[Dict[str,Any]]
    Ratings:List[Dict[str,str]]
    Recommendation:Dict[str,Any]
