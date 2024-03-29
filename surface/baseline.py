import numpy as np

class NaiveBaseline:
    def __init__(self, n_samples):
        self.n_samples = n_samples
        self.baseline = None
        self.buf = None

    def __call__(self, x):
        if self.baseline is None:
            if self.buf is None:
                self.idx = 0
                self.buf = np.empty([self.n_samples] + list(x.shape), dtype=np.float32)
            
            self.buf[self.idx] = x
            self.idx += 1

            if self.idx == self.n_samples:
                self.baseline = np.mean(self.buf, axis=0)
                del self.buf
                del self.idx
            else:
                return np.zeros(x.shape, dtype=x.dtype)
        
        return x - self.baseline
