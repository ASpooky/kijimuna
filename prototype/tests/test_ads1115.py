import pytest

from hardware_modules import ads1115
from hardware_modules.ads1115 import init_ads1115, read_voltage
from hardware_modules.ads1115_registers import ADS1115_ADDR, REG_CONFIG, REG_CONVERSION

IDLE_A0 = 0xC383  # what a real ADS1115 returns for our A0 config while idle (OS=1)
BUSY_A0 = 0x4383  # same config while a conversion is running (OS=0)


class TestInit:
    def test_writes_config_without_starting_a_conversion(self, scripted_bus):
        bus = scripted_bus({REG_CONFIG: [IDLE_A0]})

        init_ads1115(bus, channel=0)

        assert bus.writes == [(ADS1115_ADDR, REG_CONFIG, [0x43, 0x83])]

    def test_accepts_readback_with_os_bit_set(self, scripted_bus):
        bus = scripted_bus({REG_CONFIG: [IDLE_A0]})

        init_ads1115(bus, channel=0)  # does not raise

    def test_raises_when_readback_does_not_match(self, scripted_bus):
        # e.g. the write was lost and the chip still has its power-on default
        bus = scripted_bus({REG_CONFIG: [0x8583]})

        with pytest.raises(RuntimeError, match="config mismatch"):
            init_ads1115(bus, channel=0)


class TestReadVoltage:
    def test_starts_single_shot_conversion_on_requested_channel(self, scripted_bus):
        bus = scripted_bus({REG_CONFIG: [0xD383], REG_CONVERSION: [0]})

        read_voltage(bus, channel=1)

        assert bus.writes == [(ADS1115_ADDR, REG_CONFIG, [0xD3, 0x83])]

    def test_waits_until_os_bit_is_set_before_reading_result(self, scripted_bus):
        bus = scripted_bus({REG_CONFIG: [BUSY_A0, BUSY_A0, IDLE_A0], REG_CONVERSION: [0x4000]})

        read_voltage(bus, channel=0)

        regs = [reg for _, reg, _ in bus.reads]
        assert regs == [REG_CONFIG, REG_CONFIG, REG_CONFIG, REG_CONVERSION]

    @pytest.mark.parametrize(
        ("raw", "volts"),
        [
            (0x0000, 0.0),
            (0x4000, 2.048),
            (0x7FFF, 4.096 * 32767 / 32768),  # positive full scale
            (0xFFFF, -4.096 / 32768),  # -1 LSB
            (0x8000, -4.096),  # negative full scale
        ],
    )
    def test_converts_signed_16bit_to_volts(self, scripted_bus, raw, volts):
        bus = scripted_bus({REG_CONFIG: [IDLE_A0], REG_CONVERSION: [raw]})

        assert read_voltage(bus, channel=0) == pytest.approx(volts)

    def test_times_out_when_conversion_never_finishes(self, scripted_bus, monkeypatch):
        monkeypatch.setattr(ads1115, "CONVERSION_TIMEOUT_S", 0.0)
        bus = scripted_bus({REG_CONFIG: [BUSY_A0], REG_CONVERSION: [0]})

        with pytest.raises(TimeoutError, match="A0"):
            read_voltage(bus, channel=0)

        assert REG_CONVERSION not in [reg for _, reg, _ in bus.reads]
