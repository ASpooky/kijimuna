"""ADS1115 register map and single-register read/write.

Reference: ADS1115 datasheet https://www.ti.com/lit/ds/symlink/ads1115.pdf (Register Map)

The ADS1115 has four registers (0x00-0x03), each 16-bit and big-endian.
The `reg` argument of read/write goes into the Pointer Register
(the number of the register to access next).
"""

ADS1115_ADDR = 0x48  # address with the ADDR pin tied to GND (confirmed with i2cdetect)

REG_CONVERSION = 0x00
REG_CONFIG = 0x01

# Config register (16-bit) bit layout
#   bit15    OS        write: 1 = start a single conversion / read: 1 = idle (conversion done)
#   bit14:12 MUX       100 = A0-GND, 101 = A1-GND, 110 = A2-GND, 111 = A3-GND
#   bit11:9  PGA       001 = ±4.096V (sensors are powered from 3.3V, so 3.3V fits in range)
#   bit8     MODE      1 = single-shot (returns to power-down after one conversion)
#   bit7:5   DR        100 = 128 SPS (about 8 ms per conversion)
#   bit4:0   COMP_*    00011 = comparator disabled (ALERT pin unused)
CONFIG_OS_START = 0x8000
CONFIG_MUX = {0: 0x4000, 1: 0x5000, 2: 0x6000, 3: 0x7000}
CONFIG_PGA_4_096V = 0x0200
CONFIG_MODE_SINGLE = 0x0100
CONFIG_DR_128SPS = 0x0080
CONFIG_COMP_DISABLE = 0x0003

CONFIG_BASE = CONFIG_PGA_4_096V | CONFIG_MODE_SINGLE | CONFIG_DR_128SPS | CONFIG_COMP_DISABLE
FULL_SCALE_V = 4.096  # must match the PGA setting in CONFIG_BASE


def write_config(bus, config: int) -> None:
    # The ADS1115 expects the high byte first (big-endian)
    bus.write_i2c_block_data(ADS1115_ADDR, REG_CONFIG, [(config >> 8) & 0xFF, config & 0xFF])


def read_register(bus, reg: int) -> int:
    hi, lo = bus.read_i2c_block_data(ADS1115_ADDR, reg, 2)
    return (hi << 8) | lo
