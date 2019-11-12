#

import enlighten


class ProgressBars:

    def __init__(self, **kwargs):
        self.manager = enlighten.get_manager(**kwargs)

    def progress_bar_for_tracks(self, total):
        return self.manager.counter(desc='Tracks', unit='tracks', total=total, color='green')

    def progress_bar_for_loops(self, total):
        return self.manager.counter(desc='Loops', unit='tracks', total=total, color='blue')

    def stop(self):
        self.manager.stop()

# END
