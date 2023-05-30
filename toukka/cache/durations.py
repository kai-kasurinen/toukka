#

from datetime import timedelta

HOUR = int(timedelta(hours=1).total_seconds())
DAY = int(timedelta(days=1).total_seconds())
WEEK = int(timedelta(days=7).total_seconds())
YEAR = int(timedelta(days=365).total_seconds())
HALF_YEAR = int(YEAR / 2)
MONTH = int(YEAR / 12)
