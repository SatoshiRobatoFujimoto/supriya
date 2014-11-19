# -*- encoding: utf-8 -*-
from supriya.tools.synthdeftools.UGen import UGen


class Convolution2L(UGen):
    r'''

    ::

        >>> convolution_2_l = ugentools.Convolution2L.(
        ...     crossfade=1,
        ...     framesize=2048,
        ...     kernel=None,
        ...     source=None,
        ...     trigger=0,
        ...     )
        >>> convolution_2_l

    '''

    ### CLASS VARIABLES ###

    __documentation_section__ = None

    __slots__ = ()

    _ordered_input_names = (
        'source',
        'kernel',
        'trigger',
        'framesize',
        'crossfade',
        )

    _valid_calculation_rates = None

    ### INITIALIZER ###

    def __init__(
        self,
        calculation_rate=None,
        crossfade=1,
        framesize=2048,
        kernel=None,
        source=None,
        trigger=0,
        ):
        UGen.__init__(
            self,
            calculation_rate=calculation_rate,
            crossfade=crossfade,
            framesize=framesize,
            kernel=kernel,
            source=source,
            trigger=trigger,
            )

    ### PUBLIC METHODS ###

    @classmethod
    def ar(
        cls,
        crossfade=1,
        framesize=2048,
        kernel=None,
        source=None,
        trigger=0,
        ):
        r'''Constructs an audio-rate Convolution2L.

        ::

            >>> convolution_2_l = ugentools.Convolution2L.ar(
            ...     crossfade=1,
            ...     framesize=2048,
            ...     kernel=None,
            ...     source=None,
            ...     trigger=0,
            ...     )
            >>> convolution_2_l

        Returns ugen graph.
        '''
        from supriya.tools import synthdeftools
        calculation_rate = synthdeftools.CalculationRate.AUDIO
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            crossfade=crossfade,
            framesize=framesize,
            kernel=kernel,
            source=source,
            trigger=trigger,
            )
        return ugen

    ### PUBLIC PROPERTIES ###

    @property
    def source(self):
        r'''Gets `source` input of Convolution2L.

        ::

            >>> convolution_2_l = ugentools.Convolution2L.ar(
            ...     crossfade=1,
            ...     framesize=2048,
            ...     kernel=None,
            ...     source=None,
            ...     trigger=0,
            ...     )
            >>> convolution_2_l.source

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('source')
        return self._inputs[index]

    @property
    def kernel(self):
        r'''Gets `kernel` input of Convolution2L.

        ::

            >>> convolution_2_l = ugentools.Convolution2L.ar(
            ...     crossfade=1,
            ...     framesize=2048,
            ...     kernel=None,
            ...     source=None,
            ...     trigger=0,
            ...     )
            >>> convolution_2_l.kernel

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('kernel')
        return self._inputs[index]

    @property
    def trigger(self):
        r'''Gets `trigger` input of Convolution2L.

        ::

            >>> convolution_2_l = ugentools.Convolution2L.ar(
            ...     crossfade=1,
            ...     framesize=2048,
            ...     kernel=None,
            ...     source=None,
            ...     trigger=0,
            ...     )
            >>> convolution_2_l.trigger

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('trigger')
        return self._inputs[index]

    @property
    def framesize(self):
        r'''Gets `framesize` input of Convolution2L.

        ::

            >>> convolution_2_l = ugentools.Convolution2L.ar(
            ...     crossfade=1,
            ...     framesize=2048,
            ...     kernel=None,
            ...     source=None,
            ...     trigger=0,
            ...     )
            >>> convolution_2_l.framesize

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('framesize')
        return self._inputs[index]

    @property
    def crossfade(self):
        r'''Gets `crossfade` input of Convolution2L.

        ::

            >>> convolution_2_l = ugentools.Convolution2L.ar(
            ...     crossfade=1,
            ...     framesize=2048,
            ...     kernel=None,
            ...     source=None,
            ...     trigger=0,
            ...     )
            >>> convolution_2_l.crossfade

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('crossfade')
        return self._inputs[index]