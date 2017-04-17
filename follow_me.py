from flask import Flask, redirect, request, render_template
from constants import STRAVA_OAUTH_URL, LOCALHOST
from secrets import *
from urllib import urlencode

app = Flask(__name__)

my_app_params = {
    'client_id': CLIENT_ID,
    'redirect_uri': LOCALHOST,
    'response_type': 'code',
    'approval_prompt': 'auto',
    'scope': 'public'
}

@app.route('/')
def authoriziation_redirect():
    # print 'Method: %s\nForm: %s\nArgs: %s\nEOM' % (
    #     request.method, request.form, request.args
    # )
    authorization_code = request.args.get('code')
    if authorization_code:
        return render_template('index.html', authorization_code=authorization_code)
    else:
        redirect_url = STRAVA_OAUTH_URL + '?' + urlencode(my_app_params)
        return redirect(redirect_url)
