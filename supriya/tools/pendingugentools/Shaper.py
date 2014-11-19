# -*- encoding: utf-8 -*-
from supriya.tools.ugentools.Index import Index


class Shaper(Index):
    r'''

    ::

        >>> shaper = ugentools.Shaper.(
        ...     buffer_id=None,
        ...     source=None,
        ...     )
        >>> shaper

    '''

    ### CLASS VARIABLES ###

    __documentation_section__ = None

    __slots__ = ()

    _ordered_input_names = (
        'buffer_id',
        'source',
        )

    _valid_calculation_rates = None

    ### INITIALIZER ###

    def __init__(
        self,
        calculation_rate=None,
        buffer_id=None,
        source=None,
        ):
        Index.__init__(
            self,
            calculation_rate=calculation_rate,
            buffer_id=buffer_id,
            source=source,
            )

    ### PUBLIC METHODS ###

    @classmethod
    def ar(
        cls,
        buffer_id=None,
        source=None,
        ):
        r'''Constructs an audio-rate Shaper.

        ::

            >>> shaper = ugentools.Shaper.ar(
            ...     buffer_id=None,
            ...     source=None,
            ...     )
            >>> shaper

        Returns ugen graph.
        '''
        from supriya.tools import synthdeftools
        calculation_rate = synthdeftools.CalculationRate.AUDIO
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            buffer_id=buffer_id,
            source=source,
            )
        return ugen

    @classmethod
    def kr(
        cls,
        buffer_id=None,
        source=None,
        ):
        r'''Constructs a control-rate Shaper.

        ::

            >>> shaper = ugentools.Shaper.kr(
            ...     buffer_id=None,
            ...     source=None,
            ...     )
            >>> shaper

        Returns ugen graph.
        '''
        from supriya.tools import synthdeftools
        calculation_rate = synthdeftools.CalculationRate.CONTROL
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            buffer_id=buffer_id,
            source=source,
            )
        return ugen

    ### PUBLIC PROPERTIES ###

    @property
    def buffer_id(self):
        r'''Gets `buffer_id` input of Shaper.

        ::

            >>> shaper = ugentools.Shaper.ar(
            ...     buffer_id=None,
            ...     source=None,
            ...     )
            >>> shaper.buffer_id

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('buffer_id')
        return self._inputs[index]

    @property
    def source(self):
        r'''Gets `source` input of Shaper.

        ::

            >>> shaper = ugentools.Shaper.ar(
            ...     buffer_id=None,
            ...     source=None,
            ...     )
            >>> shaper.source

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('source')
        return self._inputs[index]