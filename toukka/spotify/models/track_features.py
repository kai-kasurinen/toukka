#

class TrackFeaturesDelivered():
    
    def __init__(self, features):
        self.features=features
    
    def get_features_with_delivered(self):

        features=self.features

        # https://github.com/plamere/OrganizeYourMusic/blob/master/web/index.html#L1634
        features['sadness'] = (1 - features['energy']) * (1 - features['valence'])
        features['happiness'] = features['energy'] * features['valence']
        features['anger'] = features['energy'] * (1 - features['valence'])

        # https://towardsdatascience.com/is-my-spotify-music-boring-an-analysis-involving-music-data-and-machine-learning-47550ae931de
        features['boringness'] = features['loudness'] + features['tempo'] + (features['energy'] * 100) + (features['danceability'] * 100)

        return features

    # FIXME: dup
    def _feat_filter(self, param, low, high):
        features = self.get_features_with_delivered()

        param_feature = features.get(param)
        if (param_feature >= low and param_feature <= high):
            return True
        else:
            return False


    def _feat_music_filter(self, param, low, high):

        features = self.get_features_with_delivered()

        speechiness = features.get('speechiness')
        param_feature = features.get(param)
        if (speechiness < .8 and param_feature >= low and param_feature <= high):
            return True
        else:
            return False

    def _feat_music_moods(self):

        moods = []
        # https://github.com/plamere/OrganizeYourMusic/blob/master/web/index.html#L370
        if self._feat_music_filter('energy', 0, 0.2):
            moods.append('chill')
        if self._feat_music_filter('energy', 0.8, 1.0):
            moods.append('energetic')
        if self._feat_music_filter('sadness', 0.8, 1.0):
            moods.append('sad')
        if self._feat_music_filter('anger', 0.8, 1.0):
            moods.append('anger')
        if self._feat_music_filter('happiness', 0.8, 1.0):
            moods.append('happy')
        if self._feat_music_filter('danceability', 0.8, 1.0):
            moods.append('danceable')
        # FIXME:words? values?
        if self._feat_music_filter('boringness', 0, 150):
            moods.append('boring')
        if self._feat_music_filter('boringness', 300, 1000):
            moods.append('hyper')
        return moods

    def _feat_music_styles(self):
        
        styles = []
        # https://github.com/plamere/OrganizeYourMusic/blob/master/web/index.html#L396
        if self._feat_music_filter('instrumentalness', 0.8, 1.0):
            styles.append('instrumental')
        if self._feat_music_filter('acousticness', 0.8, 1.0):
            styles.append('acoustic')
        if self._feat_music_filter('liveness', 0.85, 1.0):
            styles.append('live')
        if self._feat_filter('speechiness', 0.85, 1.0):
            styles.append('spoken word')
        if self._feat_music_filter('loudness', -5, 0):
            styles.append('loud')
        if self._feat_music_filter('loudness', -60, -10):
            styles.append('quiet')
        return styles

    def _feat_music_key_to_string(self):

        # https://github.com/poiley/spotify-info/blob/master/functions.py#L115
        keys_in_number_format = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
        number_format_to_keys = {v: k for k, v in keys_in_number_format.items()}

        key = number_format_to_keys.get(self.features.get('key'))
        return key

    def _feat_music_mode_to_string(self):

        if self.features.get('mode'):
            return 'major'
        else:
            return 'minor'








