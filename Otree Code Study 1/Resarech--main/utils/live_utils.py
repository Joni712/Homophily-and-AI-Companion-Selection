""" Utils for advanced live page messaging

The messages carry a type and some data. Each message is processed by a handler of corresponding type.

Messages from server can be adressed to several players, 
addressed by player instance, player id, string "other" for non-adressed players, or "all" for all players.

# Usage

```
@live_page
class SomePage(Page):
    
    @live_method('sometype')
    def handle_msg(player, data):
        # handle message of type 'sometype'
        ...
        # send response message of a type to the player
        yield player, type, msgdata
        # send another message to another player
        yield player2, type2, msgdata2

```

"""

import inspect
import types

from otree.api import BasePlayer


def expand_recipients(group, response):
    """ Replaces recipients with their player ids,
    handles player instances, 'all', 'others' 
    """

    if 'all' in response:
        if len(list(response.keys())) != 1:
            raise ValueError("Can not address 'all' and someone else")
        return { 0: response['all'] }

    expanded = {}

    expanded.update({
        rcpt: data
        for rcpt, data in response.items() if isinstance(rcpt, int)
    })

    expanded.update({
        rcpt.id_in_group: data
        for rcpt, data in response.items() if isinstance(rcpt, BasePlayer)
    })    

    if 'others' in response:
        msg = response.pop('others')  # type: ignore
        for p in group.get_players():
            id = p.id_in_group
            if id not in expanded:
                expanded[id] = msg

    return expanded


def live_method(name):
    def augmenter(method):
        method.__live_handler = name
        return staticmethod(method)

    return augmenter


def live_page(cls):
    handlers = {
        getattr(method, "__live_handler"): method
        for (_, method) in inspect.getmembers(cls, lambda m: inspect.isfunction(m) and hasattr(m, "__live_handler"))
    }

    def generic_live_method(player: BasePlayer, message: dict):
        if len(list(message.keys())) != 1:
            raise ValueError("Invalid input message format, expected { type: data }")

        msgtype, msgdata = list(message.items())[0]

        if msgtype not in handlers:
            raise RuntimeError(f"Missing @live_method('{msgtype}')")

        handler = handlers[msgtype]
        handled = handler(player, msgdata)

        if not isinstance(handled, types.GeneratorType):
            raise RuntimeError(f"Expected @live_method('{msgtype}') to `yield` responses")

        responses = {}
        for rcpt, t, data in handled:
            if rcpt not in responses:
                responses[rcpt] = {}
            responses[rcpt][t] = data
        responses = expand_recipients(player.group, responses)
        return responses

    cls.live_method = staticmethod(generic_live_method)

    return cls