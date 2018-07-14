import queue
import unittest
import unittest.mock

import sys
sys.path.insert(0, "../")

from python_omegle.randomchat import RandomChat
from python_omegle.chatevent import ChatEvent
from python_omegle.exceptions import PythonOmegleException
from python_omegle._common import _SERVER_POOL

from common import make_events_json


class RandomChatTest(unittest.TestCase):
    def test_constructor(self):
        RandomChat()
        # Custom language
        RandomChat("fr")
        with self.assertRaises(TypeError):
            # Not a str instance
            RandomChat(None)
        with self.assertRaises(ValueError):
            # Not in ISO 639-1 or ISO 639-2
            RandomChat("french")

    def test_initial_default_private_attributes(self):
        chat = RandomChat()

        # _language
        self.assertEqual(chat._language, "en")

        # _server_url
        self.assertIn(chat._server_url, _SERVER_POOL)

        # _events
        self.assertIsInstance(chat._events, queue.Queue)
        self.assertEqual(chat._events.qsize(), 0)

        # _random_id
        self.assertIsInstance(chat._random_id, str)
        self.assertEqual(len(chat._random_id), 8)

        # _chat_id
        self.assertIsNone(chat._chat_id)

        # _chat_ready_flag
        self.assertFalse(chat._chat_ready_flag)

    def test_property_getters(self):
        # With default language
        chat1 = RandomChat()
        self.assertEqual(chat1.language, "en")

        # With custom language
        chat2 = RandomChat("zh")
        self.assertEqual(chat2.language, "zh")

    def test_property_setters(self):
        # With default language
        chat1 = RandomChat()
        chat1.language = "nl"
        self.assertEqual(chat1.language, "nl")

        # With custom language
        chat2 = RandomChat("de")
        chat2.language = "es"
        self.assertEqual(chat2.language, "es")

    def test_simulate_events(self):
        def simulate(*events, chat):
            events_json = make_events_json(*events)
            return chat._classify_events_and_add_to_queue(events_json)

        chat = RandomChat()

        # CHAT_READY
        simulate((ChatEvent.CHAT_READY, None), chat=chat)
        event, argument = chat.get_event()
        self.assertEqual(event, ChatEvent.CHAT_READY)
        self.assertEqual(argument, None)

        # CHAT_ENDED
        simulate((ChatEvent.CHAT_ENDED, None), chat=chat)
        event, argument = chat.get_event()
        self.assertEqual(event, ChatEvent.CHAT_ENDED)
        self.assertEqual(argument, None)

        # GOT_MESSAGE
        # Suppress the initial CHAT_READY event (see test_ready_flag())
        chat._chat_ready_flag = True
        simulate((ChatEvent.GOT_MESSAGE, "Hello, World!"), chat=chat)
        event, argument = chat.get_event()
        self.assertEqual(event, ChatEvent.GOT_MESSAGE)
        self.assertEqual(argument, "Hello, World!")

        # Assert that order is maintained
        simulate((ChatEvent.CHAT_WAITING, None), chat=chat)
        simulate((ChatEvent.CHAT_READY, None), chat=chat)
        event1, _ = chat.get_event()
        event2, _ = chat.get_event()
        self.assertEqual(event1, ChatEvent.CHAT_WAITING)
        self.assertEqual(event2, ChatEvent.CHAT_READY)

    def test_ready_flag(self):
        def simulate(*events, chat):
            events_json = make_events_json(*events)
            return chat._classify_events_and_add_to_queue(events_json)

        chat = RandomChat()

        # CHAT_READY
        self.assertFalse(chat._chat_ready_flag)
        simulate((ChatEvent.CHAT_READY, None), chat=chat)
        self.assertTrue(chat._chat_ready_flag)

        # CHAT_ENDED
        simulate((ChatEvent.CHAT_ENDED, None), chat=chat)
        self.assertFalse(chat._chat_ready_flag)

        # GOT_MESSAGE
        simulate((ChatEvent.GOT_MESSAGE, ""), chat=chat)
        self.assertTrue(chat._chat_ready_flag)

if __name__ == "__main__":
    unittest.main()
