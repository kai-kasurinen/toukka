#

import os
import logging

from xdg.BaseDirectory import save_cache_path

# import langdetect
# from langdetect.lang_detect_exception import LangDetectException

os.environ['FTLANG_CACHE'] = save_cache_path('toukka', 'fasttext-langdetect')

# import ftlangdetect

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


def lang_detect(text):
    return lang_detect_1(text)

def lang_detect_1(text):
     return None

#  File "/usr/lib/python3/dist-packages/fasttext/FastText.py", line 232, in predict
#    return labels, np.array(probs, copy=False)
#                   ~~~~~~~~^^^^^^^^^^^^^^^^^^^
# ValueError: Unable to avoid copy while creating an array as requested.


# def lang_detect_1(text):
#    res = ftlangdetect.detect(text=text)
#    logger.debug('%s (%s, %s)', text, res['lang'], res['score'])
#    return res['lang']


def lang_detect_0(text):
    try:
        lang = langdetect.detect(text)
    except LangDetectException:
        lang = None
    return lang
