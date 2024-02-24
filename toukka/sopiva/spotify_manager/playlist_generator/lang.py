#

import logging

import langdetect
from langdetect.lang_detect_exception import LangDetectException

import ftlangdetect

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


def lang_detect(text):
    return lang_detect_1(text)


def lang_detect_1(text):
    res = ftlangdetect.detect(text=text)
    logger.debug('%s (%s, %s)', text, res['lang'], res['score'])
    return res['lang']


def lang_detect_0(text):
    try:
        lang = langdetect.detect(text)
    except LangDetectException:
        lang = None
    return lang
