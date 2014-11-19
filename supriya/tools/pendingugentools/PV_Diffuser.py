# -*- encoding: utf-8 -*-
from supriya.tools.ugentools.PV_ChainUGen import PV_ChainUGen


class PV_Diffuser(PV_ChainUGen):
    r'''

    ::

        >>> pv_diffuser = ugentools.PV_Diffuser.(
        ...     )
        >>> pv_diffuser

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
        buffer_=None,
        trigger=0,
        ):
        r'''Constructs a PV_Diffuser.

        ::

            >>> pv_diffuser = ugentools.PV_Diffuser.new(
            ...     buffer_=None,
            ...     trigger=0,
            ...     )
            >>> pv_diffuser

        Returns ugen graph.
        '''
        from supriya.tools import synthdeftools
        calculation_rate = None
        ugen = cls._new_expanded(
            calculation_rate=calculation_rate,
            buffer_=buffer_,
            trigger=trigger,
            )
        return ugen
