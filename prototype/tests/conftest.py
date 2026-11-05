import pytest


class ScriptedBus:
    """Test double for smbus2.SMBus.

    - Records every write as (addr, reg, data).
    - Returns scripted 16-bit values per register on read. Each read pops the
      next value; the last value is repeated once the script runs out.
    """

    def __init__(self, reads: dict[int, list[int]] | None = None):
        self.writes: list[tuple[int, int, list[int]]] = []
        self.reads: list[tuple[int, int, int]] = []
        self._script = {reg: list(values) for reg, values in (reads or {}).items()}

    def write_i2c_block_data(self, addr, reg, data):
        self.writes.append((addr, reg, list(data)))

    def read_i2c_block_data(self, addr, reg, length):
        self.reads.append((addr, reg, length))
        values = self._script[reg]
        value = values.pop(0) if len(values) > 1 else values[0]
        return [(value >> 8) & 0xFF, value & 0xFF][:length]


@pytest.fixture
def scripted_bus():
    return ScriptedBus
