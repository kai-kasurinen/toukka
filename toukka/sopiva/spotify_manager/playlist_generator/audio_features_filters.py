#

import logging

import pandas

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



def is_album_instrumental(spotify, album_id):
    
    album = spotify.album(album_id)
    track_ids = [track.id for track in album.tracks.items]
    
    tracks_audio_features = spotify.tracks_audio_features(track_ids)
    tracks_audio_features_df = pandas.DataFrame(tracks_audio_features)

    instrumentalness_mean = tracks_audio_features_df['instrumentalness'].mean()

    logger.debug(f'album {album.uri} instrumentalness mean is {instrumentalness_mean}')
    
    if instrumentalness_mean > 0.5:
        return True
    else:
        return False
    

    
