Python-Omegle
=============

Before you can write any code, it's essential to have at least a basic
understanding of the Omegle protocol (the client-server-client protocol), and
of the Python-Omegle protocol (this API).

The Protocol: Omegle
--------------------

Note: If you are only interested in the concrete Omegle protocol, skip right
ahead to `How does Omegle work?`_.

Note: This is not a complete description of the protocol. Because there is no
official Omegle API, some of this information is the result of trial-and-error
testing. To somewhat limit the amount of text in this file, some implementation
details have been left out.

A brief introduction to Omegle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Omegle is a popular online chatting service. The website first launched in
2009, and was an immediate success. [1]_ The website features both a video chat
and a text chat mode. Despite attempts to stop spam, there are still quite a
few bots starting automated chats.

Omegle text chat allows one to chat with a randomly selected partner.
Alternatively, you can chat with someone who shares your interests. In 2011,
spy mode was introduced. In spy mode, you can either be the spy, and pose a
question for two strangers to discuss, or be a spyee, and discuss a question
with another stranger while someone else listens in.

How do client-server-client chat services connect two clients?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most HTTP-based client-server-client chat protocols work like this:

1. A client requests for the server to find a chat partner;
2. The server waits until it gets a request from another client;
3. The server relays messages between between the two, until either one of the
   clients disconnects.

From the client's point of view, this looks something like this:

.. image:: images/basic_chat_flowchart.png

When a client asks the server to find a partner, the server generates a unique
ID for that client. The server then returns a response with the client's ID,
and a status. If at the time the request was made, no other clients were
waiting to start a chat, the server tells the client to standby until further
notice. Once a partner becomes available, the server tells the client it is
connected.

Here's a visualization of this procedure:

.. image:: images/establish_connection.png

The blue text next to each node indicates the status or action taken at that
point. The dashed arrows next to C1 represent I/O operations. You can imagine
similar operations for C2.

How does the server do its job as a middleman?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once two clients are connected to one another, they can start exchanging
messages. To interact with their partner, a client simply sends a request to
the server, including the action they want to perform and their ID. The server
remembers the partner the ID is tied to, and is able to effectively be a
middleman:

.. image:: images/actions.png

The rightwards double arrow (⇒) and the rightwards double arrow with stroke
(⇏) represent 'associated with' and 'not / no longer associated with',
respectively. When the chat ends, the server disposes of the IDs so they may
be reused.

.. _`How does Omegle work?`:

How does Omegle work?
~~~~~~~~~~~~~~~~~~~~~

In the previous sections, some details were intentionally left out, such as
as how querying for a partner works exactly, and how embedding an ID works.
That's because these details are specific to Omegle.

This is the complete flowchart for generalized Omegle client-server
interaction, as seen from the client's point of view:

.. image:: images/complete_omegle_flowchart.png

Don't be overwhelmed, it isn't all that complicated. Let's follow the path
and add comments step by step.

1. The client creates a random ID. The random ID is 8 characters long and
   consists of uppercase letters and digits.

2. The client is now in a state where it can start a new chat.

3. The client sends a request to the server, asking it to look for a partner
   (Request: *Start ___ chat*).

4. If the server returns a client ID, go to 6.

5. If the server does not return a client ID, something went wrong. A common
   issue is server-side spam prevention (using ReCAPTCHA). If that is the
   case, the user is to solve a ReCAPTCHA test before continuing. If the
   issue has nothing to do with ReCAPTCHA, it may be a connection problem.
   The client simply retries until it obtains an ID.

6. Along with the client ID, the server has sent an initial set of events.

7. If one of the events signifies that a connection has been established,
   go to 9.

8. If there is no event that signifies a connection has been established,
   the client tells the user it is waiting for a partner, while continously
   checking in for potential new events (Request: *Query events*) until one
   is found.

9. At this point, a connection between the two clients has been established.

10. The client will make a request to the server to keep updated on the
    latest events (Request: *Query events*).

11. If there are no new events, go to 10.

12. The client processes the events and outputs data accordingly.

13. If any of the events signifies the end of the chat (i.e. the partner
    disconnected, or their connection timed out), go to 2.

14. Go to 10.

This is the table of requests:

.. _`Requests table`:

