from geopy.geocoders import Nominatim



geolocator = Nominatim(user_agent="app")

location_ = 'Минск'
location = geolocator.geocode(location_, language="ru")

print(location)