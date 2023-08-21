from urllib.parse import quote_plus

import requests


def build_oauth_url(state, scope, client_id, redirect_uri):
    # TODO: Use URL builder
    url = 'https://accounts.spotify.com/authorize'
    url += '?response_type=code'
    url += '&client_id=' + quote_plus(client_id)
    url += '&scope=' + quote_plus(scope)
    url += '&redirect_uri=' + quote_plus(redirect_uri)
    url += '&state=' + quote_plus(state)
    return url


def get_user_profile(token):
    url = 'https://api.spotify.com/v1/me'
    headers = {'authorization': f'Bearer {token}'}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data


def get_access_token(auth_code, client_id, client_secret, redirect_uri):
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
    response.raise_for_status()

    return response.json()['access_token']


def get_tracks(token):
    url = 'https://api.spotify.com/v1/me/tracks'
    headers = {'authorization': f'Bearer {token}'}

    items = []
    offset = 0
    page_size = 50
    while url:
        params = {
            'limit': page_size,
            'offset': offset,
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        items += data.get('items', [])
        offset += page_size
        url = data.get('next', None)

    return items


def create_playlist(name, description, user, token):
    url = f'https://api.spotify.com/v1/users/{user["id"]}/playlists'
    headers = {'authorization': f'Bearer {token}'}

    params = {
        'name': name,
        'description': description,
        'public': False,
    }
    response = requests.post(url, headers=headers, json=params)
    response.raise_for_status()
    data = response.json()

    # FIXME: Even after this call the playlist is still public?!
    make_playlist_private(data, token)

    return data


def make_playlist_private(playlist, token):
    url = f'https://api.spotify.com/v1/playlists/{playlist["id"]}'
    headers = {'authorization': f'Bearer {token}'}

    params = {
        'public': False,
    }
    response = requests.put(url, headers=headers, json=params)
    response.raise_for_status()


def add_tracks_to_playlist(tracks, playlist, token):
    url = f'https://api.spotify.com/v1/playlists/{playlist["id"]}/tracks'
    headers = {'authorization': f'Bearer {token}'}

    page_size = 100
    while tracks:
        params = {
            'uris': [track['track']['uri'] for track in tracks[:page_size]]
        }
        response = requests.post(url, headers=headers, json=params)
        response.raise_for_status()
        tracks = tracks[page_size:]