+----------------------+-----------------+-------------+----------------------+--------------------+
| Requests table                                                                                   |
+----------------------+-----------------+-------------+----------------------+--------------------+
| Description          | URL [2]_        | HTTP method | Parameters           | Static parameters  |
+======================+=================+=============+======================+====================+
| Server               | omegle.com [3]_ | N/A         | N/A                  | N/A                |
+----------------------+-----------------+-------------+----------------------+--------------------+
| Start random chat    | /start?         | GET         | * randid             | * caps: recaptcha2 |
|                      |                 |             | * lang               | * rcs: 1           |
|                      |                 |             |                      | * firstevents: 1   |
+----------------------+-----------------+-------------+----------------------+--------------------+
| Start interests chat | /start?         | GET         | * randid             | * caps: recaptcha2 |
|                      |                 |             | * lang               | * rcs: 1           |
|                      |                 |             | * topics             | * firstevents: 1   |
+----------------------+-----------------+-------------+----------------------+--------------------+
| Start spy chat       | /start?         | GET         | * randid             | * caps: recaptcha2 |
|                      |                 |             | * lang               | * rcs: 1           |
|                      |                 |             |                      | * firstevents: 1   |
|                      |                 |             |                      | * wantspy: 1       |
+----------------------+-----------------+-------------+----------------------+--------------------+
| Query events         | /events         | POST        | * id                 | N/A                |
+----------------------+-----------------+-------------+----------------------+--------------------+
| Send message         | /send           | POST        | * id                 | N/A                |
|                      |                 |             | * msg                |                    |
+----------------------+-----------------+-------------+----------------------+--------------------+
| Disconnect           | /disconnect     | POST        | * id                 | N/A                |
+----------------------+-----------------+-------------+----------------------+--------------------+
| Start typing         | /typing         | POST        | * id                 | N/A                |
+----------------------+-----------------+-------------+----------------------+--------------------+
| Stop typing          | /stoppedtyping  | POST        | * id                 | N/A                |
+----------------------+-----------------+-------------+----------------------+--------------------+

Things to note:

* The *Start ___ chat* requests ask the server to look for a partner, but don't
  guarantee that one is immediately available. This must be confirmed by
  waiting for the right event (see below).
* The static parameters are required by Omegle, but not part of the API.
  Python-Omegle takes care of these behind the scenes.

Most client code will revolve around handling events (step 10). Therefore, the
events events deserve some extra attention. There are 7 different events to
take into account: [4]_

.. _`Events table`:

+------------------------+----------+--------------------+
| Events table                                           |
+------------------------+----------+--------------------+
| Description            | Argument | Notes              |
+========================+==========+====================+
| Chat ready             | [5]_     | N/A                |
+------------------------+----------+--------------------+
| Chat ended             | N/A      | No further actions |
|                        |          | possible with this |
|                        |          | client ID.         |
+------------------------+----------+--------------------+
| Waiting for partner    | N/A      | Could be ignored,  |
|                        |          | potentially useful |
|                        |          | for informing the  |
|                        |          | end user.          |
+------------------------+----------+--------------------+
| Partner started typing | N/A      | Could be ignored,  |
|                        |          | potentially useful |
|                        |          | for informing the  |
|                        |          | end user.          |
+------------------------+----------+--------------------+
| Partner stopped typing | N/A      | Could be ignored,  |
|                        |          | potentially useful |
|                        |          | for informing the  |
|                        |          | end user.          |
+------------------------+----------+--------------------+
| Got message            | Message  | N/A                |
+------------------------+----------+--------------------+
| Got server notice      | Notice   | N/A                |
+------------------------+----------+--------------------+

|

.. _`The Protocol: Python-Omegle`:

The Protocol: Python-Omegle
---------------------------

Of the four Omegle text chat types, Python-Omegle supports three. Each chat
type is a class on its own. Each class instance can dispatch chats: start
them, handle events, interact with the other party, and ultimately disconnect.

Abstract chat
~~~~~~~~~~~~~

Location: `python_omegle/_abstractchat.py`_

The ``_AbstractChat`` class is an abstract type, of which other chats derive.
It defines a number of attributes and methods which are the same across all
chats:

* An event queue, which holds the events in the order they were retrieved;
* A way to start a new chat, using ``_AbstractChat.start()``;
* A way to get an event from the queue, using ``_AbstractChat.get_event()``;
* A way to send a message, using ``_AbstractChat.send()``;
* A way to disconnect, using ``_AbstractChat.disconnect()``;
* A way to tell the server the user started typing, using
  ``_AbstractChat.start_typing()``;
* A way to tell the server the user stopped typing, using
  ``_AbstractChat.stop_typing()``;
* A way to get and set the language option, which allows client to filter
  chats by language, using ``_AbstractChat.language``;
* Other attributes intended for internal use.

The API for these methods is identical for all chat types. The only
exception to that rule is ``_AbstractChat.get_event()``.
``_AbstractChat.get_event()`` always returns an (event, argument) tuple,
the first element of which is an enum value indicating the type of event,
and the second element of which is a string, list or ``None``, depending on
the argument included in the HTTP response.

If the method is called and the event queue contains at least one event,
the first event is returned. If the method is called, and the event queue
is empty, the operation blocks until at least one event is retrieved. The
event(s) are then put onto the queue, and a single event is returned from
the queue.

