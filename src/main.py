from fastapi import FastAPI
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/get_calenderweek_dates/{cw}/{year}")
def read_cwd(cw: int, year: int):
    date_string = str(year) + " " + str(cw) + " 0"
    date = datetime.strptime(date_string, "%Y %W %w")
    start = date - timedelta(days=70)
    end = date + timedelta(days=70)
    return {"start": start, "end": end}

@app.get("/calculate_lat_lon/{address}")
def calculate_lat_lon(address: str):
    locator = Nominatim(user_agent="GetLoc")
    location = locator.geocode(address)
    return {"lat": location.latitude, "lon": location.longitude, "adress": address}
