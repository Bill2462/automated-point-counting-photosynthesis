import numpy as np
import usb.core
import usb.util
import numpy as np
from .data import load_samples
from time import sleep

WIDTH = 240
HEIGHT = 136

class TouchSurface:
    def __init__(self):
        self.send_msg = np.zeros([64,], dtype= np.ubyte)
        self.send_msg[0] = 3
        self.send_msg[1] = 83

        self.connect()

    def connect(self):
        self.dev = usb.core.find(idVendor=0x0547, idProduct=0x3003)

        if self.dev is None:
            raise ValueError("Device not found")
                
        # Fix error on linux caused by touch driver taking coontrol of the foil.
        if self.dev.is_kernel_driver_active(0):
            try:
                self.dev.detach_kernel_driver(0)
            except usb.core.USBError as e:
                raise Exception(f"Could not detatch kernel driver from interface '{e}'")

        self.dev.set_configuration()
        self.cfg = self.dev[0]

        self.dev.ctrl_transfer(bmRequestType=0x21, bRequest=0x09, wValue = 0x303, wIndex=0x00, data_or_wLength=bytes(self.send_msg[:3]), timeout = 1000)

    def read_raw_values(self, n_retries=3):
        temp = []
        for i in range(510):
            # Sometimes read randomly fails. When it does just retry.
            for try_n in range(n_retries):
                try:
                    msg = self.dev.ctrl_transfer(bmRequestType=0xa1, bRequest=0x01, wValue=0x303, wIndex=0x00, data_or_wLength=bytes(self.send_msg), timeout=1000)
                    temp.append(msg)
                    break
                except usb.core.USBTimeoutError as e:
                    if try_n == n_retries-1:
                        raise e
        
        buffer = np.asarray(temp, dtype=np.ubyte).flatten()
        raw_view = ((85 + buffer) ^ 85).astype(np.ubyte).reshape(HEIGHT, WIDTH)

        return raw_view

    def disconnect(self):
        self.dev.reset()

class DummyTouchSurface:
    def __init__(self, datapath: str, fps=1):
        self.delay = 1/fps
        self.samples = load_samples(datapath)
        self.idx = 0
        self.n_samples = len(self.samples)
    
    def get_data(self):
        sleep(self.delay)
        sample = self.samples[self.idx]
       
        self.idx += 1
        if self.idx == self.n_samples:
            self.idx = 0

        return sample
