#

import os
import logging
import requests
import spotipy
import spotipy.util

from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache
from xdg.BaseDirectory import save_cache_path


class Spotify(spotipy.Spotify):

    def crowd_site_entity(self, entity):
        return self._get('https://api.spotify.com/crowd-site-api/v0/entity/' + entity)

    def audio_features_one(self, track):
        return self.audio_features(track)[0]

    def get_playlist_by_uri(self, uri):
        username = uri.split(':')[2]
        playlist_id = uri.split(':')[4]
        return self.user_playlist(username, playlist_id)

    def current_user_recently_played_new(self, limit=50, after=None, before=None):
        ''' Get the current user's recently played tracks
            Parameters:
                - limit - the number of entities to return
        '''
        return self._get('me/player/recently-played', limit=limit, after=after, before=before)

    def get_currently_playing_playlist(self):
        """get currently playing playlist"""

        playing = self.currently_playing()

        if not playing:
            raise ConnectionError('User not connected to Spotify ')

        context = playing.get('context')

        if not context:
            raise Exception()

        if context['type'] != 'playlist':
            raise Exception()

        return self.get_playlist_by_uri(playing['context']['uri'])

    # https://github.com/camcaswell/Spotipyhelper/blob/master/spotipyhelper.py
    def aggregate_paging_results(self, paging_obj):
        ''' Paging objects only contain a limited number of items,
            so this method aggregates all of the requested items into one list
        '''
        return_list = paging_obj['items']
        while paging_obj['next']:
            paging_obj = self.next(paging_obj)
            return_list.extend(paging_obj['items'])
        return return_list

    def get_tracks_from_playlist(self, playlist_owner=None, playlist_id=None, playlist=None):
        ''' user_playlist_tracks() returns a "paging object" which only holds 100 items at once,
            so this calls aggregate_paging_results() to get a single list of all the "playlist track objects".
            "Playlist track objects" are glorified pointers to the actual track,
            so this method resolves the pointers and returns the actual tracks.
            If you want the time the track was added or the user who added it, this method is not for you.
        '''
        if playlist:
            playlist_owner = playlist['owner']['id']
            playlist_id = playlist['id']
        elif not (playlist_owner and playlist_id):
            raise TypeError("get_tracks_from_playlist() requires a playlist, or a username and playlist id as arguments")

        try:
            query_result = self.user_playlist_tracks(playlist_owner, playlist_id)
        except spotipy.SpotifyException as error:
            print(f"Spotify threw and error while retrieving tracks from"
                  + " spotify:user:{playlist_owner}:playlist:{playlist_id}:\n{error}")
            return []

        track_objs = self.aggregate_paging_results(query_result)
        return [t['track'] for t in track_objs]

    def diff_between_playlists(self, playlist1, playlist2):
        ''' Returns a list of songs that only appear in one playlist or the other
        '''
        tracklist1 = self.get_tracks_from_playlist(playlist=playlist1)
        tracklist2 = self.get_tracks_from_playlist(playlist=playlist2)

        diff_ids = list(set([x['id'] for x in tracklist1]).symmetric_difference(set([x['id'] for x in tracklist2])))

        lookup_ref = {x['id']:x for x in tracklist1}
        lookup_ref.update({y['id']:y for y in tracklist2})

        return [lookup_ref[x] for x in diff_ids]


class SpotifyScoped:

    def __init__(self, username=None):

        scopes = [
            ## Users
            'user-read-private',
            'user-read-birthdate',
            'user-read-email',
            ## Playlists
            'playlist-modify-private',
            'playlist-read-private',
            'playlist-read-collaborative',
            'playlist-modify-public', 
            ## Follow
            'user-follow-modify',
            'user-follow-read',
            ## Playback
            'app-remote-control',
            'streaming',
            ## Spotify Connect
            'user-read-currently-playing',
            'user-modify-playback-state',
            'user-read-playback-state',
            ## Library
            'user-library-modify',
            'user-library-read',
            ## Listening history
            'user-read-recently-played',
            'user-top-read'
        ]

        scope = " ".join(scopes)

        if not username:
            username = os.getenv('SPOTIPY_USER')

        if not username:
            raise spotipy.SpotifyException(550, -1, 'no username set')

        cache_path = save_cache_path('toukka')
        cache_path_cachecontrol = save_cache_path('toukka', 'cachecontrol')
        cache_path_tokens = save_cache_path('toukka', 'tokens')
        cache_file_for_token = os.path.join(cache_path_tokens, username)

        token = spotipy.util.prompt_for_user_token(username, scope, cache_path=cache_file_for_token)

        cache = FileCache(cache_path_cachecontrol)
        session = CacheControl(requests.Session(), cache)

        self.sp = Spotify(auth=token, requests_session=session)
        self.sp.trace = False


#
