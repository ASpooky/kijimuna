import os

# SMBus talks to the special device file /dev/i2c-1 through the Linux ioctl system call.
# The Ubuntu (WSL) dev environment has neither an I2C adapter nor /dev/i2c-1,
# so setting the FAKE_I2C environment variable swaps in a mock SMBus.

class FakeSMBus:

    def __init__(self,bus:int):
        self.regs =  {0x00: [0x40, 0x00], 0x01: [0x85, 0x83]}

    def __enter__(self): return self

    def __exit__(self, *a): pass

    def write_i2c_block_data(self,addr,reg,data): self.regs[reg] = list(data)

    def read_i2c_block_data(self,addr,reg,length): return self.regs[reg][:length]

if os.environ.get("FAKE_I2C"):
    SMBus = FakeSMBus
else:
    from smbus2 import SMBus
