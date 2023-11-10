from pymodbus.client import ModbusSerialClient
# import time
import logging
import sys

MODBUS_ADDRESS = 2

logger = logging.getLogger(__name__)

class PAABSensor:
    def __init__(self, port, address):
        self.client = ModbusSerialClient(method='rtu',
                                         port=port,
                                         timeout=1,
                                         baudrate=9600)
        self._address = address
    def getRegister(self, reg):
        """Get register"""
        return self.client.read_holding_registers(reg-1,
                                                  count=1,
                                                  slave=self._address)

def run():
    for reg in range(1,30):
        paabSensor = PAABSensor(port="/dev/ttyUSB0",
                                address=MODBUS_ADDRESS)
        result=paabSensor.getRegister(reg=reg)
        logger.info(f"Register: {reg}, Result: {result}")

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
     