Chat event enum
~~~~~~~~~~~~~~~

The enum values for the various event types are part of the ``ChatEvent``
enum, located in `python_omegle/chatevent.py`_. The full list of enum values
is:

* ``ChatEvent.CHAT_READY``
* ``ChatEvent.CHAT_WAITING``
* ``ChatEvent.CHAT_ENDED``
* ``ChatEvent.GOT_SERVER_NOTICE``
* ``ChatEvent.GOT_MESSAGE``
* ``ChatEvent.PARTNER_STARTED_TYPING``
* ``ChatEvent.PARTNER_STOPPED_TYPING``

Exceptions
~~~~~~~~~~

Location: `python_omegle/exceptions.py`_

Currently, only one custom exception is defined: ``PythonOmegleException``.
Trivial problems, such as passing an incorrect argument type or value, will
raise a ``TypeError`` or ``ValueError``. ``PythonOmegleException`` is only
raised for problems with the server response, or when a ReCAPTCHA check must
be completed.

Random chat
~~~~~~~~~~~

Location: `python_omegle/randomchat.py`_

A random chat is essentially a match with a randomly picked stranger. It is the
least complicated of the classes: ``RandomChat.__init__()`` only accepts one
argument: the language to converse in. This argument defaults to the string
'en' (= English). Note that many languages are supported, but you must supply a
language code defined in `ISO 639-1`_. The language can be changed at runtime,
but the change will only be applied the next time a chat is started.

We now know enough about Python and Python-Omegle to write our first program.
This simple script creates a chat instance, connects to a stranger, sends a
message, and disconnects.

.. code:: python

  from python_omegle.randomchat import RandomChat
  from python_omegle.chatevent import ChatEvent

  chat = RandomChat()
  chat.start()
  while True:
      event, argument = chat.get_event()
      if event == ChatEvent.CHAT_READY:
          break
  # Connected, let's send the message
  chat.send("Goodbye")
  chat.disconnect()

If you run the script, chances are you're met with a ``PythonOmegleException``:

.. code::

  Traceback (most recent call last):
  ...
    raise PythonOmegleException("ReCAPTCHA check required.")
  python_omegle.exceptions.PythonOmegleException: ReCAPTCHA check required.

To prevent people from starting automated chats, Omegle uses the
`ReCAPTCHA protocol`_. After a period of inactivity on the website, the user
must pass a ReCAPTCHA test. The user is then free to start chats, until they
hit a cap. During the cooldown period, every time a new chat is started, a
ReCAPTCHA must be solved. There are no plans to incorporate a workaround for
the cap in this library. To be able to follow along with the tutorial, please
go to the Omegle website, start a chat, pass a ReCAPTCHA test successfully,
and then return.

Want to be really annoying and just watch other people wait for you to say
something?

.. code:: python

  from python_omegle.randomchat import RandomChat
  from python_omegle.chatevent import ChatEvent

  chat = RandomChat()
  chat.start()

  while True:
      event, argument = chat.get_event()
      if event == ChatEvent.CHAT_READY:
          print("- Connected to a partner -")
          break
      elif event == ChatEvent.CHAT_WAITING:
          print("- Waiting for a partner -")

  while True:
      event, argument = chat.get_event()
      if event == ChatEvent.GOT_MESSAGE:
          message = argument
          print("Partner: {}".format(message))
      elif event == ChatEvent.CHAT_ENDED:
          print("- Chat ended - ")
          break

----

Quick tip: The __init__.py file for Python-Omegle contains all the classes
that are part of the API. There is no need to import from the modules
themselves. For the remainder of this tutorial, objects will be imported from
`python_omegle/__init__.py`_.

----

The examples are neat, but don't utilize the full power of the
``RandomChat`` class. This script does the same thing as above, in a loop,
with additional event handling:

.. code:: python

  from python_omegle import RandomChat
  from python_omegle import ChatEvent


  def chat_loop(chat):
      while True:
          # Start a new chat every time the old one ends
          print("- Starting chat -")
          chat.start()
          while True:
              event, argument = chat.get_event()
              if event == ChatEvent.CHAT_WAITING:
                  print("- Waiting for a partner -")
              elif event == ChatEvent.CHAT_READY:
                  print("- Connected to a partner -")
                  break
          # Connected to a partner
          while True:
              event, argument = chat.get_event()
              if event == ChatEvent.GOT_SERVER_NOTICE:
                  notice = argument
                  print("- Server notice: {} -".format(notice))
              elif event == ChatEvent.PARTNER_STARTED_TYPING:
                  print("- Partner started typing -")
              elif event == ChatEvent.PARTNER_STOPPED_TYPING:
                  print("- Partner stopped typing -")
              elif event == ChatEvent.GOT_MESSAGE:
                  message = argument
                  print("Partner: {}".format(message))
              elif event == ChatEvent.CHAT_ENDED:
                  print("- Chat ended -")
                  break

  if __name__ == "__main__":
      chat = RandomChat()
      chat_loop(chat=chat)


