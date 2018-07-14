import abc
import json
import queue
import random

from python_omegle._common import (
    requests,   # patched
    _SERVER_POOL,
    _generate_random_id_string,
    _check_message_type,
    _check_language_type_and_value,
    _SEND_URL,
    _STOPPED_TYPING_URL,
    _TYPING_URL,
    _DISCONNECT_URL,
    _EVENTS_URL
)

__all__ = []


class _AbstractChat(metaclass=abc.ABCMeta):
    def __init__(self, language):
        """Constructor.

        Arguments:
            - language (str): The language in which the client wants to
              converse. This must be a language code defined in ISO
              639-1. The languages Cebuano (ceb) and Filipino (fil) are
              also supported, but are defined in ISO 639-2. Some
              languages supported on the Omegle website are not
              supported here because the language codes are ambiguous.

        Return:
            - No return value.
        """
        self.language = language
        self._server_url = random.choice(_SERVER_POOL)
        self._events = queue.Queue()
        self._random_id = _generate_random_id_string()
        self._chat_id = None
        self._chat_ready_flag = False

    @abc.abstractmethod
    def start(self):
        raise NotImplementedError("Method must be implemented in a subclass.")

    def get_event(self):
        """Return the latest event.

        Try to return an event from the queue. If the queue is empty,
        make a request and add the new events to the queue. If there are
        no new events to be added to the queue, continue making requests
        until a new event occurs (or the connection is closed).

        Return:
            - (tuple) An event, argument tuple. If there is no argument
              associated with the event, the argument value will be
              None.
        """
        try:
            return self._events.get_nowait()
        except queue.Empty:
            pass

        # If we get here, it means there are no events left on the
        # queue, so we must ask the server if there are any new events.
        events_json = self._get_new_events()
        self._classify_events_and_add_to_queue(events_json=events_json)
        # We now have a guarantee that there is at least one event ready
        # to be processed.
        return self._events.get()

    def send(self, message):
        """Send a message to the partner.

        Arguments:
            - message (str): The message to send.

        Raise:
            - PythonOmegleException if the HTTP request fails.

        Return:
            - No return value.
        """
        _check_message_type(message=message)
        response = requests.post(
            self._server_url + _SEND_URL,
            data={"id": self._chat_id, "msg": message}
        )

    def disconnect(self):
        """Disconnect from the chat (leave).

        Raise:
            - PythonOmegleException if the HTTP request fails.

        Return:
            - No return value.
        """
        response = requests.post(
            self._server_url + _DISCONNECT_URL,
            data={"id": self._chat_id}
        )
        self._chat_ready_flag = False

    def start_typing(self):
        """Tell the server that the client has started typing.

        Raise:
            - PythonOmegleException if the HTTP request fails.

        Return:
            - No return value.
        """
        response = requests.post(
            self._server_url + _TYPING_URL,
            data={"id": self._chat_id}
        )

    def stop_typing(self):
        """Tell the server that the client has stopped typing.

        Raise:
            - PythonOmegleException if the HTTP request fails.

        Return:
            - No return value.
        """
        response = requests.post(
            self._server_url + _STOPPED_TYPING_URL,
            data={"id": self._chat_id}
        )

    @property
    def language(self):
        return self._language

    @language.setter
    def language(self, language):
        _check_language_type_and_value(language=language)
        self._language = language

    def _get_new_events(self):
        while True:
            response = requests.post(
                self._server_url + _EVENTS_URL,
                data={"id": self._chat_id}
            )

            json_data = json.loads(response.text)
            if json_data not in (None, []):
                # NOTE: Not using implicit boolean comparison here,
                # because we only want to compare to 'null' and the
                # empty array.
                return json_data
