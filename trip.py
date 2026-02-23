import json,re
from datetime import datetime
from pydantic import BaseModel
from typing import Dict,List,Any

def load_file(file):
    with open(file,"rb") as f:
        data=json.loads(f.read().decode())
        return data

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

def parser(d):
    result={}
    if isinstance(d,dict):
        base=d.get("hotelDetailResponse").get("hotelBaseInfo")
        position=d.get("hotelDetailResponse").get("hotelPositionInfo")
        description=d.get("hotelDetailResponse").get("hotelDescriptionInfo")
        policy=d.get("hotelDetailResponse").get("hotelPolicyInfo")
        roomlist=d.get("hotelCommentResponse").get("commentStaticInfo").get("roomList")
        roommap=d.get("seoSSRData").get("seoHotelRooms").get("physicRoomMap")
        facility = d.get("hotelDetailResponse").get("hotelFacilityPopV2").get("hotelFacility")
        address=position.get("address")

        #name
        if "hotelDetailResponse" in d:
            result["Name"]=base.get("hotelNames")[0]

        #hotel id
        result["Hotel_ID"]=d.get("ssrHotelRoomListRequest").get("search").get("hotelId")

        #phone no.
        tel=description.get("tels")
        for i in tel:
            Phone= i.get("show")
            if Phone:
                digit=re.sub(r"\D","",Phone)
                result["Phone_No"]=int(digit)
        #description
        result["Description"]=description.get("description")
        #open year
        result["Open_Year"]=int(base.get("openYear"))
        #location
        result["location"]={
            "Address": address,
            "City": base.get("cityName"),
            "State": base.get("provinceName"),
            "Country": base.get("countryName"),
            "Pincode":int(re.search(r"\d{6}", address).group())
        }
        #nearby location
        nearby=[]
        nearby_name=position.get("placeInfo").get("wholePoiInfoList")
        for item in nearby_name:
            if isinstance(item,dict):
                nearby.append({
                    "distance": item.get("distance"),
                    "dist_type": item.get("distType"),
                    "Name": item.get("poiName")
                })
        result["Nearby_location"]=nearby

        #policies
        policies=[]
        for i in policy.get("checkInAndOut").get("content"):
            if i.get("title") :
                policy_dict={
                    "title":i.get("title"),
                    "description":i.get("description")
                }
            else:
                policy_dict={
                    "title":i.get("description").split(":")[0],
                    "description":i.get("description").split(":")[1]
                }
            policies.append(policy_dict)


        # breakfast_dict={}
        # breakfast_dict["title"]=policy.get("breakfast").get("title")
        # for i in policy.get("breakfast").get("content"):
        #     if i.get("title")=="Style":
        #         breakfast_dict["Style"]=i.get("description")
        #         break
        #     elif i.get("title")=="Opening hours":
        #         breakfast_dict["Opening Hours"]=i.get("description")
        #         break
        #     policies.append(breakfast_dict)
        result["Policy"] = policies

        #Facilities
        Hotel_facilities={}
        for i in facility:
            title=  i.get("title")
            items=[]
            for cat in i.get("categoryList"):
                if cat.get("title"):
                    items.append(cat.get("title"))
                for item in cat.get("list"):
                    if item.get("facilityDesc"):
                        items.append(item.get("facilityDesc"))
            Hotel_facilities[title]=items
        result["Hotel_Facilities"]=Hotel_facilities

        #Room  details
        Room=[]
        for room in roomlist:
            room_id=room.get("id")
            room_name=room.get("name")

            if not room_id:
                continue
            room_dict={
                "Room Id":room_id,
                "Name":room_name,
                "url":[],
                "facilities":[]
            }
            image_url = roommap.get(str(room_id)).get('pictureInfo')
            facility_path = roommap.get(str(room_id)).get('baseFacilityInfo')
            bedInfo = roommap.get(str(room_id), {}).get('bedInfo',{})
            facility_list = roommap.get(str(room_id)).get('newFacilityList')

            for image in image_url:
                url = image.get('url')
                if url:
                    room_dict["url"].append(url)

            for facility in facility_path:
                title = facility.get('title')
                if title:
                    room_dict['facilities'].append(title)

            bed_title = bedInfo.get('title')
            if bed_title:
                room_dict['facilities'].append(bed_title)
            for fac in facility_list:
                fac_title = fac.get('title')
                if fac_title:
                    room_dict['facilities'].append(fac_title)
            Room.append(room_dict)
        result["Room"]=Room

        #reviews
        reviews=[]
        review_rating=d.get("hotelDetailResponse",{}).get("hotelComment").get("comment")
        for review in review_rating.get("positiveDirection"):
            customer_review = {
                "Guest_Name": review.get("userInfo").get("nickName"),
                "Guest_id": review.get("id"),
                "Comment": review.get("content"),
                "Guest_Profile": review.get("userInfo").get("headPictureUrl")
            }
            reviews.append(customer_review)
        result["Reviews"]=reviews

        #ratings
        ratings=[]
        rating_path = review_rating.get("scoreDetail")
        for rating in rating_path:
            hotel_rating = {
                    "Category":rating.get("showName"),
                    "Rating":rating.get("showScore")
                }
            ratings.append(hotel_rating)
        result["Ratings"]=ratings

        #Recommendation
        recommendation= {}
        most_view = d["seoSSRData"]["seoFooterModule"]["footerItem"][0]["title"].replace(" ", "_")
        recommendation[most_view] = []
        most_view_list = d["seoSSRData"]["seoFooterModule"]["footerItem"][0]["linkItem"]
        for data in most_view_list:
            hotal_dict = {}
            hotal_dict["hotel_name"] = data["text"]
            hotal_dict["hotel_url"] = data["url"]
            recommendation[most_view].append(hotal_dict)
        result["Recommendation"]=recommendation

        return result


def dump_cleaned_file(json_data):
    with open(f"trip_hotel_cleaned.json","wb") as f:
        f.write(json.dumps(json_data, indent=4,ensure_ascii=False).encode())

def data_extracted(extracted_data):
    with open(f"trip_hotel_{datetime.now().date()}.json","wb") as f:
        f.write(json.dumps(extracted_data, indent=4,ensure_ascii=False).encode())

file_name="trip_hotel.json"
file_data=load_file(file_name)
inner_data=file_data[1]
clean_string = inner_data.replace("Jc:", "", 1)
hotel_data = json.loads(clean_string)
main_data=hotel_data[3]
dump_cleaned_file(main_data)
extracted=parser(main_data)
try:
    validated=TripHotel(**extracted)
    data_extracted(validated.model_dump())
except Exception as e:
    print("Validation error: ",e)



