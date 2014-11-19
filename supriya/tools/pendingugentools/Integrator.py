# -*- encoding: utf-8 -*-
from supriya.tools.ugentools.Filter import Filter


class Integrator(Filter):
    r'''

    ::

        >>> integrator = ugentools.Integrator.(
        ...     coefficient=1,
        ...     source=None,
        ...     )
        >>> integrator

    '''

    ### CLASS VARIABLES ###

    __documentation_section__ = None

    __slots__ = ()

    _ordered_input_names = (
        'source',
        'coefficient',
        )

    _valid_calculation_rates = None

    ### INITIALIZER ###

    def __init__(
        self,
        calculation_rate=None,
        coefficient=1,
        source=None,
        ):
        Filter.__init__(
            self,
            calculation_rate=calculation_rate,
            coefficient=coefficient,
            source=source,
            )

    ### PUBLIC METHODS ###

    @classmethod
    def ar(
        cls,
        coefficient=1,
        source=None,
        ):
        r'''Constructs an audio-rate Integrator.

        ::

            >>> integrator = ugentools.Integrator.ar(
            ...     coefficient=1,
            ...     source=None,
            ...     )
            >>> integrator

        Returns ugen graph.
        '''
        from supriya.tools import synthdeftools
        calculation_rate = synthdeftools.CalculationRate.AUDIO
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            coefficient=coefficient,
            source=source,
            )
        return ugen

    # def coeffs(): ...

    @classmethod
    def kr(
        cls,
        coefficient=1,
        source=None,
        ):
        r'''Constructs a control-rate Integrator.

        ::

            >>> integrator = ugentools.Integrator.kr(
            ...     coefficient=1,
            ...     source=None,
            ...     )
            >>> integrator

        Returns ugen graph.
        '''
        from supriya.tools import synthdeftools
        calculation_rate = synthdeftools.CalculationRate.CONTROL
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            coefficient=coefficient,
            source=source,
            )
        return ugen

    # def magResponse(): ...

    # def magResponse2(): ...

    # def magResponse5(): ...

    # def magResponseN(): ...

    # def scopeResponse(): ...

    ### PUBLIC PROPERTIES ###

    @property
    def source(self):
        r'''Gets `source` input of Integrator.

        ::

            >>> integrator = ugentools.Integrator.ar(
            ...     coefficient=1,
            ...     source=None,
            ...     )
            >>> integrator.source

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('source')
        return self._inputs[index]

    @property
    def coefficient(self):
        r'''Gets `coefficient` input of Integrator.

        ::

            >>> integrator = ugentools.Integrator.ar(
            ...     coefficient=1,
            ...     source=None,
            ...     )
            >>> integrator.coefficient

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('coefficient')
        return self._inputs[index]