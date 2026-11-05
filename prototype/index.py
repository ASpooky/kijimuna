from hardware_modules.i2c_bus import SMBus
import time

from hardware_modules.ads1115 import init_ads1115, read_voltage

# =============================================================================
# How soil moisture becomes a number the CPU can read
# =============================================================================
#
#   Gajumaru soil ──(moisture)──▶ soil sensor ──(analog voltage)──▶ ADS1115 ──(I2C)──▶ Pi CPU
#
# 1. Soil sensor (capacitive v1.2)
#    - An analog part: soil moisture changes its capacitance, which it outputs
#      as a 0-3.3V voltage on the OUT pin.
#    - Drier = higher voltage, wetter = lower (roughly: dry ~2.x V / in water ~1.x V).
#    - It has no I2C address; the CPU cannot talk to it directly.
#
# 2. ADS1115 (16-bit ADC, I2C address 0x48)  → hardware_modules/ads1115_registers.py, ads1115.py
#    - The Pi 4 has no analog inputs, so the ADS1115 turns voltages into numbers.
#    - Four inputs A0-A3. kijimuna wires sensor 1 → A0, sensor 2 → A1.
#    - Which input, which range and when to convert are set by writing the
#      Config register (0x01); the result lands in the Conversion register (0x00)
#      as a 16-bit signed integer.
#
# 3. I2C (2-wire serial bus: SDA = pin3, SCL = pin5)  → hardware_modules/i2c_bus.py
#    - The standard for carrying 0/1 over the wire:
#      START → address (7-bit) + R/W → ACK → data → STOP.
#    - What the bytes mean (which register does what) is defined by the ADS1115
#      datasheet, not by I2C.
#    - On Linux, smbus2 issues ioctl calls on /dev/i2c-1 (the i2c-dev driver's
#      entry point), and the kernel's i2c-bcm2835 driver drives the BSC1
#      controller to put the waveform on SDA/SCL.

I2C_BUS = 1  # Pi pin3/pin5 are I2C bus 1 (/dev/i2c-1)
SOIL_CHANNELS = [0, 1]  # sensor 1 = A0, sensor 2 = A1
READ_INTERVAL_S = 5


def main() -> None:
    with SMBus(I2C_BUS) as bus:
        # Startup setup: first write to the ADS1115
        init_ads1115(bus, SOIL_CHANNELS[0])

        while True:
            # step1: read the soil sensors
            voltages = [read_voltage(bus, ch) for ch in SOIL_CHANNELS]
            print("  ".join(f"A{ch}={v:.3f}V" for ch, v in zip(SOIL_CHANNELS, voltages)))

            time.sleep(READ_INTERVAL_S)


# Start only when run directly as `python index.py` (importing just loads the definitions)
if __name__ == "__main__":
    main()
