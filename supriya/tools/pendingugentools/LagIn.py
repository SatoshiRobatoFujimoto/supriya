# -*- encoding: utf-8 -*-
from supriya.tools.ugentools.AbstractIn import AbstractIn


class LagIn(AbstractIn):
    r'''

    ::

        >>> lag_in = ugentools.LagIn.(
        ...     bus=0,
        ...     channel_count=1,
        ...     lag=0.1,
        ...     )
        >>> lag_in

    '''

    ### CLASS VARIABLES ###

    __documentation_section__ = None

    __slots__ = ()

    _ordered_input_names = (
        'bus',
        'channel_count',
        'lag',
        )

    _valid_calculation_rates = None

    ### INITIALIZER ###

    def __init__(
        self,
        calculation_rate=None,
        bus=0,
        channel_count=1,
        lag=0.1,
        ):
        AbstractIn.__init__(
            self,
            calculation_rate=calculation_rate,
            bus=bus,
            channel_count=channel_count,
            lag=lag,
            )

    ### PUBLIC METHODS ###

    # def isInputUGen(): ...

    @classmethod
    def kr(
        cls,
        bus=0,
        channel_count=1,
        lag=0.1,
        ):
        r'''Constructs a control-rate LagIn.

        ::

            >>> lag_in = ugentools.LagIn.kr(
            ...     bus=0,
            ...     channel_count=1,
            ...     lag=0.1,
            ...     )
            >>> lag_in

        Returns ugen graph.
        '''
        from supriya.tools import synthdeftools
        calculation_rate = synthdeftools.CalculationRate.CONTROL
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            bus=bus,
            channel_count=channel_count,
            lag=lag,
            )
        return ugen

    # def newFromDesc(): ...

    ### PUBLIC PROPERTIES ###

    @property
    def bus(self):
        r'''Gets `bus` input of LagIn.

        ::

            >>> lag_in = ugentools.LagIn.ar(
            ...     bus=0,
            ...     channel_count=1,
            ...     lag=0.1,
            ...     )
            >>> lag_in.bus

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('bus')
        return self._inputs[index]

    @property
    def channel_count(self):
        r'''Gets `channel_count` input of LagIn.

        ::

            >>> lag_in = ugentools.LagIn.ar(
            ...     bus=0,
            ...     channel_count=1,
            ...     lag=0.1,
            ...     )
            >>> lag_in.channel_count

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('channel_count')
        return self._inputs[index]

    @property
    def lag(self):
        r'''Gets `lag` input of LagIn.

        ::

            >>> lag_in = ugentools.LagIn.ar(
            ...     bus=0,
            ...     channel_count=1,
            ...     lag=0.1,
            ...     )
            >>> lag_in.lag

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('lag')
        return self._inputs[index]