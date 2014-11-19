# -*- encoding: utf-8 -*-
from supriya.tools.ugentools.PulseCount import PulseCount


class SetResetFF(PulseCount):
    r'''

    ::

        >>> set_reset_ff = ugentools.SetResetFF.(
        ...     reset=0,
        ...     trigger=0,
        ...     )
        >>> set_reset_ff

    '''

    ### CLASS VARIABLES ###

    __documentation_section__ = None

    __slots__ = ()

    _ordered_input_names = (
        'trigger',
        'reset',
        )

    _valid_calculation_rates = None

    ### INITIALIZER ###

    def __init__(
        self,
        calculation_rate=None,
        reset=0,
        trigger=0,
        ):
        PulseCount.__init__(
            self,
            calculation_rate=calculation_rate,
            reset=reset,
            trigger=trigger,
            )

    ### PUBLIC METHODS ###

    @classmethod
    def ar(
        cls,
        reset=0,
        trigger=0,
        ):
        r'''Constructs an audio-rate SetResetFF.

        ::

            >>> set_reset_ff = ugentools.SetResetFF.ar(
            ...     reset=0,
            ...     trigger=0,
            ...     )
            >>> set_reset_ff

        Returns ugen graph.
        '''
        from supriya.tools import synthdeftools
        calculation_rate = synthdeftools.CalculationRate.AUDIO
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            reset=reset,
            trigger=trigger,
            )
        return ugen

    @classmethod
    def kr(
        cls,
        reset=0,
        trigger=0,
        ):
        r'''Constructs a control-rate SetResetFF.

        ::

            >>> set_reset_ff = ugentools.SetResetFF.kr(
            ...     reset=0,
            ...     trigger=0,
            ...     )
            >>> set_reset_ff

        Returns ugen graph.
        '''
        from supriya.tools import synthdeftools
        calculation_rate = synthdeftools.CalculationRate.CONTROL
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            reset=reset,
            trigger=trigger,
            )
        return ugen

    ### PUBLIC PROPERTIES ###

    @property
    def trigger(self):
        r'''Gets `trigger` input of SetResetFF.

        ::

            >>> set_reset_ff = ugentools.SetResetFF.ar(
            ...     reset=0,
            ...     trigger=0,
            ...     )
            >>> set_reset_ff.trigger

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('trigger')
        return self._inputs[index]

    @property
    def reset(self):
        r'''Gets `reset` input of SetResetFF.

        ::

            >>> set_reset_ff = ugentools.SetResetFF.ar(
            ...     reset=0,
            ...     trigger=0,
            ...     )
            >>> set_reset_ff.reset

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('reset')
        return self._inputs[index]