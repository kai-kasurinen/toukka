#

import enlighten


class ProgressBars:

    def __init__(self, **kwargs) -> None:
        self.manager = enlighten.get_manager(**kwargs)

    def progress_bar_for_tracks(self, total) -> enlighten.Counter:
        return self.manager.counter(desc='Tracks', unit='tracks', total=total, color='green')

    def progress_bar_for_loops(self, total) -> enlighten.Counter:
        return self.manager.counter(desc='Loops', unit='tracks', total=total, color='blue')

    def stop(self) -> None:
        self.manager.stop()

# END
