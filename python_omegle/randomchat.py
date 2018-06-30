import json

from python_omegle._abstractchat import _AbstractChat
from python_omegle._common import (
    requests,   # patched
    _START_URL,
    _validate_status_code
)
from python_omegle.chatevent import ChatEvent
from python_omegle.exceptions import PythonOmegleException


class RandomChat(_AbstractChat):
    """Represents a chat with a randomly picked partner.

    Please refer to the documentation for an elaborate description
    of the Python-Omegle protocol.
    """

    def __init__(self, language="en"):
        """Constructor.

        Arguments:
            - language = "en" (str): The language in which to converse.
              This must be a language code defined in ISO 639-1. The
              languages Cebuano (ceb) and Filipino (fil) are also
              supported, but only defined in ISO 639-2. Some languages
              supported on the Omegle website are not supported because
              they are ambiguous.

        Return:
            - No return value.
        """
        super().__init__(language=language)

    def start(self):
        """Start looking for a partner.

        Ask the server to start looking for a partner. Ideally, the
        server returns a client ID. If the client ID is obtained
        successfully, add initial events to the event queue and return.

        Raise:
            - PythonOmegleException if the response's status code is not
              200.

            - PythonOmegleException if the response does not include a
              client ID.

        Return:
            - No return value.
        """
        response = requests.get(
            self._server_url + _START_URL.format(
                self._random_id,    # randid
                self.language       # lang
            )
        )
        _validate_status_code(response=response)
        json_data = json.loads(response.text)

        try:
            self._chat_id = json_data["clientID"]
        except KeyError:
            raise PythonOmegleException("Failed to get chat ID.")

        try:
            events_json = json_data["events"]
        except KeyError:
            return
        self._classify_events_and_add_to_queue(events_json=events_json)

    def _classify_events_and_add_to_queue(self, events_json):
        for event in events_json:
            event_type = event[0]
            if event_type == "connected":
                self._chat_ready_flag = True
                self._events.put((ChatEvent.CHAT_READY, None))
            elif event_type == "waiting":
                self._events.put((ChatEvent.CHAT_WAITING, None))
            elif event_type == "typing":
                if not self._chat_ready_flag:
                    # Simulate a 'chat ready' event (see Issues: 1)
                    self._events.put((ChatEvent.CHAT_READY, None))
                self._events.put((ChatEvent.PARTNER_STARTED_TYPING, None))
            elif event_type == "stoppedTyping":
                self._events.put((ChatEvent.PARTNER_STOPPED_TYPING, None))
            elif event_type == "gotMessage":
                if not self._chat_ready_flag:
                    # Simulate a 'chat ready' event (see Issues: 1)
                    self._events.put((ChatEvent.CHAT_READY, None))
                message = event[1]
                self._events.put((ChatEvent.GOT_MESSAGE, message))
            elif event_type == "strangerDisconnected":
                if not self._chat_ready_flag:
                    # Simulate a 'chat ready' event (see Issues: 1)
                    self._events.put((ChatEvent.CHAT_READY, None))
                self._events.put((ChatEvent.CHAT_ENDED, None))
                self._chat_ready_flag = False
            elif event_type == "serverMessage":
                notice = event[1]
                self._events.put((ChatEvent.GOT_SERVER_NOTICE, notice))
            elif event_type == "identDigests":
                # Included after a partner was found, may be ignored.
                pass
            elif event_type == "recaptchaRequired":
                raise PythonOmegleException("ReCAPTCHA check required.")
