from flask import Flask, redirect, request, render_template
from constants import *
from secrets import *
from urllib import urlencode
from urlparse import urljoin
import requests
import json

from stravalib.client import Client
from helpers import matches_criteria, get_min_dist, get_activity_url, km, Match


app = Flask(__name__)
my_host = LOCALHOST
#my_host = REMOTEHOST

my_app_params = {
    'client_id': CLIENT_ID,
    'redirect_uri': urljoin(my_host, '/'),
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
        "home_loc_lat": request.form['home_loc_lat'],
        "home_loc_lon": request.form['home_loc_lon'],
        "max_dist_from_home": request.form['max_dist_from_home'],
        "min_ride_length": request.form['min_ride_length'],
        "max_ride_length": request.form['max_ride_length'],
        "max_results": request.form['max_results'],
    }


def get_matching_activities(user_token, params):

    client = Client(user_token)
    matches = list()
    i = 0

    print "Getting friend activities"
    # limited to last 200 total activities as per http://strava.github.io/api/v3/activities/#get-feed
    friend_activities_iterator = client.get_friend_activities()

    while len(matches) < 10:
        i = i + 1
        try:
            activity = friend_activities_iterator.next()
            # print "Considering activity %s" % activity.id
            if matches_criteria(activity):
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
            id=m.id, name=m.name, url=get_activity_url(m), length=km(m.distance), dist_from_home=km(get_min_dist(m))
        ) for m in matches
    ]


@app.route('/')
def index():
    """
    For authorized users, display page for parameter selection
    For non-authorized users, redirect to Strava app authorization page
    """
    authorization_code = request.args.get('code')
    if authorization_code:
        return render_template('index.html', auth_code=authorization_code)
    else:
        return redirect(authorization_url)


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
        return render_template('matches.html', matches=matches)
    else:
        #return 400
        pass
