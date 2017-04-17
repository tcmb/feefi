#!/usr/bin/env python

from math import cos, asin, sqrt
from units import unit
from constants import P, HOME_LOC

km = unit('km')

def distance(lat1, lon1, lat2, lon2):
    a = 0.5 - cos((lat2 - lat1) * P)/2 + cos(lat1 * P) * cos(lat2 * P) * (1 - cos((lon2 - lon1) * P)) / 2
    return 12742 * asin(sqrt(a))

def start_distance_from_home(activity):
    return distance(HOME_LOC.lat, HOME_LOC.lon, activity.start_latlng.lat, activity.start_latlng.lon)

def end_distance_from_home(activity):
    return distance(HOME_LOC.lat, HOME_LOC.lon, activity.end_latlng.lat, activity.end_latlng.lon)

def is_close_to_home(activity):
    return km(start_distance_from_home(activity)) <= km(10) or km(end_distance_from_home(activity)) <= km(10)

def matches_criteria(activity):
    return activity.type == "Ride" and km(activity.distance) > km(100) and is_close_to_home(activity)

def get_min_dist(activity):
    return min(start_distance_from_home(activity), end_distance_from_home(activity))
