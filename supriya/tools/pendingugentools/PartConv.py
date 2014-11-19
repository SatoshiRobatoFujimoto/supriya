# -*- encoding: utf-8 -*-
from supriya.tools.synthdeftools.UGen import UGen


class PartConv(UGen):
    r'''

    ::

        >>> part_conv = ugentools.PartConv.(
        ...     fftsize=None,
        ...     irbufnum=None,
        ...     source=None,
        ...     )
        >>> part_conv

    '''

    ### CLASS VARIABLES ###

    __documentation_section__ = None

    __slots__ = ()

    _ordered_input_names = (
        'source',
        'fftsize',
        'irbufnum',
        )

    _valid_calculation_rates = None

    ### INITIALIZER ###

    def __init__(
        self,
        calculation_rate=None,
        fftsize=None,
        irbufnum=None,
        source=None,
        ):
        UGen.__init__(
            self,
            calculation_rate=calculation_rate,
            fftsize=fftsize,
            irbufnum=irbufnum,
            source=source,
            )

    ### PUBLIC METHODS ###

    @classmethod
    def ar(
        cls,
        fftsize=None,
        irbufnum=None,
        source=None,
        ):
        r'''Constructs an audio-rate PartConv.

        ::

            >>> part_conv = ugentools.PartConv.ar(
            ...     fftsize=None,
            ...     irbufnum=None,
            ...     source=None,
            ...     )
            >>> part_conv

        Returns ugen graph.
        '''
        from supriya.tools import synthdeftools
        calculation_rate = synthdeftools.CalculationRate.AUDIO
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            fftsize=fftsize,
            irbufnum=irbufnum,
            source=source,
            )
        return ugen

    # def calcBufSize(): ...

    # def calcNumPartitions(): ...

    ### PUBLIC PROPERTIES ###

    @property
    def source(self):
        r'''Gets `source` input of PartConv.

        ::

            >>> part_conv = ugentools.PartConv.ar(
            ...     fftsize=None,
            ...     irbufnum=None,
            ...     source=None,
            ...     )
            >>> part_conv.source

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('source')
        return self._inputs[index]

    @property
    def fftsize(self):
        r'''Gets `fftsize` input of PartConv.

        ::

            >>> part_conv = ugentools.PartConv.ar(
            ...     fftsize=None,
            ...     irbufnum=None,
            ...     source=None,
            ...     )
            >>> part_conv.fftsize

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('fftsize')
        return self._inputs[index]

    @property
    def irbufnum(self):
        r'''Gets `irbufnum` input of PartConv.

        ::

            >>> part_conv = ugentools.PartConv.ar(
            ...     fftsize=None,
            ...     irbufnum=None,
            ...     source=None,
            ...     )
            >>> part_conv.irbufnum

        Returns ugen input.
        '''
        index = self._ordered_input_names.index('irbufnum')
        return self._inputs[index]