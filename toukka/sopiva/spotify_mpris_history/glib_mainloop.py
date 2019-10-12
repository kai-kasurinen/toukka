#

import logging

from gi.repository import GLib

logger = logging.getLogger(__name__)


class MainLoop:
    def __init__(self):
        self.mainloop = GLib.MainLoop()

    def run(self):
        logger.debug('mainloop run')
        try:
            self.mainloop.run()
        except KeyboardInterrupt:
            logger.info('Ctrl+C hit, quitting')
            self.exit()

    def exit(self):
        logger.debug('mainloop quit')
        self.mainloop.quit()

# END
