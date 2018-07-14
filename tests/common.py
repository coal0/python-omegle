import sys
sys.path.insert(0, "../")

from python_omegle.chatevent import ChatEvent


def make_events_json(*events):
    EVENT_ENUM_TO_STRINGS = {
        ChatEvent.CHAT_READY: "connected",
        ChatEvent.CHAT_WAITING: "waiting",
        ChatEvent.CHAT_ENDED: "strangerDisconnected",
        ChatEvent.GOT_MESSAGE: "gotMessage",
        ChatEvent.PARTNER_STARTED_TYPING: "typing",
        ChatEvent.PARTNER_STOPPED_TYPING: "stoppedTyping",
        ChatEvent.GOT_SERVER_NOTICE: "serverMessage"
    }

    events_json = [(EVENT_ENUM_TO_STRINGS[event], argument) for event, argument in events]
    # Spyee chat expects a question
    events_json.append(("question", "dummy: question"))
    # Interests chat expects common interests
    events_json.append(("commonLikes", "dummy: common likes"))
    return events_json