Interest-based chat
~~~~~~~~~~~~~~~~~~~

Tired of getting matched with bots?  Picking the right topics minimizes the
chance of connecting to bots. This should look familiar now:

.. code:: python

  from python_omegle import InterestsChat
  from python_omegle import ChatEvent

  # We'll talk about foo and/or bar
  chat = InterestsChat(["foo", "bar"])
  chat.start()
  while True:
      event, argument = chat.get_event()
      if event == ChatEvent.CHAT_READY:
          common_interests = argument
          print("- Connected, common interests: {} -".format(*common_interests))
          break
  chat.send("Goodbye")
  chat.disconnect()

One thing to note is that the argument for ``ChatEvent.CHAT_READY`` is not
``None``, as was the case with ``RandomChat``, but is a list of common
interests. This list may contain all interests, or be a subset of what was
passed to the constructor.

Just like with ``RandomChat``, the language can be set in the
constructor:

.. code:: python

  # We'll talk about foo and/or bar in Spanish
  chat = InterestsChat(["foo", "bar"], language="es")
  # ...

... or modified dynamically using ``InterestsChat.language``:

.. code:: python

  # We'll talk about foo and/or bar in Spanish
  chat = InterestsChat(["foo", "bar"], language="es")
  # Actually, we'll go with French
  chat.language = "fr"
  # ...

And the same goes for the interests (``InterestsChat.interests``):

.. code:: python

  # We'll talk about foo and/or bar
  chat = InterestsChat(["foo", "bar"])
  # quux is interesting too
  chat.interests.append("quux")


Spyee chat
~~~~~~~~~~

Lastly, there's spyee mode:

.. code:: python

  from python_omegle import SpyeeChat
  from python_omegle import ChatEvent

  chat = SpyeeChat()
  chat.start()
  while True:
      event, argument = chat.get_event()
      if event == ChatEvent.CHAT_READY:
          question = argument
          print("- Discuss this question: {} -".format(question))
          break
  chat.send("Goodbye")
  chat.disconnect()

Note how the argument for ``ChatEvent.CHAT_READY`` is now the question posed by
the spy.

|

Issues
------

1. Two languages which are supported on the Omegle website but not defined in
ISO 639-1 are Cebuano and Filipino, which are defined in `ISO 639-2`_ instead,
and are the only supported languages with a three letter language code. Frisian
and Hmong are not accepted, even though they're supported on the Omegle website
and are part of ISO 639-1, because their language code is ambiguous.

2. After you receive a ``ChatEvent.PARTNER_STARTED_TYPING`` event, it's
very likely that you will not receive a ``ChatEvent.PARTNER_STOPPED_TYPING``
event when your partner sends you a message. That's an intentional design choice
in the Omegle protocol, not a bug. Because this may be seen as a quirk of the
API, it's on the todo list to fix this and mock a
``ChatEvent.PARTNER_STOPPED_TYPING`` encounter.

|

Reference
---------

XXX

|

----

.. [1] `Welcome to the omegle blog!`_ (archive.org)

.. [2] The URLs listed below have an implicit base URL of frontN.omegle.com (see the
       `Requests table`_ and [4]_). For example, the *Send* URL is actually
       frontN.omegle.com/send.

.. [3] The server URL (listed as 'omegle.com') is actually any of 32 addresses. The URL is
       frontN.omegle.com, where N is a number 1 through 32.

.. [4] There are other events, but they can be ignored, or are dealt with by Python-Omegle
       in an appropiate manner. For example, 'recaptchaRequired' is not listed, because
       when encountered, an exception is raised. It wouldn't make sense to expose these
       types of events.

.. [5] The argument for the 'Connected' event depends on the type of chat. This event will
       be explained in detail in the respective sections.


.. _`python_omegle/_abstractchat.py`: ../python_omegle/_abstractchat.py

.. _`python_omegle/chatevent.py`: ../python_omegle/chatevent.py

.. _`python_omegle/exceptions.py`: ../python_omegle/exceptions.py

.. _`python_omegle/randomchat.py`: ../python_omegle/randomchat.py

.. _`ISO 639-1`: https://en.wikipedia.org/wiki/ISO_639-1

.. _`ISO 639-2`: https://en.wikipedia.org/wiki/ISO_639-2

.. _`ReCAPTCHA protocol`: https://google.com/recaptcha/

.. _`python_omegle/__init__.py`: python_omegle/__init__.py

.. _`Welcome to the omegle blog!`: https://web.archive.org/web/20090403052716/http://omegler.blogspot.com/2009/03/welcome-to-omegle-blog.html
