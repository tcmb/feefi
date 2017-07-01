#!/usr/bin/env python

from math import cos, asin, sqrt
from collections import namedtuple
from units import unit
from constants import P, HOME_LOC

km = unit('km')

Match = namedtuple('Match', ['id', 'name', 'athlete_name', 'length', 'url', 'dist_from_home'])

def distance(lat1, lon1, lat2, lon2):
    a = 0.5 - cos((lat2 - lat1) * P)/2 + cos(lat1 * P) * cos(lat2 * P) * (1 - cos((lon2 - lon1) * P)) / 2
    return 12742 * asin(sqrt(a))

def start_distance_from_home(activity):
    assert activity.start_latlng is not None
    return distance(HOME_LOC.lat, HOME_LOC.lon, activity.start_latlng.lat, activity.start_latlng.lon)

def end_distance_from_home(activity):
    assert activity.end_latlng is not None
    return distance(HOME_LOC.lat, HOME_LOC.lon, activity.end_latlng.lat, activity.end_latlng.lon)

def is_close_to_home(activity, dist_from_home):
    # some activities like trainer rides don't have GPS information. Those are not considered 'close to home'.
    if activity.start_latlng is not None and activity.end_latlng is not None:
        return km(start_distance_from_home(activity)) <= km(dist_from_home) or km(end_distance_from_home(activity)) <= km(dist_from_home)
    else:
        return False

def matches_criteria(activity, params):
    activity_does_match = activity.type == "Ride" and \
        km(activity.distance) > km(params['min_activity_length']) and \
        is_close_to_home(activity, params['max_dist_from_home'])
    # consider max_activity_length only if != 0
    if activity_does_match and params['max_activity_length'] != 0:
        return activity_does_match and km(activity.distance) < km(params['max_activity_length'])
    else:
        return activity_does_match

def get_min_dist(activity):
    return min(start_distance_from_home(activity), end_distance_from_home(activity))

def get_activity_url(activity):
    return u"https://www.strava.com/activities/%s" % activity.id

def get_athlete_name(activity):
    athlete_name = u""
    if activity.athlete:
        athlete_name = activity.athlete.firstname + ' ' + activity.athlete.lastname
    return athlete_name
