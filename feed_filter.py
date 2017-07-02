import os
import json
import requests
from urllib import urlencode
from urlparse import urljoin
from flask import Flask, redirect, request, render_template
from stravalib.client import Client
from constants import *
from helpers import matches_criteria, get_min_dist, get_activity_url, get_athlete_name, km, Match
# use local, non-version-controlled secrets file, fall back to env var usage
try:
    from secrets import CLIENT_ID, CLIENT_SECRET, BASE_URL
except ImportError:
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    BASE_URL = os.getenv('BASE_URL')


application = Flask(__name__)
app = application

my_app_params = {
    'client_id': CLIENT_ID,
    'redirect_uri': urljoin(BASE_URL, '/'),
    'response_type': 'code',
    'approval_prompt': 'auto',
    'scope': 'public'
}

authorization_url = STRAVA_AUTH_URL + '?' + urlencode(my_app_params)


def get_user_token(authorization_code):
    params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': authorization_code
    }
    user_token_response = requests.post(STRAVA_TOKEN_URL, data=params)
    returned_data = json.loads(user_token_response.text)
    user_token = returned_data.get('access_token')
    return user_token


def get_match_params(request):
    return {
        "activity_type": request.form['activity_type'],
        "home_loc_lat": request.form['home_loc_lat'],
        "home_loc_lon": request.form['home_loc_lon'],
        "max_dist_from_home": request.form['max_dist_from_home'],
        "min_activity_length": request.form['min_activity_length'],
        "max_activity_length": request.form['max_activity_length'],
        "max_results": request.form['max_results'],
    }


def validate_filter_parameters(params):
    # This one might be worth unit testing...
    # 1. ensure correct types
    try:
        params["activity_type"] = unicode(params['activity_type'])
        params["home_loc_lat"] = float(params['home_loc_lat'])
        params["home_loc_lon"] = float(params['home_loc_lon'])
        params["max_dist_from_home"] = int(params['max_dist_from_home'])
        params["min_activity_length"] = int(params['min_activity_length'])
        params["max_activity_length"] = int(params['max_activity_length'])
        params['max_results'] = int(params['max_results'])
    except ValueError, e:
        # simple error handling for now: use default params
        return DEFAULT_FILTER_PARAMS

    # 2. ensure params within sensible boundaries
    params["activity_type"] = params["activity_type"] if params["activity_type"] in [u"Ride", u"Run"] else u"Ride"
    params["home_loc_lat"] = params['home_loc_lat'] if -90 <= params['home_loc_lat'] <= 90 else DEFAULT_FILTER_PARAMS['home_loc_lat']
    params["home_loc_lon"] = params['home_loc_lon'] if -180 <= params["home_loc_lon"] <= 180 else DEFAULT_FILTER_PARAMS['home_loc_lon']
    params["max_dist_from_home"] = params['max_dist_from_home'] if 0 <= params["max_dist_from_home"] <= 100 else DEFAULT_FILTER_PARAMS['max_dist_from_home']
    # min activity length can be chosen at will, as long as it's less than max activity length (unless max_activity_length is 0)
    # worst case is that max_results will be returned, and the Strava Feed API also has a cap of 200 results.
    params["min_activity_length"] = params['min_activity_length'] if params["min_activity_length"] <= params["max_activity_length"] or params['max_activity_length'] == 0 else DEFAULT_FILTER_PARAMS['min_activity_length']
    # max activity length can be 0 for unlimited length, otherwise it needs to be larger than min activity length
    params["max_activity_length"] = params['max_activity_length'] if params["max_activity_length"] == 0 or params["max_activity_length"] >= params["min_activity_length"] else DEFAULT_FILTER_PARAMS['max_activity_length']
    # cap at Strava max results limit for the Feed API
    params['max_results'] = params['max_results'] if 1 <= params["max_results"] <= 200 else 200

    return params


def get_matching_activities(user_token, params):

    params = validate_filter_parameters(params)

    client = Client(user_token)
    matches = list()
    i = 0

    print "Getting friend activities"
    # limited to last 200 total activities as per http://strava.github.io/api/v3/activities/#get-feed
    friend_activities_iterator = client.get_friend_activities()

    while len(matches) < params['max_results']:
        i = i + 1
        try:
            activity = friend_activities_iterator.next()
            # print "Considering activity %s" % activity.id
            if matches_criteria(activity, params):
                matches.append(activity)
                print "Added %s (%i)" % (activity.id, i)
            else:
                print "Disregarding %s (%i)" % (activity.id, i)
        except StopIteration, e:
            break

    return matches


def extract_match_data(matches):
    return [
        Match(
            id=m.id,
            name=m.name,
            athlete_name=get_athlete_name(m),
            url=get_activity_url(m),
            length=km(m.distance),
            dist_from_home=km(get_min_dist(m)
            )
        ) for m in matches
    ]


@app.route('/')
def index():
    """
    For authorized users, display page for parameter selection
    For non-authorized users, show landing page with link to Strava app authorization page
    """
    authorization_code = request.args.get('code')
    if authorization_code:
        return render_template('index.html', auth_code=authorization_code)
    else:
        return render_template('authorize.html', authorization_url=authorization_url)


@app.route('/matches', methods=['POST'])
def matches():
    """
    Run activity search for authorized user according to selected params
    """
    authorization_code = request.form.get('auth_code')
    if authorization_code:
        user_token = get_user_token(authorization_code)
        params = get_match_params(request)
        matches = extract_match_data(
            get_matching_activities(user_token, params)
            )
        return render_template('matches.html', matches=matches, base_url="%s?code=%s" % (BASE_URL, authorization_code))
    else:
        #return 400
        pass
