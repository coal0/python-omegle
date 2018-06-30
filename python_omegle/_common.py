import random
import string

import requests

from python_omegle.exceptions import PythonOmegleException

_SERVER_POOL = tuple("https://front{}.omegle.com".format(n) for n in range(1, 33))

_START_URL = "/start?caps=recaptcha2&rcs=1&\
firstevents=1&randid={}&lang={}"                    # GET randid, lang
_START_INTERESTS_URL = _START_URL + "&topics={}"    # GET randid, lang, topics
_START_SPY_URL = _START_URL + "&wantsspy=1"         # GET randid, lang
_SEND_URL = "/send"                                 # POST id, msg
_DISCONNECT_URL = "/disconnect"                     # POST id
_TYPING_URL = "/typing"                             # POST id
_STOPPED_TYPING_URL = "/stoppedtyping"              # POST id
_EVENTS_URL = "/events"                             # POST id

_RANDOM_ID_POOL = string.ascii_uppercase + string.digits

# Language codes according to ISO 639-1 (+ ISO 639-2).
# Only languages supported by the Google Translate widget are included
# here.
_LANGUAGE_CODES = (
    "en",
    "af",
    "sq",
    "am",
    "ar",
    "hy",
    "az",
    "eu",
    "be",
    "bn",
    "bs",
    "bg",
    "ca",
    "ceb",  # Cebuano, ISO 639-2
    "ny",
    "zh",   # Simply listed as 'Chinese'
    "co",
    "hr",
    "cs",
    "da",
    "nl",
    "eo",
    "et",
    "fil",   # Filipino, ISO 639-2
    "fi",
    "fr",
    # Frisian not implemented, ambiguous
    "gl",
    "ka",
    "de",
    "el",
    "gu",
    "ht",
    "ha",
    "he",
    "hi",
    # Hmong not implemented, ambiguous
    "hu",
    "is",
    "ig",
    "id",
    "ga",
    "it",
    "ja",
    "jv",
    "kn",
    "kk",
    "km",
    "ko",
    "ku",
    "ky",
    "lo",
    "la",
    "lv",
    "lt",
    "lb",
    "mk",
    "mg",
    "ms",
    "ml",
    "mt",
    "mi",
    "mr",
    "mn",
    "my",
    "ne",
    "no",
    "ps",
    "fa",
    "pl",
    "pt",
    "ro",
    "ru",
    "sm",
    "gd",
    "sr",
    "st",
    "sn",
    "sd",
    "si",
    "sk",
    "sl",
    "so",
    "es",
    "su",
    "sw",
    "sv",
    "tg",
    "ta",
    "te",
    "th",
    "tr",
    "uk",
    "ur",
    "uz",
    "vi",
    "cy",
    "xh",
    "yi",
    "yo",
    "zu"
)

_MIN_QUESTION_LENGTH = 10
_MAX_QUESTION_LENGTH = 200


def _check_message_type(message):
    """Check if the argument is a string.
    If the argument is not a string, raise a TypeError.
    """
    if not isinstance(message, str):
        raise TypeError("Message must be a string.")


def _check_interests_type(interests):
    """Check if the argument is a list.
    If the argument is not a list, raise a TypeError.
    """
    if not isinstance(interests, list):
        raise TypeError("Interests must be a list.")


def _check_language_type_and_value(language):
    """Check if a language specification is valid.
    If the argument is not a string, raise a TypeError.
    If the argument is not a valid language code, that is, it is not
    defined in _LANGUAGE_CODES, raise a ValueError.
    """
    if not isinstance(language, str):
        raise TypeError("Language must be a 'str' instance.")
    elif language.lower() not in _LANGUAGE_CODES:
        raise ValueError(
            "Unknown language: '{}' ".format(language) +
            "(not defined or ambiguous in ISO 639-1 / ISO 639-2)."
        )


def _validate_status_code(response):
    """Check if the argument has a valid response code.
    If the status code is not 200, raise a PythonOmegleException.
    This function assumes the argument is a requests.Response instance.
    """
    if response.status_code != requests.codes.ok:
        raise PythonOmegleException(
            "Request returned bad HTTP status code ({}).".format(
                response.status_code
            )
        )


def _generate_random_id_string():
    """Generate an 8-character random ID string.
    The ID returned consists of digits and uppercase ASCII letters.
    """
    return "".join(random.choice(_RANDOM_ID_POOL) for _ in range(9))


def _make_safe_request(function):
    """Try to return function().
    If a requests.RequestException is caught, raise a
    PythonOmegleException.
    """
    try:
        return function()
    except requests.RequestException as exc:
        error_message = "HTTP request failed (reason: {}).".format(str(exc))
        raise PythonOmegleException(error_message) from None

requests.get_ = requests.get
requests.post_ = requests.post

def _safe_requests_get(*args, **kwargs):
    return _make_safe_request(lambda: requests.get_(*args, **kwargs))

def _safe_requests_post(*args, **kwargs):
    return _make_safe_request(lambda: requests.post_(*args, **kwargs))

requests.get = _safe_requests_get
requests.post = _safe_requests_post

del _safe_requests_get
del _safe_requests_post


def _check_question_type_and_value(question):
    """Check if a question is valid.
    If the argument is not a string, raise a TypeError.
    If the argument is shorter than _MIN_QUESTION_LENGTH, or longer than
    _MAX_QUESTION_LENGTH, raise a ValueError.
    """
    if not isinstance(question, str):
        raise TypeError("Question must be a string.")
    question_length = len(question.strip())
    if question_length < _MIN_QUESTION_LENGTH:
        raise ValueError("Question must be at least 10 characters long.")
    elif question_length > _MAX_QUESTION_LENGTH:
        raise ValueError("Question can't be longer than 200 characters.")
