import argparse
import threading
from surface.com import ZmqSubscriber
from surface.display import Display
from surface.touch_surface import WIDTH, HEIGHT

def get_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--address", type=str, default="tcp://localhost:5555",
                        help="Address of the data.")

    parser.add_argument("--channel", type=str, default="default",
                        help="Channel name.")

    parser.add_argument("--vmax", type=float, default=255,
                        help="Maximum value on colorbar.")

    parser.add_argument("--vmin", type=float, default=0,
                        help="Minimum value on colorbar.")

    parser.add_argument("--width", type=int, default=WIDTH,
                        help="Width of the display.")

    parser.add_argument("--height", type=int, default=HEIGHT,
                        help="Heidht of the display.")

    parser.add_argument("--cmap", type=str,
                        help="Colormap name (see matplotlib).")
    
    parser.add_argument("--idx", type=int,
                        help="When tuple or list is received we can set which one is displayed.")

    parser.add_argument("--title",  type=str, default="",
                        help="Title of the graph.")

    return parser.parse_args()

class DisplayWorker:
    def __init__(self, display, receiver, data_idx=None):
         self.display = display
         self.receiver = receiver
         self.data_idx = data_idx

    def start(self):
        def wrapper():
            while 1:
                data = self.receiver.get_data()
                if isinstance(data, tuple) or isinstance(data, list):
                    if self.data_idx:
                        data = data[self.data_idx]
                    else:
                        data = data[0]
                
                self.display.frame = data
        self.thread = threading.Thread(target=wrapper)
        self.thread.start()

def main():
    args = get_arguments()

    rcv = ZmqSubscriber(args.address, args.channel)

    display = Display(args.height, args.width, vmin=args.vmin, vmax=args.vmax, cmap=args.cmap, title=args.title)
    display_worker = DisplayWorker(display, rcv, args.idx)

    print("Starting display worker")
    print("Please exit matplotlib window first!")
    display_worker.start()
    display.start()

if __name__ == "__main__":
    main()
