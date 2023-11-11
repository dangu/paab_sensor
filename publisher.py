import zmq
import sys
import logging

logger = logging.getLogger("publisher.py")

class Publisher:
    """ZMQ publisher"""
    def __init__(self):
        """Init"""
        pass

    def open(self, port):
        """Bind to a specific port"""
        context = zmq.Context()
        self._socket = context.socket(zmq.PUB)
        bind_address = f"tcp://0.0.0.0:{port}"
        logging.info(f"Binding to {bind_address} ...")
        self._socket.bind(bind_address)

    def send(self, data):
        """Send data"""
        self._socket.send_pyobj(data)

def run(port):
    """Test publisher"""
    publisher = Publisher()
    publisher.open(port=port)


    logger.info("ZMQ Publisher test")
    for x in range(100):
        publisher.send(f"{x}")

if __name__=='__main__':
    run(port=sys.argv[1])

