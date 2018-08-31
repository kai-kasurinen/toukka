#

import logging

import spotipy
from .spotipyhelper import subSpotify

class Spotify(spotipy.Spotify, subSpotify):

    def crowd_site_entity(self, entity):
        return self._get('https://api.spotify.com/crowd-site-api/v0/entity/' + entity)

    def crowd_site_recent_entities(self):
        # ? limit, offset
        return self._get('https://api.spotify.com/crowd-site-api/v0/recent-entities')

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

    def get_external_urls(self, uri, name):
        # FIXME: may fail
        r = self.crowd_site_entity(uri)
        if not r:
            return {}
        entity = r.get('entity')
        urls = [url.get('url') for url in entity.get('external_urls') if url.get('name') == name]
        logging.debug('found %s %s urls from %s entity', len(urls), name, uri)
        return urls



#
