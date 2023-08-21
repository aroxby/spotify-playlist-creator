from datetime import datetime
import os
from uuid import uuid4

from flask import Flask, redirect, request

from spotify import (
    add_tracks_to_playlist, build_oauth_url, get_user_profile,
    create_playlist, get_access_token, get_tracks,
)

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
    scope = 'user-read-private user-read-email user-library-read playlist-modify-private playlist-modify-public'

    url = build_oauth_url(state, scope, client_id, redirect_uri)
    print('Redirecting to Spotify...')
    return redirect(url)


@app.route('/callback')
def callback():
    auth_code = request.args['code']
    # state = request.args['state']

    print('Authenticating with Spotify...')
    token = get_access_token(auth_code, client_id, client_secret, redirect_uri)

    print('Getting user profile...')
    user = get_user_profile(token)

    print('Loading tracks...')
    tracks = get_tracks(token)

    print('Creating new playlist...')
    playlist_name = 'SPC (' + str(datetime.now()) + ')'
    playlist_description = 'Created automagically on ' + str(datetime.now())
    playlist = create_playlist(playlist_name, playlist_description, user, token)

    print('Adding tracks to playlist...')
    add_tracks_to_playlist(tracks, playlist, token)

    print('Done!')

    data = playlist['external_urls']
    return data
