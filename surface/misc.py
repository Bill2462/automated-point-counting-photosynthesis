import cv2
import numpy as np
from . import touch_surface

def measure_average_value(receiver, n_avg=10, width=touch_surface.WIDTH, height=touch_surface.HEIGHT):
    buf = np.empty((n_avg, width, height), dtype=np.uint8)
    for i in range(n_avg):
        buf[i] = receiver.get_data()

    return np.mean(buf, axis=0)

def get_n_samples(receiver, n):
    out = np.empty((n, touch_surface.WIDTH, touch_surface.HEIGHT), dtype=np.uint8)
    
    for i in range(n):
        out[i] = receiver.get_data()

    return out

def normalize_size(imgs, target_size):
    out = np.empty((len(imgs), target_size[0], target_size[1]), dtype=np.float32)

    for i, img in enumerate((imgs)):
        if img.shape[0] != target_size[0] or img.shape[1] != target_size[1]:
            out[i] = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
        else:
            out[i] = img

    return out

def align(img, min_loc_offset=0):
    offset = -(np.argmin(img, axis=1)[-1]) + min_loc_offset
    return np.roll(img, offset, axis=1)

def pos_neg_sep(x):
   positive = np.copy(x)
   negative = np.copy(x)

   positive[positive < 0.0] = 0.0
   negative[negative > 0.0] = 0.0
   negative = np.abs(negative)

   return [positive, negative]

def norm(x):
   return ((x-np.min(x))/(np.max(x)-np.min(x)) )* 255.
