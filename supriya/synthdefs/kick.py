# =*- encoding: utf-8 -*-
from supriya.tools import synthdeftools
from supriya.tools import ugentools


def _build_kick_synthdef():

    builder = synthdeftools.SynthDefBuilder(
        out=0,
        )

    ### ENVELOPE ###

    gate = ugentools.Impulse.ar(frequency=2)
    envelope = synthdeftools.Envelope.percussive(
        attack_time=0.01,
        release_time=1.0,
        )
    envelope = ugentools.EnvGen.ar(
        done_action=0,
        envelope=envelope,
        gate=gate
        )
    envelope = synthdeftools.Op.squared(envelope)

    ### NOISE COMPONENT ###

    noise = ugentools.PinkNoise.ar()
    noise = ugentools.BPF.ar(
        source=noise,
        frequency=ugentools.LinLin.ar(
            source=synthdeftools.Op.cubed(envelope),
            out_min=30,
            out_max=120,
            ),
        reciprocal_of_q=2,
        )
    noise *= envelope

    ### PITCHED COMPONENT ###

    pitch = ugentools.SinOsc.ar(
        frequency=ugentools.LinLin.ar(
            source=envelope,
            out_min=10,
            out_max=80,
            ),
        )
    pitch = pitch * 2.0
    pitch = synthdeftools.Op.distort(pitch)
    pitch = ugentools.RLPF.ar(
        source=pitch,
        frequency=ugentools.LinLin.ar(
            source=envelope,
            out_min=30,
            out_max=120,
            ),
        reciprocal_of_q=0.5,
        )
    pitch *= envelope

    mix = pitch + noise

    out = ugentools.Out.ar(builder['out'], (mix, mix))

    builder.add_ugen(out)
    synthdef = builder.build()
    return synthdef

kick = _build_kick_synthdef()

__all__ = (
    'kick',
    )