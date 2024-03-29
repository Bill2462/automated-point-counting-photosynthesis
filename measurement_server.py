from surface.touch_surface import TouchSurface
from surface.com import ZmqPublisher

ADDRESS = "tcp://*:5555"

def main():
    transmitter = ZmqPublisher()
    surface = TouchSurface()
    print("Measurement server started!")

    while 1:
        data = surface.read_raw_values()
        transmitter.send_data(data)

if __name__ == "__main__":
    main()
