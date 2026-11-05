"""ADS1115 operations (initialization and single-shot voltage reads).

How the CPU gets a voltage (every read):
  (1) Write "start conversion on A0" to Config   write_i2c_block_data(0x48, 0x01, [hi, lo])
  (2) Wait for the conversion to finish          until the OS bit (bit15) of Config is 1 again
  (3) Read 2 bytes from Conversion               read_i2c_block_data(0x48, 0x00, 2)
  (4) Big-endian signed integer -> voltage       (value × 4.096 / 32768)
"""

import time

from .ads1115_registers import (
    CONFIG_BASE,
    CONFIG_MUX,
    CONFIG_OS_START,
    FULL_SCALE_V,
    REG_CONFIG,
    REG_CONVERSION,
    read_register,
    write_config,
)

CONVERSION_TIMEOUT_S = 0.1


def init_ads1115(bus, channel: int = 0) -> None:
    """Startup setup: write the config without starting a conversion (OS=0), then read it back to verify the link."""
    expected = CONFIG_MUX[channel] | CONFIG_BASE
    write_config(bus, expected)
    actual = read_register(bus, REG_CONFIG)
    # On read, the OS bit reports status (1 while idle), so leave it out of the comparison
    if actual & ~CONFIG_OS_START != expected:
        raise RuntimeError(f"ADS1115 config mismatch: wrote 0x{expected:04X}, read 0x{actual:04X}")
    print(f"ADS1115 ready (config=0x{actual:04X})")


def read_voltage(bus, channel: int) -> float:
    """Run a single-shot conversion on the given channel and return the voltage [V]."""
    # (1) Select the channel and start a conversion
    write_config(bus, CONFIG_OS_START | CONFIG_MUX[channel] | CONFIG_BASE)

    # (2) Wait until the OS bit is 1 (conversion done)
    deadline = time.monotonic() + CONVERSION_TIMEOUT_S
    while not read_register(bus, REG_CONFIG) & CONFIG_OS_START:
        if time.monotonic() > deadline:
            raise TimeoutError(f"ADS1115 conversion timeout (A{channel})")
        time.sleep(0.001)

    # (3) Read the conversion result
    raw = read_register(bus, REG_CONVERSION)

    # (4) Convert to 16-bit signed, then to volts
    if raw & 0x8000:
        raw -= 1 << 16
    return raw * FULL_SCALE_V / 32768
