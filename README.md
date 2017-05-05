# FeeFi the Feed Filter.
Discover inspiring rides by filtering your Strava Feed by
- minimum and maximum length
- distance from home (or any other location)

## Installation for running locally
1. Create and configure a Strava application at http://labs.strava.com/developers/
2. Set the application's callback domain to 127.0.0.1:5000
3. Install requirements
```
pip install -r requirements.txt`
```
4. Create module `secrets.py` and add your app-specific paramters:
```
CLIENT_ID = 12345
CLIENT_SECRET = 'my_client_secret'
ACCESS_TOKEN = 'my_access_token'
```
5. Set main module as Flask app:
```
export FLASK_APP=feed_filter.py
```
6. Run via `flask run`
7. Go to http://127.0.0.1:5000
8. Find bug and file an issue here :)
