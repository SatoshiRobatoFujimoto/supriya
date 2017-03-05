# -*- encoding: utf-8 -*-
import time
from patterntools_testbase import TestCase
from supriya import synthdefs
from supriya.tools import nonrealtimetools
from supriya.tools import patterntools


class TestCase(TestCase):

    pbus_01 = patterntools.Pbus(
        pattern=patterntools.Pbind(
            amplitude=1.0,
            duration=patterntools.Pseq([1.0, 2.0, 3.0], 1),
            frequency=patterntools.Pseq([440, 660, 880], 1),
            ),
        release_time=0.25,
        )

    pbus_02 = patterntools.Pbus(
        patterntools.Pmono(
            amplitude=1.0,
            duration=0.75,
            frequency=patterntools.Pseq([222, 333, 444], 1),
            ),
        )

    def test___iter___01(self):
        events = list(self.pbus_01)
        self.compare_objects_as_strings(
            events,
            '''
            supriya.tools.patterntools.CompositeEvent(
                delta=0.0,
                events=(
                    supriya.tools.patterntools.BusEvent(
                        calculation_rate=supriya.tools.synthdeftools.CalculationRate.AUDIO,
                        channel_count=2,
                        delta=0.0,
                        uuid=UUID('A'),
                        ),
                    supriya.tools.patterntools.GroupEvent(
                        delta=0.0,
                        uuid=UUID('B'),
                        ),
                    supriya.tools.patterntools.SynthEvent(
                        add_action=supriya.tools.servertools.AddAction.ADD_AFTER,
                        amplitude=1.0,
                        delta=0.0,
                        in_=UUID('A'),
                        synthdef=<supriya.tools.synthdeftools.SynthDef('454b69a7c505ddecc5b39762d291a5ec')>,
                        target_node=UUID('B'),
                        uuid=UUID('C'),
                        ),
                    ),
                )
            supriya.tools.patterntools.NoteEvent(
                amplitude=1.0,
                duration=1.0,
                frequency=440,
                is_stop=True,
                out=UUID('A'),
                target_node=UUID('B'),
                uuid=UUID('D'),
                )
            supriya.tools.patterntools.NoteEvent(
                amplitude=1.0,
                duration=2.0,
                frequency=660,
                is_stop=True,
                out=UUID('A'),
                target_node=UUID('B'),
                uuid=UUID('E'),
                )
            supriya.tools.patterntools.NoteEvent(
                amplitude=1.0,
                duration=3.0,
                frequency=880,
                is_stop=True,
                out=UUID('A'),
                target_node=UUID('B'),
                uuid=UUID('F'),
                )
            supriya.tools.patterntools.CompositeEvent(
                delta=0.0,
                events=(
                    supriya.tools.patterntools.NullEvent(
                        delta=0.25,
                        ),
                    supriya.tools.patterntools.SynthEvent(
                        delta=0.0,
                        is_stop=True,
                        uuid=UUID('C'),
                        ),
                    supriya.tools.patterntools.GroupEvent(
                        delta=0.0,
                        is_stop=True,
                        uuid=UUID('B'),
                        ),
                    supriya.tools.patterntools.BusEvent(
                        delta=0.0,
                        is_stop=True,
                        uuid=UUID('A'),
                        ),
                    ),
                is_stop=True,
                )
            ''',
            replace_uuids=True,
            )

    def test___iter___02(self):
        events = list(self.pbus_02)
        self.compare_objects_as_strings(
            events,
            '''
            supriya.tools.patterntools.CompositeEvent(
                delta=0.0,
                events=(
                    supriya.tools.patterntools.BusEvent(
                        calculation_rate=supriya.tools.synthdeftools.CalculationRate.AUDIO,
                        channel_count=2,
                        delta=0.0,
                        uuid=UUID('A'),
                        ),
                    supriya.tools.patterntools.GroupEvent(
                        delta=0.0,
                        uuid=UUID('B'),
                        ),
                    supriya.tools.patterntools.SynthEvent(
                        add_action=supriya.tools.servertools.AddAction.ADD_AFTER,
                        amplitude=1.0,
                        delta=0.0,
                        in_=UUID('A'),
                        synthdef=<supriya.tools.synthdeftools.SynthDef('454b69a7c505ddecc5b39762d291a5ec')>,
                        target_node=UUID('B'),
                        uuid=UUID('C'),
                        ),
                    ),
                )
            supriya.tools.patterntools.NoteEvent(
                amplitude=1.0,
                duration=0.75,
                frequency=222,
                out=UUID('A'),
                target_node=UUID('B'),
                uuid=UUID('D'),
                )
            supriya.tools.patterntools.NoteEvent(
                amplitude=1.0,
                duration=0.75,
                frequency=333,
                out=UUID('A'),
                target_node=UUID('B'),
                uuid=UUID('D'),
                )
            supriya.tools.patterntools.NoteEvent(
                amplitude=1.0,
                duration=0.75,
                frequency=444,
                is_stop=True,
                out=UUID('A'),
                target_node=UUID('B'),
                uuid=UUID('D'),
                )
            supriya.tools.patterntools.CompositeEvent(
                delta=0.0,
                events=(
                    supriya.tools.patterntools.NullEvent(
                        delta=0.25,
                        ),
                    supriya.tools.patterntools.SynthEvent(
                        delta=0.0,
                        is_stop=True,
                        uuid=UUID('C'),
                        ),
                    supriya.tools.patterntools.GroupEvent(
                        delta=0.0,
                        is_stop=True,
                        uuid=UUID('B'),
                        ),
                    supriya.tools.patterntools.BusEvent(
                        delta=0.0,
                        is_stop=True,
                        uuid=UUID('A'),
                        ),
                    ),
                is_stop=True,
                )
            ''',
            replace_uuids=True,
            )

    def test_send_01a(self):
        events = self.setup_send(self.pbus_01, iterations=1)
        self.compare_objects_as_strings(
            events,
            '''
            supriya.tools.patterntools.CompositeEvent(
                delta=0.0,
                events=(
                    supriya.tools.patterntools.BusEvent(
                        calculation_rate=supriya.tools.synthdeftools.CalculationRate.AUDIO,
                        channel_count=2,
                        delta=0.0,
                        uuid=UUID('A'),
                        ),
                    supriya.tools.patterntools.GroupEvent(
                        delta=0.0,
                        uuid=UUID('B'),
                        ),
                    supriya.tools.patterntools.SynthEvent(
                        add_action=supriya.tools.servertools.AddAction.ADD_AFTER,
                        amplitude=1.0,
                        delta=0.0,
                        in_=UUID('A'),
                        synthdef=<supriya.tools.synthdeftools.SynthDef('454b69a7c505ddecc5b39762d291a5ec')>,
                        target_node=UUID('B'),
                        uuid=UUID('C'),
                        ),
                    ),
                )
            supriya.tools.patterntools.CompositeEvent(
                delta=0.0,
                events=(
                    supriya.tools.patterntools.SynthEvent(
                        delta=0.0,
                        is_stop=True,
                        uuid=UUID('C'),
                        ),
                    supriya.tools.patterntools.GroupEvent(
                        delta=0.0,
                        is_stop=True,
                        uuid=UUID('B'),
                        ),
                    supriya.tools.patterntools.BusEvent(
                        delta=0.0,
                        is_stop=True,
                        uuid=UUID('A'),
                        ),
                    ),
                is_stop=True,
                )
            ''',
            replace_uuids=True,
            )

    def test_send_01b(self):
        events = self.setup_send(self.pbus_01, iterations=2)
        self.compare_objects_as_strings(
            events,
            '''
            supriya.tools.patterntools.CompositeEvent(
                delta=0.0,
                events=(
                    supriya.tools.patterntools.BusEvent(
                        calculation_rate=supriya.tools.synthdeftools.CalculationRate.AUDIO,
                        channel_count=2,
                        delta=0.0,
                        uuid=UUID('A'),
                        ),
                    supriya.tools.patterntools.GroupEvent(
                        delta=0.0,
                        uuid=UUID('B'),
                        ),
                    supriya.tools.patterntools.SynthEvent(
                        add_action=supriya.tools.servertools.AddAction.ADD_AFTER,
                        amplitude=1.0,
                        delta=0.0,
                        in_=UUID('A'),
                        synthdef=<supriya.tools.synthdeftools.SynthDef('454b69a7c505ddecc5b39762d291a5ec')>,
                        target_node=UUID('B'),
                        uuid=UUID('C'),
                        ),
                    ),
                )
            supriya.tools.patterntools.NoteEvent(
                amplitude=1.0,
                duration=1.0,
                frequency=440,
                is_stop=True,
                out=UUID('A'),
                target_node=UUID('B'),
                uuid=UUID('D'),
                )
            supriya.tools.patterntools.CompositeEvent(
                delta=0.0,
                events=(
                    supriya.tools.patterntools.NullEvent(
                        delta=0.25,
                        ),
                    supriya.tools.patterntools.SynthEvent(
                        delta=0.0,
                        is_stop=True,
                        uuid=UUID('C'),
                        ),
                    supriya.tools.patterntools.GroupEvent(
                        delta=0.0,
                        is_stop=True,
                        uuid=UUID('B'),
                        ),
                    supriya.tools.patterntools.BusEvent(
                        delta=0.0,
                        is_stop=True,
                        uuid=UUID('A'),
                        ),
                    ),
                is_stop=True,
                )
            ''',
            replace_uuids=True,
            )

    def test_send_02a(self):
        events = self.setup_send(self.pbus_02, iterations=1)
        self.compare_objects_as_strings(
            events,
            '''
            supriya.tools.patterntools.CompositeEvent(
                delta=0.0,
                events=(
                    supriya.tools.patterntools.BusEvent(
                        calculation_rate=supriya.tools.synthdeftools.CalculationRate.AUDIO,
                        channel_count=2,
                        delta=0.0,
                        uuid=UUID('A'),
                        ),
                    supriya.tools.patterntools.GroupEvent(
                        delta=0.0,
                        uuid=UUID('B'),
                        ),
                    supriya.tools.patterntools.SynthEvent(
                        add_action=supriya.tools.servertools.AddAction.ADD_AFTER,
                        amplitude=1.0,
                        delta=0.0,
                        in_=UUID('A'),
                        synthdef=<supriya.tools.synthdeftools.SynthDef('454b69a7c505ddecc5b39762d291a5ec')>,
                        target_node=UUID('B'),
                        uuid=UUID('C'),
                        ),
                    ),
                )
            supriya.tools.patterntools.CompositeEvent(
                delta=0.0,
                events=(
                    supriya.tools.patterntools.SynthEvent(
                        delta=0.0,
                        is_stop=True,
                        uuid=UUID('C'),
                        ),
                    supriya.tools.patterntools.GroupEvent(
                        delta=0.0,
                        is_stop=True,
                        uuid=UUID('B'),
                        ),
                    supriya.tools.patterntools.BusEvent(
                        delta=0.0,
                        is_stop=True,
                        uuid=UUID('A'),
                        ),
                    ),
                is_stop=True,
                )
            ''',
            replace_uuids=True,
            )

    def test_send_02b(self):
        events = self.setup_send(self.pbus_02, iterations=2)
        self.compare_objects_as_strings(
            events,
            '''
            supriya.tools.patterntools.CompositeEvent(
                delta=0.0,
                events=(
                    supriya.tools.patterntools.BusEvent(
                        calculation_rate=supriya.tools.synthdeftools.CalculationRate.AUDIO,
                        channel_count=2,
                        delta=0.0,
                        uuid=UUID('A'),
                        ),
                    supriya.tools.patterntools.GroupEvent(
                        delta=0.0,
                        uuid=UUID('B'),
                        ),
                    supriya.tools.patterntools.SynthEvent(
                        add_action=supriya.tools.servertools.AddAction.ADD_AFTER,
                        amplitude=1.0,
                        delta=0.0,
                        in_=UUID('A'),
                        synthdef=<supriya.tools.synthdeftools.SynthDef('454b69a7c505ddecc5b39762d291a5ec')>,
                        target_node=UUID('B'),
                        uuid=UUID('C'),
                        ),
                    ),
                )
            supriya.tools.patterntools.NoteEvent(
                amplitude=1.0,
                duration=0.75,
                frequency=222,
                out=UUID('A'),
                target_node=UUID('B'),
                uuid=UUID('D'),
                )
            supriya.tools.patterntools.CompositeEvent(
                delta=0.0,
                events=(
                    supriya.tools.patterntools.NullEvent(
                        delta=0.25,
                        ),
                    supriya.tools.patterntools.SynthEvent(
                        delta=0.0,
                        is_stop=True,
                        uuid=UUID('C'),
                        ),
                    supriya.tools.patterntools.GroupEvent(
                        delta=0.0,
                        is_stop=True,
                        uuid=UUID('B'),
                        ),
                    supriya.tools.patterntools.BusEvent(
                        delta=0.0,
                        is_stop=True,
                        uuid=UUID('A'),
                        ),
                    ),
                is_stop=True,
                )
            ''',
            replace_uuids=True,
            )

    def test_manual_incommunicado(self):
        lists, deltas = self.manual_incommunicado(self.pbus_01)
        assert lists == [
            [10, [
                ['/g_new', 1000, 0, 1],
                ['/s_new', '454b69a7c505ddecc5b39762d291a5ec', 1001, 3, 1000,
                    'in_', 0],
                ['/s_new', 'da0982184cc8fa54cf9d288a0fe1f6ca', 1002, 0, 1000,
                    'amplitude', 1.0, 'frequency', 440, 'out', 0]]],
            [11.0, [
                ['/n_set', 1002, 'gate', 0],
                ['/s_new', 'da0982184cc8fa54cf9d288a0fe1f6ca', 1003, 0, 1000,
                    'amplitude', 1.0, 'frequency', 660, 'out', 0]]],
            [13.0, [
                ['/n_set', 1003, 'gate', 0],
                ['/s_new', 'da0982184cc8fa54cf9d288a0fe1f6ca', 1004, 0, 1000,
                    'amplitude', 1.0, 'frequency', 880, 'out', 0]]],
            [16.0, [
                ['/n_set', 1004, 'gate', 0]]],
            [16.25, [
                ['/n_free', 1000, 1001]]]]
        assert deltas == [1.0, 2.0, 3.0, 0.25, None]

    def test_manual_communicado_pbind_01(self):
        player = patterntools.RealtimeEventPlayer(
            self.pbus_01,
            server=self.server,
            )
        # Initial State
        server_state = str(self.server.query_remote_nodes(include_controls=True))
        assert server_state == self.normalize(r'''
            NODE TREE 0 group
                1 group
        ''')
        # Step 1
        player(0, 0)
        self.server.sync()
        server_state = str(self.server.query_remote_nodes(include_controls=True))
        assert server_state == self.normalize(r'''
            NODE TREE 0 group
                1 group
                    1000 group
                        1002 da0982184cc8fa54cf9d288a0fe1f6ca
                            out: 16.0, amplitude: 1.0, frequency: 440.0, gate: 1.0, pan: 0.5
                    1001 454b69a7c505ddecc5b39762d291a5ec
                        done_action: 2.0, fade_time: 0.02, gate: 1.0, in_: 16.0, out: 0.0
        ''')
        # Step 2
        player(0, 0)
        self.server.sync()
        server_state = str(self.server.query_remote_nodes(include_controls=True))
        assert server_state == self.normalize(r'''
            NODE TREE 0 group
                1 group
                    1000 group
                        1003 da0982184cc8fa54cf9d288a0fe1f6ca
                            out: 16.0, amplitude: 1.0, frequency: 660.0, gate: 1.0, pan: 0.5
                        1002 da0982184cc8fa54cf9d288a0fe1f6ca
                            out: 16.0, amplitude: 1.0, frequency: 440.0, gate: 0.0, pan: 0.5
                    1001 454b69a7c505ddecc5b39762d291a5ec
                        done_action: 2.0, fade_time: 0.02, gate: 1.0, in_: 16.0, out: 0.0
        ''')
        # Wait for termination
        time.sleep(0.5)
        server_state = str(self.server.query_remote_nodes(include_controls=True))
        assert server_state == self.normalize(r'''
            NODE TREE 0 group
                1 group
                    1000 group
                        1003 da0982184cc8fa54cf9d288a0fe1f6ca
                            out: 16.0, amplitude: 1.0, frequency: 660.0, gate: 1.0, pan: 0.5
                    1001 454b69a7c505ddecc5b39762d291a5ec
                        done_action: 2.0, fade_time: 0.02, gate: 1.0, in_: 16.0, out: 0.0
        ''')
        # Step 3
        player(0, 0)
        self.server.sync()
        server_state = str(self.server.query_remote_nodes(include_controls=True))
        assert server_state == self.normalize(r'''
            NODE TREE 0 group
                1 group
                    1000 group
                        1004 da0982184cc8fa54cf9d288a0fe1f6ca
                            out: 16.0, amplitude: 1.0, frequency: 880.0, gate: 1.0, pan: 0.5
                        1003 da0982184cc8fa54cf9d288a0fe1f6ca
                            out: 16.0, amplitude: 1.0, frequency: 660.0, gate: 0.0, pan: 0.5
                    1001 454b69a7c505ddecc5b39762d291a5ec
                        done_action: 2.0, fade_time: 0.02, gate: 1.0, in_: 16.0, out: 0.0
        ''')
        # Wait for termination
        time.sleep(0.5)
        server_state = str(self.server.query_remote_nodes(include_controls=True))
        assert server_state == self.normalize(r'''
            NODE TREE 0 group
                1 group
                    1000 group
                        1004 da0982184cc8fa54cf9d288a0fe1f6ca
                            out: 16.0, amplitude: 1.0, frequency: 880.0, gate: 1.0, pan: 0.5
                    1001 454b69a7c505ddecc5b39762d291a5ec
                        done_action: 2.0, fade_time: 0.02, gate: 1.0, in_: 16.0, out: 0.0
        ''')
        # Step 4
        player(0, 0)
        self.server.sync()
        server_state = str(self.server.query_remote_nodes(include_controls=True))
        assert server_state == self.normalize(r'''
            NODE TREE 0 group
                1 group
                    1000 group
                        1004 da0982184cc8fa54cf9d288a0fe1f6ca
                            out: 16.0, amplitude: 1.0, frequency: 880.0, gate: 0.0, pan: 0.5
                    1001 454b69a7c505ddecc5b39762d291a5ec
                        done_action: 2.0, fade_time: 0.02, gate: 1.0, in_: 16.0, out: 0.0
        ''')
        # Wait for termination
        time.sleep(0.5)
        server_state = str(self.server.query_remote_nodes(include_controls=True))
        assert server_state == self.normalize(r'''
            NODE TREE 0 group
                1 group
                    1000 group
                    1001 454b69a7c505ddecc5b39762d291a5ec
                        done_action: 2.0, fade_time: 0.02, gate: 1.0, in_: 16.0, out: 0.0
        ''')
        # Step 4
        player(0, 0)
        self.server.sync()
        server_state = str(self.server.query_remote_nodes(include_controls=True))
        assert server_state == self.normalize(r'''
            NODE TREE 0 group
                1 group
        ''')

    def test_nonrealtime_01a(self):
        session = nonrealtimetools.Session()
        with session.at(0):
            final_offset = session.inscribe(self.pbus_01)
        d_recv_commands = []
        for synthdef in sorted(
            [synthdefs.system_link_audio_2, synthdefs.default],
            key=lambda x: x.anonymous_name,
            ):
            compiled_synthdef = bytearray(synthdef.compile())
            d_recv_commands.append(['/d_recv', compiled_synthdef])
        assert session.to_lists() == [
            [0.0, [
                *d_recv_commands,
                ['/g_new', 1000, 0, 0],
                ['/s_new', '454b69a7c505ddecc5b39762d291a5ec', 1001, 3, 1000,
                    'in_', 16],
                ['/s_new', 'da0982184cc8fa54cf9d288a0fe1f6ca', 1002, 0, 1000,
                    'amplitude', 1.0, 'frequency', 440, 'out', 16]]],
            [1.0, [
                ['/s_new', 'da0982184cc8fa54cf9d288a0fe1f6ca', 1003, 0, 1000,
                    'amplitude', 1.0, 'frequency', 660, 'out', 16],
                ['/n_set', 1002, 'gate', 0]]],
            [3.0, [
                ['/s_new', 'da0982184cc8fa54cf9d288a0fe1f6ca', 1004, 0, 1000,
                    'amplitude', 1.0, 'frequency', 880, 'out', 16],
                ['/n_set', 1003, 'gate', 0]]],
            [6.0, [['/n_set', 1004, 'gate', 0]]],
            [6.25, [['/n_free', 1000], ['/n_set', 1001, 'gate', 0], [0]]]]
        assert final_offset == 6.25

    def test_nonrealtime_01b(self):
        session = nonrealtimetools.Session()
        with session.at(0):
            final_offset = session.inscribe(self.pbus_01, duration=3)
        d_recv_commands = []
        for synthdef in sorted(
            [synthdefs.system_link_audio_2, synthdefs.default],
            key=lambda x: x.anonymous_name,
            ):
            compiled_synthdef = bytearray(synthdef.compile())
            d_recv_commands.append(['/d_recv', compiled_synthdef])
        assert session.to_lists() == [
            [0.0, [
                *d_recv_commands,
                ['/g_new', 1000, 0, 0],
                ['/s_new', '454b69a7c505ddecc5b39762d291a5ec', 1001, 3, 1000,
                    'in_', 16],
                ['/s_new', 'da0982184cc8fa54cf9d288a0fe1f6ca', 1002, 0, 1000,
                    'amplitude', 1.0, 'frequency', 440, 'out', 16]]],
            [1.0, [
                ['/s_new', 'da0982184cc8fa54cf9d288a0fe1f6ca', 1003, 0, 1000,
                    'amplitude', 1.0, 'frequency', 660, 'out', 16],
                ['/n_set', 1002, 'gate', 0]]],
            [3.0, [['/n_set', 1003, 'gate', 0]]],
            [3.25, [['/n_free', 1000], ['/n_set', 1001, 'gate', 0], [0]]]]
        assert final_offset == 3.25

    def test_nonrealtime_01c(self):
        session = nonrealtimetools.Session()
        with session.at(0):
            final_offset = session.inscribe(self.pbus_01, duration=2)
        d_recv_commands = []
        for synthdef in sorted(
            [synthdefs.system_link_audio_2, synthdefs.default],
            key=lambda x: x.anonymous_name,
            ):
            compiled_synthdef = bytearray(synthdef.compile())
            d_recv_commands.append(['/d_recv', compiled_synthdef])
        assert session.to_lists() == [
            [0.0, [
                *d_recv_commands,
                ['/g_new', 1000, 0, 0],
                ['/s_new', '454b69a7c505ddecc5b39762d291a5ec', 1001, 3, 1000,
                    'in_', 16],
                ['/s_new', 'da0982184cc8fa54cf9d288a0fe1f6ca', 1002, 0, 1000,
                    'amplitude', 1.0, 'frequency', 440, 'out', 16]]],
            [1.0, [
                ['/n_set', 1002, 'gate', 0]]],
            [1.25, [['/n_free', 1000], ['/n_set', 1001, 'gate', 0], [0]]]]
        assert final_offset == 1.25
