# -*- encoding: utf-8 -*-
import bisect
from abjad.tools import timespantools
from supriya.tools import requesttools
from supriya.tools import servertools
from supriya.tools import synthdeftools
from supriya.tools.nonrealtimetools.SessionObject import SessionObject


class Synth(timespantools.Timespan, SessionObject):
    '''
    A non-realtime Synth.
    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        '_add_action',
        '_events',
        '_session',
        '_synth_kwargs',
        '_synthdef',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        session,
        start_offset=None,
        stop_offset=None,
        synthdef=None,
        add_action=None,
        **synth_kwargs
        ):
        from supriya.tools import servertools
        timespantools.Timespan.__init__(
            self,
            start_offset=start_offset,
            stop_offset=stop_offset,
            )
        SessionObject.__init__(self, session)
        if add_action is None:
            add_action = servertools.AddAction.ADD_TO_HEAD
        assert add_action in (
            servertools.AddAction.ADD_TO_HEAD,
            servertools.AddAction.ADD_TO_TAIL,
            )
        self._add_action = add_action
        self._events = {}
        assert isinstance(synthdef, synthdeftools.SynthDef)
        self._synthdef = synthdef
        self._synth_kwargs = synth_kwargs.copy()

    ### SPECIAL METHODS ###

    def __getitem__(self, item):
        from supriya.tools import nonrealtimetools
        assert self.session._session_moments
        timestep = self.session._session_moments[-1].timestep
        return self._get_at_timestep(timestep, item)

    def __setitem__(self, item, value):
        from supriya.tools import nonrealtimetools
        assert self.session._session_moments
        timestep = self.session._session_moments[-1].timestep
        assert isinstance(value, (int, float, nonrealtimetools.Bus, nonrealtimetools.BusGroup))
        self._set_at_timestep(timestep, item, value)

    ### PRIVATE METHODS ###

    def _collect_requests(self, id_mapping):
        from supriya.tools import nonrealtimetools
        node_id = id_mapping[self]
        target_node_id = 0
        events_by_timestep = {}
        events_by_timestep[self.start_offset] = self.synth_kwargs.copy()
        for item, events in self._events.items():
            for timestep, value in events:
                timestep += self.start_offset
                event = events_by_timestep.setdefault(timestep, {})
                event[item] = value
        bus_prototype = (
            nonrealtimetools.Bus, 
            nonrealtimetools.BusGroup, 
            type(None),
            )
        for timestep, event in tuple(events_by_timestep.items()):
            settings = {}
            a_mappings = {}
            c_mappings = {}
            for key, value in event.items():
                if isinstance(value, bus_prototype):
                    if value.calculation_rate == \
                        synthdeftools.CalculationRate.AUDIO:
                        a_mappings[key] = value
                    else:
                        c_mappings[key] = value
                else:
                    settings[key] = value
            requests = []
            if timestep == self.start_offset:
                if ('duration' in self.synthdef.parameter_names and
                    'duration' not in settings):
                    settings['duration'] = float(self.duration)
                request = requesttools.SynthNewRequest(
                    add_action=self.add_action,
                    node_id=node_id,
                    synthdef=self.synthdef.anonymous_name,
                    target_node_id=target_node_id,
                    **settings
                    )
                requests.append(request)
            else:
                request = requesttools.NodeSetRequest(
                    node_id=node_id,
                    **settings
                    )
                requests.append(request)
            if a_mappings:
                request = requesttools.NodeMapToAudioBusRequest(
                    node_id=node_id,
                    **a_mappings
                    )
                requests.append(request)
            if c_mappings:
                request = requesttools.NodeMapToControlBusRequest(
                    node_id=node_id,
                    **c_mappings
                    )
                requests.append(request)
            events_by_timestep[timestep] = requests
        if 'gate' in self.synthdef.parameter_names:
            end_request = requesttools.NodeSetRequest(node_id=node_id, gate=0)
        else:
            end_request = requesttools.NodeFreeRequest(node_ids=[node_id])
        events_by_timestep.setdefault(self.stop_offset, []).append(end_request)
        return events_by_timestep

    def _get_start_request(self, mapping):
        node_id = mapping[self]
        target_node_id = 0
        parameter_names = self.synthdef.parameter_names
        synth_kwargs = self.synth_kwargs
        if 'duration' in parameter_names and 'duration' not in synth_kwargs:
            synth_kwargs['duration'] = float(self.duration)
        request = requesttools.SynthNewRequest(
            add_action=servertools.AddAction.ADD_TO_TAIL,
            node_id=node_id,
            synthdef=self.synthdef.anonymous_name,
            target_node_id=target_node_id,
            **synth_kwargs
            )
        return request

    def _get_at_timestep(self, timestep, item):
        '''
        Relative to Synth start offset.
        '''
        timestep -= self.start_offset
        events = self._events.get(item)
        default = self.synthdef.parameters[item].value
        default = self._synth_kwargs.get(item, default)
        if not events:
            return default
        index = bisect.bisect_left(events, (timestep, 0.))
        if len(events) <= index:
            old_timestep, value = events[-1]
        else:
            old_timestep, value = events[index]
        if old_timestep == timestep:
            return value
        index -= 1
        if index < 0:
            return default
        _, value = events[index]
        return value

    def _set_at_timestep(self, timestep, item, value):
        '''
        Relative to Synth start offset.
        '''
        timestep -= self.start_offset
        if timestep < 0 or self.duration < timestep:
            return
        events = self._events.setdefault(item, [])
        new_event = (timestep, value)
        if not events:
            events.append(new_event)
            return
        index = bisect.bisect_left(events, new_event)
        if len(events) <= index:
            events.append(new_event)
        old_timestep, old_value = events[index]
        if old_timestep == timestep:
            events[index] = (timestep, value)
        else:
            events.insert(index, new_event)

    ### PUBLIC PROPERTIES ###

    @property
    def add_action(self):
        return self._add_action

    @property
    def session(self):
        return self._session

    @property
    def synth_kwargs(self):
        return self._synth_kwargs.copy()

    @property
    def synthdef(self):
        return self._synthdef
