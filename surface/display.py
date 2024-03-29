import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation, rc
from . import touch_surface

class Display:
    def __init__(self, width=touch_surface.WIDTH, height=touch_surface.HEIGHT,
                 size_scale=0.6, vmin=-30, vmax=30, cmap="seismic", title=""):
        self.current_frame = None
        self.fig, self.ax = plt.subplots(figsize=(16*size_scale, 9*size_scale))
        self.fig.suptitle(title, fontsize=20)
        self.frame = np.zeros((width, height))
        self.im = self.ax.imshow(self.frame, vmin=vmin, vmax=vmax,  cmap=cmap)

    def start(self):
        def animate(_):
            self.im.set_array(self.frame)
            return [self.im]

        self.anim = animation.FuncAnimation(self.fig, animate, frames=None, interval=100, blit=True)
        plt.axis("off")
        plt.colorbar(self.im, fraction=0.0265, pad=0.03)
        plt.show()

