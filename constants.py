from stravalib.attributes import LatLon

STRAVA_AUTH_URL = 'https://www.strava.com/oauth/authorize'
STRAVA_TOKEN_URL = 'https://www.strava.com/oauth/token'
P = 0.017453292519943295
HOME_LOC = LatLon(lat=52.47, lon=13.45)
DEFAULT_FILTER_PARAMS = {
    "home_loc_lat": "52.47",
    "home_loc_lon": "13.45",
    "max_dist_from_home": "10",
    "min_ride_length": "100",
    "max_ride_length": "0",
    'max_results': "10",
}
