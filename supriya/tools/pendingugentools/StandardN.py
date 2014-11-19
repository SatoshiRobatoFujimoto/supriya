# -*- encoding: utf-8 -*-
from supriya.tools.ugentools.ChaosGen import ChaosGen


class StandardN(ChaosGen):
    r'''

    ::

        >>> standard_n = ugentools.StandardN.(
        ...     frequency=22050,
        ...     k=1,
        ...     xi=0.5,
        ...     yi=0,
        ...     )
        >>> standard_n

    '''

    ### CLASS VARIABLES ###

    __documentation_section__ = None

    __slots__ = ()

    _ordered_input_names = (
        'frequency',
        'k',
        'xi',
        'yi',
        )

    _valid_calculation_rates = None

    ### INITIALIZER ###

    def __init__(
        self,
        calculation_rate=None,
        frequency=22050,
        k=1,
        xi=0.5,
        yi=0,
        ):
        ChaosGen.__init__(
            self,
            calculation_rate=calculation_rate,
            frequency=frequency,
            k=k,
            xi=xi,
            yi=yi,
            )

    ### PUBLIC METHODS ###

    @classmethod
    def ar(
        cls,
        frequency=22050,
        k=1,
        xi=0.5,
        yi=0,
        ):
        r'''Constructs an audio-rate StandardN.

        ::

            >>> standard_n = ugentools.StandardN.ar(
            ...     frequency=22050,
            ...     k=1,
            ...     xi=0.5,
            ...     yi=0,
            ...     )
            >>> standard_n

        Returns ugen graph.
        '''
        from supriya.tools import synthdeftools
        calculation_rate = synthdeftools.CalculationRate.AUDIO
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            frequency=frequency,
            k=k,
            xi=xi,
            yi=yi,
            )
        return ugen

    # def equation(): ...

    ### PUBLIC PROPERTIES ###

    @property
    def frequency(self):
        r'''Gets `frequency` input of StandardN.

        ::

            >>> standard_n = ugentools.StandardN.ar(
            ...     frequency=22050,
            ...     k=1,
            ...     xi=0.5,
            ...     yi=0,
            ...     )
            >>> standard_n.frequency

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('frequency')
        return self._inputs[index]

    @property
    def k(self):
        r'''Gets `k` input of StandardN.

        ::

            >>> standard_n = ugentools.StandardN.ar(
            ...     frequency=22050,
            ...     k=1,
            ...     xi=0.5,
            ...     yi=0,
            ...     )
            >>> standard_n.k

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('k')
        return self._inputs[index]

    @property
    def xi(self):
        r'''Gets `xi` input of StandardN.

        ::

            >>> standard_n = ugentools.StandardN.ar(
            ...     frequency=22050,
            ...     k=1,
            ...     xi=0.5,
            ...     yi=0,
            ...     )
            >>> standard_n.xi

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('xi')
        return self._inputs[index]

    @property
    def yi(self):
        r'''Gets `yi` input of StandardN.

        ::

            >>> standard_n = ugentools.StandardN.ar(
            ...     frequency=22050,
            ...     k=1,
            ...     xi=0.5,
            ...     yi=0,
            ...     )
            >>> standard_n.yi

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('yi')
        return self._inputs[index]