from ._types import *
from . import pyarc2
import numpy as np


class ArC2Error(Exception): ...

class BiasOrder:
    Cols: ClassVar[pyarc2.BiasOrder] = ...
    Rows: ClassVar[pyarc2.BiasOrder] = ...
    @classmethod
    def __init__(cls) -> None: ...

class ControlMode:
    Header: ClassVar[pyarc2.ControlMode] = ...
    Internal: ClassVar[pyarc2.ControlMode] = ...
    @classmethod
    def __init__(cls) -> None: ...

class DataMode:
    All: ClassVar[pyarc2.DataMode] = ...
    Bits: ClassVar[pyarc2.DataMode] = ...
    Words: ClassVar[pyarc2.DataMode] = ...
    @classmethod
    def __init__(cls) -> None: ...

class ReadType:
    Current: ClassVar[pyarc2.ReadType] = ...
    Voltage: ClassVar[pyarc2.ReadType] = ...
    @classmethod
    def __init(cls) -> None: ...

class AuxDACFn:
    SELL: ClassVar[pyarc2.AuxDACFn] = ...
    SELH: ClassVar[pyarc2.AuxDACFn] = ...
    ARB1: ClassVar[pyarc2.AuxDACFn] = ...
    ARB2: ClassVar[pyarc2.AuxDACFn] = ...
    ARB3: ClassVar[pyarc2.AuxDACFn] = ...
    ARB4: ClassVar[pyarc2.AuxDACFn] = ...
    CREF: ClassVar[pyarc2.AuxDACFn] = ...
    CSET: ClassVar[pyarc2.AuxDACFn] = ...
    @classmethod
    def __init__(cls) -> None: ...

class InstrumentLL:
    @classmethod
    def __init__(cls, port: int, fw: str) -> None: ...
    def bit_currents_from_address(self, addr: int) -> np.ndarray: ...
    def busy(self) -> bool: ...
    def config_channels(self, input: Iterable[tuple[int, float]], base: Optional[float]) -> InstrumentLL: ...
    def config_aux_channels(self, input: Iterable[tuple[AuxDACFn, float]]) -> InstrumentLL: ...
    def config_selectors(self, input: Iterable[int]) -> InstrumentLL: ...
    def connect_to_gnd(self, chans: IntIterable) -> InstrumentLL: ...
    def gnd_add(self, chans: IntIterable) -> InstrumentLL: ...
    def gnd_remove(self, chans: IntIterable) -> InstrumentLL: ...
    def connect_to_ac_gnd(self, chans: IntIterable) -> InstrumentLL: ...
    def gnd_ac_add(self, chans: IntIterable) -> InstrumentLL: ...
    def gnd_ac_remove(self, chans: IntIterable) -> InstrumentLL: ...
    def currents_from_address(self, addr: int, chans: IntIterable) -> np.ndarray: ...
    def delay(self, nanos: int) -> InstrumentLL: ...
    def execute(self) -> InstrumentLL: ...
    def float_all(self) -> InstrumentLL: ...
    def generate_ramp(self, low: int, high: int, vstart: float, vstep: float, vstop: float,
        pw_nanos: int, inter_nanos: int, num_pulses: int, read_at: ReadAt,
        read_after: ReadAfter) -> InstrumentLL: ...
    def generate_read_train(self, lows: Optional[IntIterable], highs: IntIterable,
        vread: float, nreads: int, inter_nanos: int, ground: bool) -> InstrumentLL: ...
    def generate_vread_train(self, chans: IntIterable, averaging: bool, npulses: int,
        inter_nanos: int) -> InstrumentLL: ...
    def ground_all(self) -> InstrumentLL: ...
    def ground_all_fast(self) -> InstrumentLL: ...
    def open_channels(self, channels: Iterable[int]) -> InstrumentLL: ...
    def pick_one(self, mode: DataMode, rtype: ReadType) -> Optional[np.ndarray]: ...
    def pulse_all(self, vpulse: float, nanos: int, order: BiasOrder) -> InstrumentLL: ...
    def pulse_one(self, low: int, high: int, voltage: float, nanos: int) -> InstrumentLL: ...
    def pulse_slice(self, chan: int, voltage: float, nanos: int) -> InstrumentLL: ...
    def pulse_slice_fast_open(self, chans: List[tuple[int, float, float]], cl_nanos: List[Optional[int]],
        preset_state: bool) -> InstrumentLL: ...
    def pulse_slice_masked(self, chan: int, voltage: float, nanos: int, mask: IntIterable) -> InstrumentLL: ...
    def pulseread_all(self, vpulse: float, nanos: int, vread: float, order: BiasOrder) -> np.ndarray: ...
    def pulseread_one(self, low: int, high: int, vpulse: float, nanos: int, vread: float) -> float: ...
    def pulseread_slice(self, chan: int, vpulse: float, nanos: int, vread: float) -> np.ndarray: ...
    def pulseread_slice_masked(self, chan: int, mask: IntIterable, vpulse: float,
        nanos: int, vread: float) -> np.ndarray: ...
    def read_all(self, vread: float, order: BiasOrder) -> np.ndarray: ...
    def read_one(self, low: int, high: int, vread: float) -> float: ...
    def read_slice(self, chan: int, vread: float) -> np.ndarray: ...
    def read_slice_masked(self, chan: int, mask: IntIterable, vread: float) -> np.ndarray: ...
    def read_slice_open(self, highs: IntIterable, ground_after: bool) -> np.ndarray: ...
    def read_slice_open_deferred(self, highs: IntIterable, ground_after: bool) -> InstrumentLL: ...
    def vread_channels(self, chans: IntIterable, averaging: bool) -> List[float]: ...
    def read_train(self, low: int, high: int, vread: float, interpulse: int,
        preload: Optional[float], condition: WaitFor) -> None: ...
    def set_control_mode(self, mode: ControlMode) -> InstrumentLL: ...
    def set_logic(self, mask: int) -> InstrumentLL: ...
    def wait(self) -> None: ...
    def word_currents_from_address(self, addr: int) -> np.ndarray: ...

class ReadAfter:
    Block: ClassVar[pyarc2.ReadAfter] = ...
    Never: ClassVar[pyarc2.ReadAfter] = ...
    Pulse: ClassVar[pyarc2.ReadAfter] = ...
    Ramp: ClassVar[pyarc2.ReadAfter] = ...
    @classmethod
    def __init__(cls) -> None: ...
    def from_str(self, r: str) -> ReadAfter: ...

class ReadAt:
    Bias: ClassVar[pyarc2.ReadAt] = ...
    Never: ClassVar[pyarc2.ReadAt] = ...
    @classmethod
    def __init__(cls) -> None: ...
    def Arb(self, voltage) -> ReadAt: ...
    def voltage(self) -> float: ...

class WaitFor:
    @classmethod
    def __init__(cls) -> None: ...
    def Iterations(self, iterations: int) -> WaitFor: ...
    def Millis(self, millis: int) -> WaitFor: ...
    def Nanos(self, nanos: int) -> WaitFor: ...

def find_ids() -> List[int]: ...
