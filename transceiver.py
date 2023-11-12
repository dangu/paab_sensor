"""Receive data from the paab pressure sensur and send the data over zmq"""
import paab_sensor
import publisher
import logging
import sys
import time
import json
import statistics

class Transceiver:
    """Transmitter/receiver class"""
    def __init__(self,
                 filterTime,
                 location,
                 onlySendWhenChanged):
        """Init"""
        self._dataDictFilt = {'waterLevel': []}
        self._lastValueDict = {'waterLevel':None}
        self._filterTimeSecs = filterTime
        self._location = location
        self._t0 = 0
        self._onlySendWhenChanged = onlySendWhenChanged

        self._logger = logging.getLogger("Transceiver")
        
    def _filterAndSendData(self,name,value):
        """Get data from sensor and send over TCP/IP"""
        dataDict = {}
        decimals=3
        self._dataDictFilt[name].append(value)

        tNow = time.time()
        if (tNow-self._t0) > self._filterTimeSecs:
            self._logger.debug("Filter time reached")
            self._t0 = tNow
            sampleDict = {}
            valueChanged = False
            for key, valueList in self._dataDictFilt.items():
                valFilt = round(statistics.median(valueList),3)
                sampleDict[key] = valFilt
                if self._lastValueDict[key] != valFilt:
                    valueChanged = True
                self._lastValueDict[key] = valFilt
                self._dataDictFilt[key] = []
                self._logger.info(f"{key}: {valueList} => {valFilt})")

            if not self._onlySendWhenChanged or valueChanged:
                packetDict ={'name': 'waterLevel',
                             'tags': {'location':self._location},
                             'dataDict': sampleDict}
                self._publisher.send(packetDict)
                self._logger.info("Send changed data")
        
    def connectAndRun(self,
                      port,
                      baudrate,
                      address,
                      zmqPort,
                      sampleTime):
        """Connect to port and run receiver"""
        paabSensor = paab_sensor.PAABSensor(port=port,
                                baudrate=baudrate,
                                address=address)

        self._publisher = publisher.Publisher()
        self._publisher.open(port=zmqPort)


        while(True):
            try:
                waterLevelInt=paabSensor.getReg1Value()
                # Use water level in meters
                waterLevel=waterLevelInt/1000.0
                self._filterAndSendData(name="waterLevel",
                                        value=waterLevel)
                time.sleep(sampleTime)
            except ValueError as e:
                self._logger.error(f"Error reading sensor data: {e}")
                time.sleep(5)
def run():
    """Run main functionality"""
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-7s][%(name)s] %(message)s")
    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler("transceiver.log")
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(logging.WARNING)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(logging.DEBUG)
    rootLogger.addHandler(consoleHandler)

    rootLogger.setLevel(logging.INFO)

    # Open configuration file
    cfgFileName = "config.json"
    with open(cfgFileName, 'r') as cfgFile:
        config = json.load(cfgFile)

    rootLogger.info(f"Starting using this configuration:\n{config}")
    
    sampleTime=int(config['measurement']['sampleTime'])
    filterTime=int(config['measurement']['filterTime'])
    location=config['measurement']['location']
    port=config['measurement']['port']
    baudrate=config['measurement']['baudrate']
    address=int(config['measurement']['modbusAddress'])
    onlySendWhenChanged = config['measurement']['onlySendWhenChanged']=='1'
    zmqPort=config['network']['zmqPort']

    
    transceiver=Transceiver(filterTime=filterTime,
                            location=location,
                            onlySendWhenChanged=onlySendWhenChanged)
    transceiver.connectAndRun(port=port,
                              baudrate=baudrate,
                              address=address,
                              zmqPort=zmqPort,
                              sampleTime=sampleTime)
                            
    
if __name__=="__main__":
    run()
    
