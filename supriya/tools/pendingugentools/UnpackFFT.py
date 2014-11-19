# -*- encoding: utf-8 -*-
from supriya.tools.ugentools.MultiOutUGen import MultiOutUGen


class UnpackFFT(MultiOutUGen):
    r'''

    ::

        >>> unpack_fft = ugentools.UnpackFFT.(
        ...     )
        >>> unpack_fft

    '''

    ### CLASS VARIABLES ###

    __documentation_section__ = None

    __slots__ = ()

    _ordered_input_names = ()

    _valid_calculation_rates = None

    ### INITIALIZER ###

    ### PUBLIC METHODS ###

    @classmethod
    def new(
        cls,
        bufsize=None,
        chain=None,
        frombin=0,
        tobin=None,
        ):
        r'''Constructs a UnpackFFT.

        ::

            >>> unpack_fft = ugentools.UnpackFFT.new(
            ...     bufsize=None,
            ...     chain=None,
            ...     frombin=0,
            ...     tobin=None,
            ...     )
            >>> unpack_fft

        Returns ugen graph.
        '''
        from supriya.tools import synthdeftools
        calculation_rate = None
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            bufsize=bufsize,
            chain=chain,
            frombin=frombin,
            tobin=tobin,
            )
        return ugen

    # def newFromDesc(): ...
