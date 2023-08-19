import os
from urllib.parse import quote_plus
from uuid import uuid4

from flask import Flask, redirect, request
import requests


client_id = os.environ['SPOTIFY_CLIENT_ID']
client_secret = os.environ['SPOTIFY_CLIENT_SECRET']
redirect_uri = 'http://localhost:5000/callback'

app = Flask(__name__)


@app.route('/')
def index():
    # I got tired of typing out /init
    # return '', 403
    return redirect('http://localhost:5000/init')


@app.route('/init')
def flow_init():
    state = str(uuid4())  # FIXME: Sign something here so we can verify it computationally
    scope = 'user-library-read'

    # TODO: Use URL builder
    url = 'https://accounts.spotify.com/authorize'
    url += '?response_type=code'
    url += '&client_id=' + quote_plus(client_id)
    url += '&scope=' + quote_plus(scope)
    url += '&redirect_uri=' + quote_plus(redirect_uri)
    url += '&state=' + quote_plus(state)

    print(f'Redirecting to {url}')
    return redirect(url)


@app.route('/callback')
def callback():
    auth_code = request.args['code']
    # state = request.args['state']

    token = get_access_token(auth_code)

    profile_url = 'https://api.spotify.com/v1/me/tracks'
    headers = {'authorization': f'Bearer {token}'}
    response = requests.get(profile_url, headers=headers, params={'limit': 50})
    try:
        return response.json()
    except:
        raise ValueError(dump_response(response))


def dump_response(response):
    data = {
        'status': str(response.status_code),
        'body': str(response.content),
    }
    return data


def get_access_token(auth_code):
    url = 'https://accounts.spotify.com/api/token'
    auth = (client_id, client_secret)
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
    }
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri,
    }

    response = requests.post(url, auth=auth, headers=headers, data=data)
    try:
        return response.json()['access_token']
    except:
        raise ValueError(dump_response(response))
