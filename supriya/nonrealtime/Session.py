import bisect
import collections
import os
import pathlib
from queue import PriorityQueue

import uqbar.io

import supriya.commands
import supriya.osc
import supriya.realtime
import supriya.soundfiles
import supriya.synthdefs
import supriya.time
from supriya import HeaderFormat, SampleFormat
from supriya.commands import (
    BufferCopyRequest,
    BufferFillRequest,
    BufferGenerateRequest,
    BufferNormalizeRequest,
    BufferReadChannelRequest,
    BufferReadRequest,
    BufferSetContiguousRequest,
    BufferSetRequest,
    BufferWriteRequest,
    BufferZeroRequest,
    NothingRequest,
    RequestBundle,
)
from supriya.nonrealtime.SessionObject import SessionObject
from supriya.nonrealtime.Synth import Synth
from supriya.utils import iterate_nwise


class Session:
    """
    A non-realtime session.

    ::

        >>> import supriya.nonrealtime
        >>> session = supriya.nonrealtime.Session()

    ::

        >>> import supriya.synthdefs
        >>> import supriya.ugens
        >>> builder = supriya.synthdefs.SynthDefBuilder(frequency=440)
        >>> with builder:
        ...     out = supriya.ugens.Out.ar(
        ...         source=supriya.ugens.SinOsc.ar(
        ...             frequency=builder['frequency'],
        ...             )
        ...         )
        ...
        >>> synthdef = builder.build()

    ::

        >>> with session.at(0):
        ...     synth_a = session.add_synth(duration=10, synthdef=synthdef)
        ...     synth_b = session.add_synth(duration=15, synthdef=synthdef)
        ...
        >>> with session.at(5):
        ...     synth_c = session.add_synth(duration=10, synthdef=synthdef)
        ...

    ::

        >>> result = session.to_lists(duration=20)
        >>> result == [
        ...     [0.0, [
        ...         ['/d_recv', bytearray(synthdef.compile(use_anonymous_name=True))],
        ...         ['/s_new', '9c4eb4778dc0faf39459fa8a5cd45c19', 1000, 0, 0],
        ...         ['/s_new', '9c4eb4778dc0faf39459fa8a5cd45c19', 1001, 0, 0]]],
        ...     [5.0, [['/s_new', '9c4eb4778dc0faf39459fa8a5cd45c19', 1002, 0, 0]]],
        ...     [10.0, [['/n_free', 1000]]],
        ...     [15.0, [['/n_free', 1001, 1002]]],
        ...     [20.0, [[0]]],
        ... ]
        True

    """

    ### CLASS VARIABLES ###

    __documentation_section__ = "Non-realtime Session"

    __is_terminal_ajv_list_item__ = True

    __slots__ = (
        "_active_moments",
        "_audio_input_bus_group",
        "_audio_output_bus_group",
        "_buffers",
        "_buses",
        "_input",
        "_name",
        "_nodes",
        "_offsets",
        "_options",
        "_padding",
        "_root_node",
        "_session_ids",
        "_states",
        "_transcript",
    )

    _ordered_buffer_post_alloc_request_types = (
        BufferReadRequest,
        BufferReadChannelRequest,
        BufferZeroRequest,
        BufferFillRequest,
        BufferGenerateRequest,
        BufferSetRequest,
        BufferSetContiguousRequest,
        BufferNormalizeRequest,
        BufferCopyRequest,
    )

    _ordered_buffer_pre_free_request_types = (
        BufferWriteRequest,
        # supriya.commands.BufferCloseRequest,  # should be automatic
    )

    ### INITIALIZER ###

    def __init__(
        self,
        input_bus_channel_count=None,
        output_bus_channel_count=None,
        input_=None,
        name=None,
        padding=None,
        **kwargs,
    ):
        import supriya.nonrealtime

        self._options = supriya.realtime.ServerOptions(
            input_bus_channel_count=input_bus_channel_count,
            output_bus_channel_count=output_bus_channel_count,
        )
        self._active_moments = []
        self._buffers = supriya.time.TimespanCollection(accelerated=True)
        self._name = name
        self._nodes = supriya.time.TimespanCollection(accelerated=True)
        self._offsets = []
        self._root_node = supriya.nonrealtime.RootNode(self)
        self._session_ids = {}
        self._states = {}
        self._transcript = None
        if input_ and not self.is_session_like(input_):
            input_ = str(input_)
        self._input = input_
        if padding is not None:
            padding = float(padding)
        self._padding = padding
        self._setup_initial_states()
        self._setup_buses()

    ### SPECIAL METHODS ###

    def __graph__(self):
        """
        Graphs session.

        TODO: Get graphviz to respect node order or reimplement as pure SVG.

        ::

            >>> session = supriya.Session()
            >>> with session.at(0):
            ...     group = session.add_group()
            ...     synth_a = group.add_synth(duration=15)
            ...
            >>> with session.at(5):
            ...     synth_b = group.add_synth(duration=15)
            ...     synth_c = group.add_synth(duration=5)
            ...
            >>> with session.at(7.5):
            ...     synth_d = synth_b.add_synth(duration=5, add_action='ADD_BEFORE')
            ...
            >>> with session.at(11):
            ...     _ = synth_d.move_node(synth_a, add_action='ADD_AFTER')
            ...
            >>> supriya.graph(session)  # doctest: +SKIP

        ::

            >>> graphviz_graph = session.__graph__()
            >>> print(format(graphviz_graph, 'graphviz'))
            digraph G {
                graph [bgcolor=transparent,
                    fontname=Arial,
                    penwidth=2,
                    rankdir=LR,
                    ranksep=1.5];
                node [fontname=Arial,
                    fontsize=12,
                    penwidth=2,
                    shape=Mrecord,
                    style="filled, rounded"];
                edge [penwidth=2];
                subgraph cluster_0 {
                    graph [label="[-inf]",
                        style="solid, rounded"];
                }
                subgraph cluster_1 {
                    graph [label="[0.0]",
                        style="solid, rounded"];
                    subgraph cluster_1_0 {
                        graph [label="1000",
                            style="dashed, rounded"];
                        node_1_0_0 [label="{ { <f_0_0_0> [1001] | <f_0_0_1> default | <f_0_0_2> amplitude: 0.1 | <f_0_0_3> frequency: 440.0 | <f_0_0_4> gate: 1.0 | <f_0_0_5> out: 0.0 | <f_0_0_6> pan: 0.5 } }"];
                    }
                }
                subgraph cluster_2 {
                    graph [label="[5.0]",
                        style="solid, rounded"];
                    subgraph cluster_2_0 {
                        graph [label="1000",
                            style="dashed, rounded"];
                        node_2_0_0 [label="{ { <f_0_0_0> [1003] | <f_0_0_1> default | <f_0_0_2> amplitude: 0.1 | <f_0_0_3> frequency: 440.0 | <f_0_0_4> gate: 1.0 | <f_0_0_5> out: 0.0 | <f_0_0_6> pan: 0.5 } }"];
                        node_2_0_1 [label="{ { <f_0_0_0> [1002] | <f_0_0_1> default | <f_0_0_2> amplitude: 0.1 | <f_0_0_3> frequency: 440.0 | <f_0_0_4> gate: 1.0 | <f_0_0_5> out: 0.0 | <f_0_0_6> pan: 0.5 } }"];
                        node_2_0_2 [label="{ { <f_0_0_0> [1001] | <f_0_0_1> default | <f_0_0_2> amplitude: 0.1 | <f_0_0_3> frequency: 440.0 | <f_0_0_4> gate: 1.0 | <f_0_0_5> out: 0.0 | <f_0_0_6> pan: 0.5 } }"];
                        node_2_0_0 -> node_2_0_1;
                        node_2_0_1 -> node_2_0_2;
                    }
                }
                subgraph cluster_3 {
                    graph [label="[7.5]",
                        style="solid, rounded"];
                    subgraph cluster_3_0 {
                        graph [label="1000",
                            style="dashed, rounded"];
                        node_3_0_0 [label="{ { <f_0_0_0> [1003] | <f_0_0_1> default | <f_0_0_2> amplitude: 0.1 | <f_0_0_3> frequency: 440.0 | <f_0_0_4> gate: 1.0 | <f_0_0_5> out: 0.0 | <f_0_0_6> pan: 0.5 } }"];
                        node_3_0_1 [label="{ { <f_0_0_0> [1004] | <f_0_0_1> default | <f_0_0_2> amplitude: 0.1 | <f_0_0_3> frequency: 440.0 | <f_0_0_4> gate: 1.0 | <f_0_0_5> out: 0.0 | <f_0_0_6> pan: 0.5 } }"];
                        node_3_0_2 [label="{ { <f_0_0_0> [1002] | <f_0_0_1> default | <f_0_0_2> amplitude: 0.1 | <f_0_0_3> frequency: 440.0 | <f_0_0_4> gate: 1.0 | <f_0_0_5> out: 0.0 | <f_0_0_6> pan: 0.5 } }"];
                        node_3_0_3 [label="{ { <f_0_0_0> [1001] | <f_0_0_1> default | <f_0_0_2> amplitude: 0.1 | <f_0_0_3> frequency: 440.0 | <f_0_0_4> gate: 1.0 | <f_0_0_5> out: 0.0 | <f_0_0_6> pan: 0.5 } }"];
                        node_3_0_0 -> node_3_0_1;
                        node_3_0_1 -> node_3_0_2;
                        node_3_0_2 -> node_3_0_3;
                    }
                }
                subgraph cluster_4 {
                    graph [label="[10.0]",
                        style="solid, rounded"];
                    subgraph cluster_4_0 {
                        graph [label="1000",
                            style="dashed, rounded"];
                        node_4_0_0 [label="{ { <f_0_0_0> [1004] | <f_0_0_1> default | <f_0_0_2> amplitude: 0.1 | <f_0_0_3> frequency: 440.0 | <f_0_0_4> gate: 1.0 | <f_0_0_5> out: 0.0 | <f_0_0_6> pan: 0.5 } }"];
                        node_4_0_1 [label="{ { <f_0_0_0> [1002] | <f_0_0_1> default | <f_0_0_2> amplitude: 0.1 | <f_0_0_3> frequency: 440.0 | <f_0_0_4> gate: 1.0 | <f_0_0_5> out: 0.0 | <f_0_0_6> pan: 0.5 } }"];
                        node_4_0_2 [label="{ { <f_0_0_0> [1001] | <f_0_0_1> default | <f_0_0_2> amplitude: 0.1 | <f_0_0_3> frequency: 440.0 | <f_0_0_4> gate: 1.0 | <f_0_0_5> out: 0.0 | <f_0_0_6> pan: 0.5 } }"];
                        node_4_0_0 -> node_4_0_1;
                        node_4_0_1 -> node_4_0_2;
                    }
                }
                subgraph cluster_5 {
                    graph [label="[11.0]",
                        style="solid, rounded"];
                    subgraph cluster_5_0 {
                        graph [label="1000",
                            style="dashed, rounded"];
                        node_5_0_0 [label="{ { <f_0_0_0> [1004] | <f_0_0_1> default | <f_0_0_2> amplitude: 0.1 | <f_0_0_3> frequency: 440.0 | <f_0_0_4> gate: 1.0 | <f_0_0_5> out: 0.0 | <f_0_0_6> pan: 0.5 } }"];
                        node_5_0_1 [label="{ { <f_0_0_0> [1001] | <f_0_0_1> default | <f_0_0_2> amplitude: 0.1 | <f_0_0_3> frequency: 440.0 | <f_0_0_4> gate: 1.0 | <f_0_0_5> out: 0.0 | <f_0_0_6> pan: 0.5 } }"];
                        node_5_0_2 [label="{ { <f_0_0_0> [1002] | <f_0_0_1> default | <f_0_0_2> amplitude: 0.1 | <f_0_0_3> frequency: 440.0 | <f_0_0_4> gate: 1.0 | <f_0_0_5> out: 0.0 | <f_0_0_6> pan: 0.5 } }"];
                        node_5_0_0 -> node_5_0_1;
                        node_5_0_1 -> node_5_0_2;
                    }
                }
                subgraph cluster_6 {
                    graph [label="[12.5]",
                        style="solid, rounded"];
                    subgraph cluster_6_0 {
                        graph [label="1000",
                            style="dashed, rounded"];
                        node_6_0_0 [label="{ { <f_0_0_0> [1001] | <f_0_0_1> default | <f_0_0_2> amplitude: 0.1 | <f_0_0_3> frequency: 440.0 | <f_0_0_4> gate: 1.0 | <f_0_0_5> out: 0.0 | <f_0_0_6> pan: 0.5 } }"];
                        node_6_0_1 [label="{ { <f_0_0_0> [1002] | <f_0_0_1> default | <f_0_0_2> amplitude: 0.1 | <f_0_0_3> frequency: 440.0 | <f_0_0_4> gate: 1.0 | <f_0_0_5> out: 0.0 | <f_0_0_6> pan: 0.5 } }"];
                        node_6_0_0 -> node_6_0_1;
                    }
                }
                subgraph cluster_7 {
                    graph [label="[15.0]",
                        style="solid, rounded"];
                    subgraph cluster_7_0 {
                        graph [label="1000",
                            style="dashed, rounded"];
                        node_7_0_0 [label="{ { <f_0_0_0> [1002] | <f_0_0_1> default | <f_0_0_2> amplitude: 0.1 | <f_0_0_3> frequency: 440.0 | <f_0_0_4> gate: 1.0 | <f_0_0_5> out: 0.0 | <f_0_0_6> pan: 0.5 } }"];
                    }
                }
                subgraph cluster_8 {
                    graph [label="[20.0]",
                        style="solid, rounded"];
                    subgraph cluster_8_0 {
                        graph [label="1000",
                            style="dashed, rounded"];
                    }
                }
                subgraph cluster_9 {
                    graph [label="[inf]",
                        style="solid, rounded"];
                }
                node_1_0_0:f_0_0_0 -> node_2_0_2:f_0_0_0;
                node_2_0_0:f_0_0_0 -> node_3_0_0:f_0_0_0;
                node_2_0_1:f_0_0_0 -> node_3_0_2:f_0_0_0;
                node_2_0_2:f_0_0_0 -> node_3_0_3:f_0_0_0;
                node_3_0_1:f_0_0_0 -> node_4_0_0:f_0_0_0;
                node_3_0_2:f_0_0_0 -> node_4_0_1:f_0_0_0;
                node_3_0_3:f_0_0_0 -> node_4_0_2:f_0_0_0;
                node_4_0_0:f_0_0_0 -> node_5_0_0:f_0_0_0;
                node_4_0_1:f_0_0_0 -> node_5_0_2:f_0_0_0;
                node_4_0_2:f_0_0_0 -> node_5_0_1:f_0_0_0;
                node_5_0_1:f_0_0_0 -> node_6_0_0:f_0_0_0;
                node_5_0_2:f_0_0_0 -> node_6_0_1:f_0_0_0;
                node_6_0_1:f_0_0_0 -> node_7_0_0:f_0_0_0;
            }

        """
        node_mappings = []
        graph = uqbar.graphs.Graph(
            attributes={
                "bgcolor": "transparent",
                "fontname": "Arial",
                "penwidth": 2,
                "rankdir": "LR",
                "ranksep": 1.5,
            },
            edge_attributes={"penwidth": 2},
            node_attributes={
                "fontname": "Arial",
                "fontsize": 12,
                "penwidth": 2,
                "shape": "Mrecord",
                "style": ["filled", "rounded"],
            },
        )
        for offset, state in sorted(self.states.items()):
            cluster, node_mapping, _ = state._as_graphviz_graph()
            cluster.attributes.update(
                label="[{}]".format(offset), style=["solid", "rounded"]
            )
            graph.append(cluster)
            node_mappings.append(node_mapping)
        for first_mapping, second_mapping in iterate_nwise(node_mappings):
            for nrt_node, graphviz_node_one in first_mapping.items():
                if not isinstance(nrt_node, Synth):
                    continue
                graphviz_node_two = second_mapping.get(nrt_node)
                if graphviz_node_two is None:
                    continue
                graphviz_node_one["session_id"].attach(graphviz_node_two["session_id"])
        return graph

    def __render__(self, output_file_path=None, render_directory_path=None, **kwargs):
        exit_code, output_file_path = self.render(
            output_file_path=output_file_path,
            render_directory_path=render_directory_path,
            **kwargs,
        )
        return output_file_path

    def __repr__(self):
        return "<{}>".format(type(self).__name__)

    def __session__(self):
        return self

    ### PRIVATE METHODS ###

    def _add_state_at(self, offset):
        old_state = self._find_state_before(offset)
        state = old_state._clone(offset)
        self.states[offset] = state
        self.offsets.insert(self.offsets.index(old_state.offset) + 1, offset)
        return state

    def _apply_transitions(self, offsets, chain=True):
        import supriya.nonrealtime

        if supriya.nonrealtime.DoNotPropagate._stack:
            return
        queue = PriorityQueue()
        try:
            for offset in offsets:
                queue.put(offset)
        except TypeError:
            queue.put(offsets)
        previous_offset = None
        while not queue.empty():
            offset = queue.get()
            if offset == previous_offset:
                continue
            previous_offset = offset
            state = self._find_state_at(offset, clone_if_missing=False)
            if state is None:
                continue
            previous_state = self._find_state_before(offset, with_node_tree=True)
            assert previous_state is not None
            result = supriya.nonrealtime.State._apply_transitions(
                state.transitions,
                previous_state.nodes_to_children,
                previous_state.nodes_to_parents,
                state.stop_nodes,
            )
            nodes_to_children, nodes_to_parents = result
            changed = False
            if nodes_to_children != state.nodes_to_children:
                state._nodes_to_children = nodes_to_children
                state._nodes_to_parents = nodes_to_parents
                changed = True
            if changed and chain:
                next_state = self._find_state_after(offset, with_node_tree=True)
                if next_state is not None:
                    queue.put(next_state.offset)

    def _build_id_mapping(self):
        id_mapping = {}
        id_mapping.update(self._build_id_mapping_for_buffers())
        id_mapping.update(self._build_id_mapping_for_buses())
        id_mapping.update(self._build_id_mapping_for_nodes())
        return id_mapping

    def _build_id_mapping_for_buffers(self):
        mapping = {}
        for buffer_ in self._buffers:
            if buffer_ in mapping:
                continue
            if buffer_.buffer_group is None:
                mapping[buffer_] = buffer_.session_id
            else:
                initial_id = buffer_.buffer_group[0].session_id
                mapping[buffer_.buffer_group] = initial_id
                for child in buffer_.buffer_group:
                    mapping[child] = child.session_id
        return mapping

    def _build_id_mapping_for_buses(self):
        input_count = self._options._input_bus_channel_count
        output_count = self._options._output_bus_channel_count
        first_private_bus_id = input_count + output_count
        allocators = {
            supriya.CalculationRate.AUDIO: supriya.realtime.BlockAllocator(
                heap_minimum=first_private_bus_id
            ),
            supriya.CalculationRate.CONTROL: supriya.realtime.BlockAllocator(),
        }
        mapping = {}
        if output_count:
            bus_group = self.audio_output_bus_group
            mapping[bus_group] = 0
            for bus_id, bus in enumerate(bus_group):
                mapping[bus] = bus_id
        if input_count:
            bus_group = self.audio_input_bus_group
            mapping[bus_group] = output_count
            for bus_id, bus in enumerate(bus_group, output_count):
                mapping[bus] = bus_id
        for bus in self._buses:
            if bus in mapping or bus.bus_group in mapping:
                continue
            allocator = allocators[bus.calculation_rate]
            if bus.bus_group is None:
                mapping[bus] = allocator.allocate(1)
            else:
                block_id = allocator.allocate(len(bus.bus_group))
                mapping[bus.bus_group] = block_id
                for bus_id in range(block_id, block_id + len(bus.bus_group)):
                    mapping[bus] = bus_id
        return mapping

    def _build_id_mapping_for_nodes(self):
        allocator = supriya.realtime.NodeIdAllocator()
        mapping = {self.root_node: 0}
        for offset in self.offsets[1:]:
            state = self.states[offset]
            nodes = sorted(state.start_nodes, key=lambda x: x.session_id)
            for node in nodes:
                mapping[node] = allocator.allocate_node_id()
                mapping[node] = node.session_id
        return mapping

    @staticmethod
    def _build_rand_seed_synthdef():
        import supriya.ugens
        from supriya import SynthDefBuilder

        with SynthDefBuilder(rand_id=0, rand_seed=0) as builder:
            supriya.ugens.RandID.ir(rand_id=builder["rand_id"])
            supriya.ugens.RandSeed.ir(seed=builder["rand_seed"], trigger=1)
            supriya.ugens.FreeSelf.kr(trigger=1)
        return builder.build()

    def _build_render_command(
        self,
        output_filename,
        input_file_path=None,
        server_options=None,
        sample_rate=44100,
        header_format=HeaderFormat.AIFF,
        sample_format=SampleFormat.INT24,
    ):
        """
        Builds non-realtime rendering command.

        ::

            >>> import supriya.nonrealtime
            >>> session = supriya.nonrealtime.Session()
            >>> session._build_render_command('output.aiff')
            'scsynth -N {} _ output.aiff 44100 aiff int24'

        """
        server_options = server_options or supriya.realtime.ServerOptions()
        scsynth_path = "scsynth"
        if not uqbar.io.find_executable(scsynth_path):
            raise RuntimeError("Cannot find scsynth")
        parts = [scsynth_path, "-N", "{}"]
        if input_file_path:
            parts.append(os.path.expanduser(input_file_path))
        else:
            parts.append("_")
        parts.append(os.path.expanduser(output_filename))
        parts.append(str(int(sample_rate)))
        header_format = HeaderFormat.from_expr(header_format)
        parts.append(header_format.name.lower())  # Must be lowercase.
        sample_format = SampleFormat.from_expr(sample_format)
        parts.append(sample_format.name.lower())  # Must be lowercase.
        server_options = server_options.as_options_string(realtime=False)
        if server_options:
            parts.append(server_options)
        command = " ".join(parts)
        return command

    def _collect_bus_set_requests(self, bus_settings, offset):
        requests = []
        if offset in bus_settings:
            index_value_pairs = sorted(bus_settings[offset].items())
            request = supriya.commands.ControlBusSetRequest(
                index_value_pairs=index_value_pairs
            )
            requests.append(request)
        return requests

    def _collect_buffer_allocate_requests(
        self, buffer_open_states, id_mapping, start_buffers
    ):
        requests = []
        if not start_buffers:
            return requests
        for buffer_ in sorted(start_buffers, key=lambda x: x.session_id):
            arguments = dict(
                buffer_id=id_mapping[buffer_], frame_count=buffer_.frame_count
            )
            request_class = supriya.commands.BufferAllocateRequest
            if buffer_.file_path is not None:
                request_class = supriya.commands.BufferAllocateReadRequest
                arguments["file_path"] = buffer_.file_path
                arguments["starting_frame"] = buffer_.starting_frame
                channel_indices = buffer_.channel_count
                if isinstance(channel_indices, int):
                    channel_indices = tuple(range(buffer_.channel_count))
                    arguments["channel_indices"] = channel_indices
                    request_class = supriya.commands.BufferAllocateReadChannelRequest
                elif isinstance(buffer_.channel_count, tuple):
                    arguments["channel_indices"] = channel_indices
                    request_class = supriya.commands.BufferAllocateReadChannelRequest
            else:
                arguments["channel_count"] = buffer_.channel_count or 1
                arguments["frame_count"] = arguments["frame_count"] or 1
            try:
                request = request_class(**arguments)
            except TypeError:
                raise
            requests.append(request)
            buffer_open_states[id_mapping[buffer_]] = False
        return requests

    def _collect_buffer_free_requests(
        self, buffer_open_states, id_mapping, stop_buffers
    ):
        requests = []
        if not stop_buffers:
            return requests
        for buffer_ in sorted(stop_buffers, key=lambda x: x.session_id):
            if buffer_open_states[id_mapping[buffer_]]:
                close_request = supriya.commands.BufferCloseRequest(
                    buffer_id=id_mapping[buffer_]
                )
                requests.append(close_request)
            request = supriya.commands.BufferFreeRequest(buffer_id=id_mapping[buffer_])
            requests.append(request)
            del (buffer_open_states[id_mapping[buffer_]])
        return requests

    def _collect_buffer_nonlifecycle_requests(
        self,
        all_buffers,
        buffer_open_states,
        buffer_settings,
        id_mapping,
        offset,
        request_types,
    ):
        requests = []
        buffer_settings = buffer_settings.get(offset)
        if not buffer_settings:
            return requests
        for request_type in request_types:
            buffer_requests = buffer_settings.get(request_type)
            if not buffer_requests:
                continue
            if request_type in (
                supriya.commands.BufferReadRequest,
                supriya.commands.BufferReadChannelRequest,
                supriya.commands.BufferWriteRequest,
            ):
                for request in buffer_requests:
                    buffer_id = request.buffer_id
                    open_state = buffer_open_states[buffer_id]
                    if open_state:
                        close_request = supriya.commands.BufferCloseRequest(
                            buffer_id=buffer_id
                        )
                        requests.append(close_request)
                    requests.append(request)
                    open_state = bool(request.leave_open)
                    buffer_open_states[buffer_id] = open_state
            else:
                requests.extend(buffer_requests)
        return requests

    def _collect_buffer_settings(self, id_mapping):
        buffer_settings = {}
        for buffer_ in sorted(self._buffers, key=lambda x: id_mapping[x]):
            for event_type, events in buffer_._events.items():
                for offset, payload in events:
                    payload = payload.copy()
                    for key, value in payload.items():
                        try:
                            if value in id_mapping:
                                payload[key] = id_mapping[value]
                        except TypeError:  # unhashable
                            continue
                    if event_type is supriya.commands.BufferReadRequest:
                        if "channel_indices" in payload:
                            if payload["channel_indices"] is not None:
                                event = supriya.commands.BufferReadChannelRequest(
                                    **payload
                                )
                            else:
                                payload.pop("channel_indices")
                                event = supriya.commands.BufferReadRequest(**payload)
                        else:
                            event = supriya.commands.BufferReadRequest(**payload)
                    else:
                        event = event_type(**payload)
                    offset_settings = buffer_settings.setdefault(offset, {})
                    event_type_settings = offset_settings.setdefault(event_type, [])
                    event_type_settings.append(event)
        return buffer_settings

    def _collect_bus_settings(self, id_mapping):
        bus_settings = {}
        for bus in self._buses:
            if bus.calculation_rate != supriya.CalculationRate.CONTROL:
                continue
            bus_id = id_mapping[bus]
            for offset, value in bus._events:
                bus_settings.setdefault(offset, {})[bus_id] = value
        return bus_settings

    def _collect_durated_objects(self, offset, is_last_offset):
        state = self._find_state_at(offset, clone_if_missing=True)
        start_buffers, start_nodes = state.start_buffers, state.start_nodes
        stop_buffers = state.stop_buffers.copy()
        stop_nodes = state.stop_nodes.copy()
        if is_last_offset:
            stop_buffers.update(state.overlap_buffers)
            stop_nodes.update(state.overlap_nodes)
        all_buffers = set(self.buffers.find_intersection(offset))
        all_nodes = set(self.nodes.find_intersection(offset))
        all_buffers.update(stop_buffers)
        all_nodes.update(stop_nodes)
        return (
            all_buffers,
            all_nodes,
            start_buffers,
            start_nodes,
            stop_buffers,
            stop_nodes,
        )

    def _collect_node_action_requests(
        self, duration, id_mapping, node_actions, node_settings, start_nodes
    ):
        import supriya.nonrealtime

        requests = []
        for source, action in node_actions.items():
            if source in start_nodes:
                if isinstance(source, supriya.nonrealtime.Synth):
                    synth_kwargs = source.synth_kwargs
                    if source in node_settings:
                        synth_kwargs.update(node_settings.pop(source))
                    if "duration" in source.synthdef.parameter_names:
                        # need to propagate in session rendering timespan
                        # as many nodes have "infinite" duration
                        node_duration = source.duration
                        if (
                            duration < source.stop_offset
                        ):  # duration is session duration
                            node_duration = duration - source.start_offset
                        synth_kwargs["duration"] = float(node_duration)
                    request = source._to_request(action, id_mapping, **synth_kwargs)
                else:
                    request = source._to_request(action, id_mapping)
            else:
                request = action._to_request(id_mapping)
            requests.append(request)
        return requests

    def _collect_node_free_requests(self, id_mapping, stop_nodes):
        requests = []
        if stop_nodes:
            free_ids, gate_ids = [], []
            for node in stop_nodes:
                node_id = id_mapping[node]
                if (
                    hasattr(node, "synthdef")
                    and "gate" in node.synthdef.parameter_names
                ):
                    gate_ids.append(node_id)
                elif node.duration:
                    free_ids.append(node_id)
            free_ids.sort()
            gate_ids.sort()
            if free_ids:
                request = supriya.commands.NodeFreeRequest(node_ids=free_ids)
                requests.append(request)
            if gate_ids:
                for node_id in gate_ids:
                    request = supriya.commands.NodeSetRequest(node_id=node_id, gate=0)
                    requests.append(request)
        return requests

    def _collect_node_settings(self, offset, state, id_mapping):
        result = collections.OrderedDict()
        if state.nodes_to_children is None:
            # Current state is sparse;
            # Use previous non-sparse state's nodes to order settings.
            state = self._find_state_before(offset, with_node_tree=True)
            iterator = state._iterate_nodes(self.root_node, state.nodes_to_children)
        else:
            iterator = state._iterate_nodes(self.root_node, state.nodes_to_children)
        for node in iterator:
            settings = node._collect_settings(
                offset, id_mapping=id_mapping, persistent=False
            )
            if settings:
                result[node] = settings
        return result

    def _collect_node_set_requests(self, id_mapping, node_settings):
        import supriya.nonrealtime

        scalar_rate = supriya.ParameterRate.SCALAR
        requests = []
        bus_prototype = (
            supriya.nonrealtime.Bus,
            supriya.nonrealtime.BusGroup,
            type(None),
        )
        buffer_prototype = (supriya.nonrealtime.Buffer, supriya.nonrealtime.BufferGroup)
        for node, settings in node_settings.items():
            parameters = {}
            if isinstance(node, supriya.nonrealtime.Synth):
                parameters = node.synthdef.parameters
            node_id = id_mapping[node]
            a_settings = {}
            c_settings = {}
            n_settings = {}
            for key, value in settings.items():
                if key in parameters and parameters[key].parameter_rate == scalar_rate:
                    continue
                if isinstance(value, bus_prototype):
                    if value is None:
                        c_settings[key] = -1
                    elif (
                        value.calculation_rate
                        == supriya.realtime.CalculationRate.CONTROL
                    ):
                        c_settings[key] = id_mapping[value]
                    else:
                        a_settings[key] = id_mapping[value]
                else:
                    if isinstance(value, buffer_prototype):
                        value = id_mapping[value]
                    n_settings[key] = value
            if n_settings:
                request = supriya.commands.NodeSetRequest(node_id=node_id, **n_settings)
                requests.append(request)
            if a_settings:
                request = supriya.commands.NodeMapToAudioBusRequest(
                    node_id=node_id, **a_settings
                )
                requests.append(request)
            if c_settings:
                request = supriya.commands.NodeMapToControlBusRequest(
                    node_id=node_id, **c_settings
                )
                requests.append(request)
        return requests

    def _collect_requests_at_offset(
        self,
        buffer_open_states,
        buffer_settings,
        bus_settings,
        duration,
        id_mapping,
        is_last_offset,
        offset,
        visited_synthdefs,
    ):
        requests = []
        (
            all_buffers,
            all_nodes,
            start_buffers,
            start_nodes,
            stop_buffers,
            stop_nodes,
        ) = self._collect_durated_objects(offset, is_last_offset)
        state = self._find_state_at(offset, clone_if_missing=True)
        node_actions = state.transitions
        node_settings = self._collect_node_settings(offset, state, id_mapping)
        requests += self._collect_synthdef_requests(start_nodes, visited_synthdefs)
        requests += self._collect_buffer_allocate_requests(
            buffer_open_states, id_mapping, start_buffers
        )
        requests += self._collect_buffer_nonlifecycle_requests(
            all_buffers,
            buffer_open_states,
            buffer_settings,
            id_mapping,
            offset,
            self._ordered_buffer_post_alloc_request_types,
        )
        requests += self._collect_node_action_requests(
            duration, id_mapping, node_actions, node_settings, start_nodes
        )
        requests += self._collect_bus_set_requests(bus_settings, offset)
        requests += self._collect_node_set_requests(id_mapping, node_settings)
        requests += self._collect_node_free_requests(id_mapping, stop_nodes)
        requests += self._collect_buffer_nonlifecycle_requests(
            all_buffers,
            buffer_open_states,
            buffer_settings,
            id_mapping,
            offset,
            self._ordered_buffer_pre_free_request_types,
        )
        requests += self._collect_buffer_free_requests(
            buffer_open_states, id_mapping, stop_buffers
        )
        return requests

    def _collect_synthdef_requests(self, start_nodes, visited_synthdefs):
        import supriya.nonrealtime

        requests = []
        synthdefs = set()
        for node in start_nodes:
            if not isinstance(node, supriya.nonrealtime.Synth):
                continue
            elif node.synthdef in visited_synthdefs:
                continue
            synthdefs.add(node.synthdef)
            visited_synthdefs.add(node.synthdef)
        synthdefs = sorted(synthdefs, key=lambda x: x.anonymous_name)
        for synthdef in synthdefs:
            request = supriya.commands.SynthDefReceiveRequest(
                synthdefs=synthdef, use_anonymous_names=True
            )
            requests.append(request)
        return requests

    def _find_state_after(self, offset, with_node_tree=None):
        index = bisect.bisect(self.offsets, offset)
        if with_node_tree:
            while index < len(self.offsets):
                state = self.states[self.offsets[index]]
                if state.nodes_to_children is not None:
                    return state
                index += 1
            return None
        if index < len(self.offsets):
            old_offset = self.offsets[index]
            if offset < old_offset:
                return self.states[old_offset]
        return None

    def _find_state_at(self, offset, clone_if_missing=False):
        state = self.states.get(offset, None)
        if state is None and clone_if_missing:
            old_state = self._find_state_before(offset, with_node_tree=True)
            state = old_state._clone(offset)
            self.states[offset] = state
            self.offsets.insert(self.offsets.index(old_state.offset) + 1, offset)
        return state

    def _find_state_before(self, offset, with_node_tree=None):
        index = bisect.bisect_left(self.offsets, offset)
        if index == len(self.offsets):
            index -= 1
        old_offset = self.offsets[index]
        if offset <= old_offset:
            index -= 1
        if index < 0:
            return None
        if with_node_tree:
            while 0 <= index:
                state = self.states[self.offsets[index]]
                if state.nodes_to_children is not None:
                    return state
                index -= 1
            return None
        return self.states[self.offsets[index]]

    def _get_next_session_id(self, kind="node"):
        default = 0
        if kind == "node":
            default = 1000
        session_id = self._session_ids.setdefault(kind, default)
        self._session_ids[kind] += 1
        return session_id

    def _iterate_state_pairs(self, offset, with_node_tree=None):
        state_one = self._find_state_at(offset, clone_if_missing=True)
        state_two = self._find_state_after(
            state_one.offset, with_node_tree=with_node_tree
        )
        while state_two is not None:
            yield state_one, state_two
            state_one = state_two
            state_two = self._find_state_after(
                state_one.offset, with_node_tree=with_node_tree
            )

    def _setup_buses(self):
        import supriya.nonrealtime

        self._buses = collections.OrderedDict()
        self._audio_input_bus_group = None
        if self._options._input_bus_channel_count:
            self._audio_input_bus_group = supriya.nonrealtime.AudioInputBusGroup(self)
        self._audio_output_bus_group = None
        if self._options._output_bus_channel_count:
            self._audio_output_bus_group = supriya.nonrealtime.AudioOutputBusGroup(self)

    def _setup_initial_states(self):
        import supriya.nonrealtime

        offset = float("-inf")
        state = supriya.nonrealtime.State(self, offset)
        state._nodes_to_children = {self.root_node: None}
        state._nodes_to_parents = {self.root_node: None}
        self.states[offset] = state
        self.offsets.append(offset)
        offset = 0.0
        state = state._clone(offset)
        self.states[offset] = state
        self.offsets.append(offset)

    def _remove_state_at(self, offset):
        state = self._find_state_at(offset, clone_if_missing=False)
        if state is None:
            return
        assert state.is_sparse
        self.offsets.remove(offset)
        del (self.states[offset])
        return state

    def _to_non_xrefd_osc_bundles(self, duration=None):
        osc_bundles = []
        request_bundles = self._to_non_xrefd_request_bundles(duration=duration)
        for request_bundle in request_bundles:
            osc_bundles.append(request_bundle.to_osc(True))
        return osc_bundles

    def _to_non_xrefd_request_bundles(self, duration=None):
        id_mapping = self._build_id_mapping()
        if self.duration == float("inf"):
            assert duration is not None and 0 < duration < float("inf")
        duration = duration or self.duration
        offsets = self.offsets[1:]
        if duration not in offsets:
            offsets.append(duration)
            offsets.sort()
        buffer_settings = self._collect_buffer_settings(id_mapping)
        bus_settings = self._collect_bus_settings(id_mapping)
        is_last_offset = False
        request_bundles = []
        buffer_open_states = {}
        visited_synthdefs = set()
        for offset in offsets:
            requests = []
            if offset == duration:
                is_last_offset = True
            requests = self._collect_requests_at_offset(
                buffer_open_states,
                buffer_settings,
                bus_settings,
                duration,
                id_mapping,
                is_last_offset,
                offset,
                visited_synthdefs,
            )
            if is_last_offset:
                requests.append(NothingRequest())
            if requests:
                request_bundle = RequestBundle(
                    contents=requests, timestamp=float(offset)
                )
                request_bundles.append(request_bundle)
            if is_last_offset:
                break
        return request_bundles

    ### PUBLIC METHODS ###

    def at(self, offset, propagate=True):
        import supriya.nonrealtime

        offset = float(offset)
        assert 0 <= offset
        state = self._find_state_at(offset)
        if state:
            assert state.offset in self.states
        if not state:
            state = self._add_state_at(offset)
        return supriya.nonrealtime.Moment(self, offset, state, propagate)

    @SessionObject.require_offset
    def add_buffer(
        self,
        channel_count=None,
        duration=None,
        frame_count=None,
        starting_frame=None,
        file_path=None,
        offset=None,
    ):
        import supriya.nonrealtime

        start_moment = self.active_moments[-1]
        session_id = self._get_next_session_id("buffer")
        buffer_ = supriya.nonrealtime.Buffer(
            self,
            channel_count=channel_count,
            duration=duration,
            file_path=file_path,
            frame_count=frame_count,
            session_id=session_id,
            start_offset=offset,
            starting_frame=starting_frame,
        )
        start_moment.state.start_buffers.add(buffer_)
        with self.at(buffer_.stop_offset) as stop_moment:
            stop_moment.state.stop_buffers.add(buffer_)
        self._buffers.insert(buffer_)
        return buffer_

    @SessionObject.require_offset
    def add_buffer_group(
        self,
        buffer_count=1,
        channel_count=None,
        duration=None,
        frame_count=None,
        offset=None,
    ):
        import supriya.nonrealtime

        start_moment = self.active_moments[-1]
        buffer_group = supriya.nonrealtime.BufferGroup(
            self,
            buffer_count=buffer_count,
            channel_count=channel_count,
            duration=duration,
            frame_count=frame_count,
            start_offset=offset,
        )
        for buffer_ in buffer_group:
            self._buffers.insert(buffer_)
            start_moment.state.start_buffers.add(buffer_)
        with self.at(buffer_group.stop_offset) as stop_moment:
            for buffer_ in buffer_group:
                stop_moment.state.stop_buffers.add(buffer_)
        return buffer_group

    def add_bus(self, calculation_rate="control"):
        import supriya.nonrealtime

        session_id = self._get_next_session_id("bus")
        bus = supriya.nonrealtime.Bus(
            self, calculation_rate=calculation_rate, session_id=session_id
        )
        self._buses[bus] = None  # ordered dictionary
        return bus

    def add_bus_group(self, bus_count=1, calculation_rate="control"):
        import supriya.nonrealtime

        session_id = self._get_next_session_id("bus")
        bus_group = supriya.nonrealtime.BusGroup(
            self,
            bus_count=bus_count,
            calculation_rate=calculation_rate,
            session_id=session_id,
        )
        for bus in bus_group:
            self._buses[bus] = None  # ordered dictionary
        return bus_group

    def add_group(self, add_action=None, duration=None, offset=None):
        return self.root_node.add_group(
            add_action=add_action, duration=duration, offset=offset
        )

    def add_synth(
        self, add_action=None, duration=None, synthdef=None, offset=None, **synth_kwargs
    ):
        return self.root_node.add_synth(
            add_action=add_action,
            duration=duration,
            offset=offset,
            synthdef=synthdef,
            **synth_kwargs,
        )

    @SessionObject.require_offset
    def cue_soundfile(
        self,
        file_path,
        channel_count=None,
        duration=None,
        frame_count=1024 * 32,
        starting_frame=0,
        offset=None,
    ):
        if isinstance(file_path, str):
            file_path = pathlib.Path(file_path)
        if isinstance(file_path, pathlib.Path):
            assert file_path.exists()
            soundfile = supriya.soundfiles.SoundFile(str(file_path))
            channel_count = channel_count or soundfile.channel_count
        elif isinstance(file_path, type(self)):
            channel_count = channel_count or len(file_path.audio_output_bus_group)
        elif hasattr(file_path, "__session__"):
            channel_count = channel_count or file_path.output_bus_channel_count
        buffer_ = self.add_buffer(
            channel_count=channel_count,
            duration=duration,
            frame_count=frame_count,
            offset=offset,
        )
        buffer_.read(
            file_path,
            leave_open=True,
            starting_frame_in_file=starting_frame,
            offset=offset,
        )
        return buffer_

    @classmethod
    def from_project_settings(
        cls, project_settings, input_=None, name=None, padding=None
    ):
        import supriya.cli

        assert isinstance(project_settings, supriya.cli.ProjectSettings)
        server_options = supriya.realtime.ServerOptions(
            **project_settings.get("server_options", {})
        )
        input_bus_channel_count = server_options.input_bus_channel_count
        output_bus_channel_count = server_options.output_bus_channel_count
        return cls(
            input_bus_channel_count=input_bus_channel_count,
            output_bus_channel_count=output_bus_channel_count,
            input_=input_,
            name=name,
            padding=padding,
        )

    def inscribe(self, pattern, duration=None, offset=None, seed=None):
        return self.root_node.inscribe(
            pattern, duration=duration, offset=offset, seed=seed
        )

    @staticmethod
    def is_session_like(expr):
        if hasattr(expr, "__render__"):
            return True
        elif hasattr(expr, "__session__"):
            return True
        return False

    def move_node(self, node, add_action=None, offset=None):
        self.root_node.move_node(node, add_action=add_action, offset=offset)

    def rebuild_transitions(self):
        for state_one, state_two in self._iterate_state_pairs(
            float("-inf"), with_node_tree=True
        ):
            transitions = state_two._rebuild_transitions(state_one, state_two)
            state_two._transitions = transitions

    def render(
        self,
        output_file_path=None,
        debug=None,
        duration=None,
        header_format=HeaderFormat.AIFF,
        input_file_path=None,
        render_directory_path=None,
        sample_format=SampleFormat.INT24,
        sample_rate=44100,
        print_transcript=None,
        transcript_prefix=None,
        **kwargs,
    ):
        import supriya.nonrealtime

        duration = (duration or self.duration) or 0.0
        assert 0.0 < duration < float("inf")
        renderer = supriya.nonrealtime.SessionRenderer(
            session=self,
            header_format=header_format,
            print_transcript=print_transcript,
            render_directory_path=render_directory_path,
            sample_format=sample_format,
            sample_rate=sample_rate,
            transcript_prefix=transcript_prefix,
        )
        exit_code, transcript, output_file_path = renderer.render(
            output_file_path, duration=duration, debug=debug, **kwargs
        )
        self._transcript = transcript
        return exit_code, output_file_path

    @SessionObject.require_offset
    def set_rand_seed(self, rand_id=0, rand_seed=0, offset=None):
        return self.add_synth(
            add_action="ADD_TO_HEAD",
            duration=0,
            rand_id=rand_id,
            rand_seed=rand_seed,
            synthdef=self._build_rand_seed_synthdef(),
        )

    def to_lists(
        self,
        duration=None,
        header_format=HeaderFormat.AIFF,
        sample_format=SampleFormat.INT24,
        sample_rate=44100,
    ):
        import supriya.nonrealtime

        renderer = supriya.nonrealtime.SessionRenderer(
            session=self,
            header_format=header_format,
            sample_format=sample_format,
            sample_rate=sample_rate,
        )
        return renderer.to_lists(duration=duration)

    def to_osc_bundles(
        self,
        duration=None,
        header_format=HeaderFormat.AIFF,
        sample_format=SampleFormat.INT24,
        sample_rate=44100,
    ):
        import supriya.nonrealtime

        renderer = supriya.nonrealtime.SessionRenderer(
            session=self,
            header_format=header_format,
            sample_format=sample_format,
            sample_rate=sample_rate,
        )
        return renderer.to_osc_bundles(duration=duration)

    def to_strings(self, include_controls=False, include_timespans=False):
        import supriya.commands

        result = []
        previous_string = None
        for offset, state in sorted(self.states.items()):
            if offset < 0:
                continue
            self._apply_transitions(state.offset)
            query_tree_group = supriya.commands.QueryTreeGroup.from_state(
                state,
                include_controls=include_controls,
                include_timespans=include_timespans,
            )
            string = str(query_tree_group)
            if string == previous_string:
                continue
            previous_string = string
            result.append("{}:".format(float(round(offset, 6))))
            result.extend(("    " + line for line in string.split("\n")))
        return "\n".join(result)

    ### PUBLIC PROPERTIES ###

    @property
    def active_moments(self):
        return self._active_moments

    @property
    def audio_input_bus_group(self):
        return self._audio_input_bus_group

    @property
    def audio_output_bus_group(self):
        return self._audio_output_bus_group

    @property
    def buffers(self):
        return self._buffers

    @property
    def buses(self):
        return self._buses

    @property
    def duration(self):
        duration = 0.0
        for duration in reversed(self.offsets):
            if duration < float("inf"):
                break
        if duration < 0.0:
            duration = 0.0
        if duration > 0.0 and self.padding:
            duration += self.padding
        return duration

    @property
    def input_(self):
        return self._input

    @property
    def input_bus_channel_count(self):
        return self.options.input_bus_channel_count

    @property
    def name(self):
        return self._name

    @property
    def nodes(self):
        return self._nodes

    @property
    def offsets(self):
        return self._offsets

    @property
    def options(self):
        return self._options

    @property
    def output_bus_channel_count(self):
        return self.options.output_bus_channel_count

    @property
    def padding(self):
        return self._padding

    @property
    def root_node(self):
        return self._root_node

    @property
    def states(self):
        return self._states

    @property
    def transcript(self):
        return self._transcript
