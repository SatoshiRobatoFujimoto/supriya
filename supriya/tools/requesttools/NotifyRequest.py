# -*- encoding: utf-8 -*-
from supriya.tools import osctools
from supriya.tools.requesttools.Request import Request


class NotifyRequest(Request):

    ### CLASS VARIABLES ###

    __slots__ = (
        '_notify_status',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        notify_status=None,
        ):
        self._notify_status = bool(notify_status)

    ### PUBLIC METHODS ###

    def to_osc_message(self):
        request_id = int(self.request_id)
        notify_status = int(self.notify_status)
        message = osctools.OscMessage(
            request_id,
            notify_status,
            )
        return message

    ### PUBLIC PROPERTIES ###

    @property
    def notify_status(self):
        return self._notify_status

    @property
    def response_prototype(self):
        return None

    @property
    def request_id(self):
        from supriya.tools import requesttools
        return requesttools.RequestId.NOTIFY