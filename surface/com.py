import zmq

class ZmqSubscriber:
    def __init__(self, address="tcp://localhost:5555", channel="default"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(address)
        self.socket.setsockopt(zmq.SUBSCRIBE, channel.encode("ascii"))

    def get_data(self):
        self.socket.recv_string()
        return self.socket.recv_pyobj()

class ZmqPublisher:
    def __init__(self, address="tcp://*:5555"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(address)

    def send_data(self, obj, channel="default"):
        self.socket.send_string(channel, zmq.SNDMORE)
        self.socket.send_pyobj(obj)
