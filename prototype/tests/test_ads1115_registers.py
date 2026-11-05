from hardware_modules.ads1115_registers import (
    ADS1115_ADDR,
    CONFIG_BASE,
    CONFIG_MUX,
    CONFIG_OS_START,
    REG_CONFIG,
    REG_CONVERSION,
    read_register,
    write_config,
)


class TestConfigBits:
    def test_base_is_pga_4v_single_shot_128sps_comparator_off(self):
        # PGA=001, MODE=1, DR=100, COMP_QUE=11 -> 0b0000_0011_1000_0011
        assert CONFIG_BASE == 0x0383

    def test_start_conversion_on_a0(self):
        # OS=1, MUX=100 (A0-GND)
        assert CONFIG_OS_START | CONFIG_MUX[0] | CONFIG_BASE == 0xC383

    def test_start_conversion_on_a1(self):
        # OS=1, MUX=101 (A1-GND)
        assert CONFIG_OS_START | CONFIG_MUX[1] | CONFIG_BASE == 0xD383

    def test_power_on_default_differs_from_our_config(self):
        # Datasheet power-on default is 0x8583 (PGA ±2.048V); we must overwrite it
        assert CONFIG_BASE & 0x0E00 != 0x8583 & 0x0E00


class TestWriteConfig:
    def test_sends_high_byte_first_to_config_register(self, scripted_bus):
        bus = scripted_bus()

        write_config(bus, 0xC383)

        assert bus.writes == [(ADS1115_ADDR, REG_CONFIG, [0xC3, 0x83])]


class TestReadRegister:
    def test_combines_bytes_as_big_endian(self, scripted_bus):
        bus = scripted_bus({REG_CONVERSION: [0x1234]})

        assert read_register(bus, REG_CONVERSION) == 0x1234
        assert bus.reads == [(ADS1115_ADDR, REG_CONVERSION, 2)]
