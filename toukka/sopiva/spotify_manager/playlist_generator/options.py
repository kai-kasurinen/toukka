#
# https://options.readthedocs.io/en/latest/
# https://github.com/jonathaneunice/options

from options import Options


class PlaylistGeneratorOptions:

    def __init__(self, **kwargs):

        # NOTE: pydoc fails when defined on class property

        self.options = Options(
            dry_run=False,
            progress_bar=False,
            looper_target_count=300,
            looper_max_tries=100000,
            looper_force=False,
            expand_track_to_album=False,
            expand_track_to_artists=False,
            expand_track_to_recommendations=False,
            expand_artist_to_albums=False,
            expand_artist_to_random_album=False,
            expand_artist_to_top_tracks=False,
            expand_artist_to_related_artists=False,
            expand_artist_to_recommendations=False,
            expand_album_to_tracks=False,
            expand_album_to_artists=False,
            expand_album_to_recommendations=False,
            expand_playlist_to_items=False,
            expand_show_to_episodes=False,
            expand_genre_to_playlists=False,
            expand_genre_to_artists=False,
            expand_genre_to_related_genres=False,
            ignore_various_artists_albums=False,
            various_artists_uri='spotify:artist:0LyfQWJT6nXafLPZqxe9Of',
            ignore_non_instrumental_albums=False,
            ignore_played_albums=False,
            ignore=[],
            include_album_groups=['album', 'single', 'compilation'],
            include_genre_playlists=['intro',
                                     'sound',
                                     'female',
                                     # NOTE: year lists are stupid!
                                     # 'year_2018',
                                     # 'year_2019',
                                     # 'year_2020',
                                     'pulse',
                                     'edge'],
            sort_artist_albums_by_keys=['album_group', 'release_date'],
            sort_artist_albums_reverse=False,
            sort_show_episodes_by_keys=['release_date'],
            sort_show_episodes_reverse=False,
            randomize_artists=False,
            randomize_albums=False,
            randomize_tracks=False,
            randomize_playlist_items=False,
            randomize_genres=False,
            randomize_uris=False,
            randomize_search=False,
            randomize_recommendations=False,
            played_count_min=0
        )

        self.options = self.options.push(kwargs)

    # TODO: add read and write methods

    def update_options_from_file(self, filename):
        new_options = Options.read(filename)
        self.options.update(new_options)


# END
