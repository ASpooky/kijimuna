import importlib

import pytest
import smbus2

from hardware_modules import i2c_bus


@pytest.fixture
def reload_i2c_bus(monkeypatch):
    """Reload i2c_bus under a given FAKE_I2C value, and restore it afterwards."""

    def _reload(fake: bool):
        if fake:
            monkeypatch.setenv("FAKE_I2C", "1")
        else:
            monkeypatch.delenv("FAKE_I2C", raising=False)
        return importlib.reload(i2c_bus)

    yield _reload
    monkeypatch.undo()
    importlib.reload(i2c_bus)


class TestSelection:
    def test_uses_fake_when_fake_i2c_is_set(self, reload_i2c_bus):
        module = reload_i2c_bus(fake=True)

        assert module.SMBus is module.FakeSMBus

    def test_uses_smbus2_otherwise(self, reload_i2c_bus):
        module = reload_i2c_bus(fake=False)

        assert module.SMBus is smbus2.SMBus


class TestFakeSMBus:
    def test_context_manager_returns_itself(self):
        bus = i2c_bus.FakeSMBus(1)

        with bus as entered:
            assert entered is bus

    def test_read_returns_last_written_data(self):
        bus = i2c_bus.FakeSMBus(1)

        bus.write_i2c_block_data(0x48, 0x01, [0xC3, 0x83])

        assert bus.read_i2c_block_data(0x48, 0x01, 2) == [0xC3, 0x83]

    def test_read_truncates_to_requested_length(self):
        bus = i2c_bus.FakeSMBus(1)

        assert bus.read_i2c_block_data(0x48, 0x00, 1) == [0x40]
