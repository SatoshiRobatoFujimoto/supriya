# -*- encoding: utf-8 -*-
from supriya.tools.synthdeftools.UGen import UGen


class Stepper(UGen):
    r'''

    ::

        >>> stepper = ugentools.Stepper.(
        ...     maximum=7,
        ...     minimum=0,
        ...     reset=0,
        ...     resetval=None,
        ...     step=1,
        ...     trigger=0,
        ...     )
        >>> stepper

    '''

    ### CLASS VARIABLES ###

    __documentation_section__ = None

    __slots__ = ()

    _ordered_input_names = (
        'trigger',
        'reset',
        'minimum',
        'maximum',
        'step',
        'resetval',
        )

    _valid_calculation_rates = None

    ### INITIALIZER ###

    def __init__(
        self,
        calculation_rate=None,
        maximum=7,
        minimum=0,
        reset=0,
        resetval=None,
        step=1,
        trigger=0,
        ):
        UGen.__init__(
            self,
            calculation_rate=calculation_rate,
            maximum=maximum,
            minimum=minimum,
            reset=reset,
            resetval=resetval,
            step=step,
            trigger=trigger,
            )

    ### PUBLIC METHODS ###

    @classmethod
    def ar(
        cls,
        maximum=7,
        minimum=0,
        reset=0,
        resetval=None,
        step=1,
        trigger=0,
        ):
        r'''Constructs an audio-rate Stepper.

        ::

            >>> stepper = ugentools.Stepper.ar(
            ...     maximum=7,
            ...     minimum=0,
            ...     reset=0,
            ...     resetval=None,
            ...     step=1,
            ...     trigger=0,
            ...     )
            >>> stepper

        Returns ugen graph.
        '''
        from supriya.tools import synthdeftools
        calculation_rate = synthdeftools.CalculationRate.AUDIO
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            maximum=maximum,
            minimum=minimum,
            reset=reset,
            resetval=resetval,
            step=step,
            trigger=trigger,
            )
        return ugen

    @classmethod
    def kr(
        cls,
        maximum=7,
        minimum=0,
        reset=0,
        resetval=None,
        step=1,
        trigger=0,
        ):
        r'''Constructs a control-rate Stepper.

        ::

            >>> stepper = ugentools.Stepper.kr(
            ...     maximum=7,
            ...     minimum=0,
            ...     reset=0,
            ...     resetval=None,
            ...     step=1,
            ...     trigger=0,
            ...     )
            >>> stepper

        Returns ugen graph.
        '''
        from supriya.tools import synthdeftools
        calculation_rate = synthdeftools.CalculationRate.CONTROL
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            maximum=maximum,
            minimum=minimum,
            reset=reset,
            resetval=resetval,
            step=step,
            trigger=trigger,
            )
        return ugen

    ### PUBLIC PROPERTIES ###

    @property
    def trigger(self):
        r'''Gets `trigger` input of Stepper.

        ::

            >>> stepper = ugentools.Stepper.ar(
            ...     maximum=7,
            ...     minimum=0,
            ...     reset=0,
            ...     resetval=None,
            ...     step=1,
            ...     trigger=0,
            ...     )
            >>> stepper.trigger

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('trigger')
        return self._inputs[index]

    @property
    def reset(self):
        r'''Gets `reset` input of Stepper.

        ::

            >>> stepper = ugentools.Stepper.ar(
            ...     maximum=7,
            ...     minimum=0,
            ...     reset=0,
            ...     resetval=None,
            ...     step=1,
            ...     trigger=0,
            ...     )
            >>> stepper.reset

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('reset')
        return self._inputs[index]

    @property
    def minimum(self):
        r'''Gets `minimum` input of Stepper.

        ::

            >>> stepper = ugentools.Stepper.ar(
            ...     maximum=7,
            ...     minimum=0,
            ...     reset=0,
            ...     resetval=None,
            ...     step=1,
            ...     trigger=0,
            ...     )
            >>> stepper.minimum

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('minimum')
        return self._inputs[index]

    @property
    def maximum(self):
        r'''Gets `maximum` input of Stepper.

        ::

            >>> stepper = ugentools.Stepper.ar(
            ...     maximum=7,
            ...     minimum=0,
            ...     reset=0,
            ...     resetval=None,
            ...     step=1,
            ...     trigger=0,
            ...     )
            >>> stepper.maximum

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('maximum')
        return self._inputs[index]

    @property
    def step(self):
        r'''Gets `step` input of Stepper.

        ::

            >>> stepper = ugentools.Stepper.ar(
            ...     maximum=7,
            ...     minimum=0,
            ...     reset=0,
            ...     resetval=None,
            ...     step=1,
            ...     trigger=0,
            ...     )
            >>> stepper.step

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('step')
        return self._inputs[index]

    @property
    def resetval(self):
        r'''Gets `resetval` input of Stepper.

        ::

            >>> stepper = ugentools.Stepper.ar(
            ...     maximum=7,
            ...     minimum=0,
            ...     reset=0,
            ...     resetval=None,
            ...     step=1,
            ...     trigger=0,
            ...     )
            >>> stepper.resetval

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('resetval')
        return self._inputs[index]