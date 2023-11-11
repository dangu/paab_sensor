from pymodbus.client import ModbusSerialClient
# import time
import logging
import sys

MODBUS_ADDRESS = 2

logger = logging.getLogger(__name__)

class PAABSensor:
    def __init__(self, port, address, enableWrites=False):
        self._enableWrites = enableWrites
        self.client = ModbusSerialClient(method='rtu',
                                         port=port,
                                         timeout=0.5,
                                         baudrate=9600)
        self._address = address

    def getRegister(self, reg):
        """Get register"""
        return self.client.read_holding_registers(reg,
                                                  count=1,
                                                  slave=self._address)

    def setRegister(self, reg, value):
        """Set register"""
        if self._enableWrites:
            result = self.client.write_register(reg, value, slave=self._address)
            if not result.isError():
                logger.debug(f"Write {reg:04}:{value}")
            else:
                logger.error(f"Could not write register {result}")
        else:
            logger.debug(f"Would write {reg}:{value}")

    def setRelays(self, relaysState):
        """Set relay states"""
        relayReg = 0x04
        value = 0
        if relaysState[0]:
            value |= 0x01
        if relaysState[1]:
            value |= 0x02
        self.setRegister(reg=relayReg, value=value)
        
    
def dumpAllRegisters():
    """Dump all 255 registers"""
    paabSensor = PAABSensor(port="/dev/ttyUSB0",
                            address=MODBUS_ADDRESS)
    for reg in range(1,256):
        result=paabSensor.getRegister(reg=reg)
        if result.isError():
            logger.info(f"Register: 0x{reg:02X} ({reg:3}), Error: {result}")
        else:
            valueUnsigned=result.registers[0]
            valueSigned=int.from_bytes(valueUnsigned.to_bytes(2, byteorder='big', signed=False), byteorder='big', signed=True)
            logger.info(f"Register: 0x{reg:02X} ({reg:3}), data: 0x{valueUnsigned:04X} ({valueSigned})")


def testMeasure():
    """Measure register 1"""
    paabSensor = PAABSensor(port="/dev/ttyUSB0",
                            address=MODBUS_ADDRESS,
                            enableWrites=True)
    paabSensor.setRegister(reg=0x32,value=5)
    paabSensor.setRegister(reg=0x3A,value=5)

    reg=0x01
    while(True):
        result=paabSensor.getRegister(reg=reg)
        if result.isError():
            logger.info(f"Register: 0x{reg:02X} ({reg:3}), Error: {result}")
        else:
            valueUnsigned=result.registers[0]
            valueSigned=int.from_bytes(valueUnsigned.to_bytes(2, byteorder='big', signed=False), byteorder='big', signed=True)
            logger.info(f"Register: 0x{reg:02X} ({reg:3}), data: 0x{valueUnsigned:04X} ({valueSigned})")

    
def testRelays():
    """Test setting relay output"""
    paabSensor = PAABSensor(port="/dev/ttyUSB0",
                            address=MODBUS_ADDRESS,
                            enableWrites=True)
    paabSensor.setRegister(reg=0x32,value=5)
    paabSensor.setRegister(reg=0x3A,value=5)

    while(True):
        paabSensor.setRelays(relaysState=[0,0])
        paabSensor.setRelays(relaysState=[0,1])
        paabSensor.setRelays(relaysState=[1,0])
        paabSensor.setRelays(relaysState=[1,1])
    
    
def run():
 #   dumpAllRegisters()
 #   testRelays()
    testMeasure()
    
if __name__ =="__main__":
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-7s][%(name)s] %(message)s")
    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler("paab_sensor.log")
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(logging.WARNING)
    rootLogger.addHandler(fileHandler)
    
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    
    rootLogger.setLevel(logging.INFO)
    run()
     
