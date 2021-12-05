from .pyarc2 import Instrument as __InstrumentLL
from .pyarc2 import BiasOrder, ControlMode, DataMode
from .pyarc2 import ReadAt, ReadAfter, ArC2Error
from .pyarc2 import find_ids as _find_ids

from dataclasses import dataclass
from functools import partial
from enum import Enum


find_ids = _find_ids
""" Find all available device ids """


class IdleMode(Enum):
    """
    IdleMode is used with `Instrument.finalise_operation` to
    mark at what state the channels should be left. Selecting
    `Float` will disconnect all channels and leave their state
    unchanged. `Gnd` will reset all channels to arbitrary voltage
    operation and set them to 0.0 V.
    """

    Float: int = 0b01
    Gnd: int = 0b10


@dataclass
class ArC2Config:
    """
    Convenience dataclass to group ArC2 configuration options.
    """
    idleMode: IdleMode
    controlMode: ControlMode


class Instrument(__InstrumentLL):

    def __init__(self, port, firmware):
        """
        Initialise a new ArC2 connection. Argument `port` is the EFM id that
        can be found with `pyarc2.find_ids` and `firmware` is the path to
        the FPGA firmware to load when initialising.
        """
        super(Instrument, self).__init__()

    def _array_iter_inner(self, mode):
        data = self.pick_one(mode)
        if data is None:
            return None
        return [data]

    def get_iter(self, mode):
        """
        Return an iteration on the internal data buffer. This allows
        users to iterate through the saved results on ArC2's memory
        in the order they were saved. The available modes of retrieval
        are outlined in `DataMode`.

        >>> from pyarc2 import Instrument, ReadAt, ReadAfter, DataMode, IdleMode
        >>> arc = Instrument(0, '/path/to/firmware')
        >>> arc.generate_ramp(3, 3, 0.0, 0.1, 1.0, 1e-7, 10e-6, 5, ReadAt.Bias, ReadAfter.Pulse)
        >>>    .execute()
        >>>    .finalise_operation(IdleMode.Gnd)
        >>>    .wait()
        >>> data = arc.get_iter(DataMode.Bits)
        >>> for datum in data:
        >>>     print(datum) # 32-element array containing bitline currents
        """
        fn = partial(self._array_iter_inner, mode)
        return iter(fn, None)

    def finalise_operation(self, mode):
        """
        This function is used to safely reset channels at the end of
        an operation. The available options are outlined in `IdleMode`.
        Please note that floating the channels will disconnect them
        and leave them in the configuration they were before. For instance
        at the end of a fast operation (fast pulses, fast ramps, etc) the
        channels will still be left in a High Speed driver mode. However
        explicitly grounding the devices will switch them to arbitrary
        voltage (incurring the 120 μs penalty to do so).
        """
        if mode == IdleMode.Float:
            self.ground_all_fast().float_all().execute()
        elif mode == IdleMode.Gnd:
            self.ground_all().execute()
