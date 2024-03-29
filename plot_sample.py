import argparse
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from surface.data import load_samples

def get_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("input_filepath", type=str,
                        help="Path to numpy file.")

    parser.add_argument("--baseline_path", type=str,
                        help="Optional path to numpy file containing baseline.")

    parser.add_argument("--vmax", type=float, default=255,
                        help="Maximum value on colorbar.")

    parser.add_argument("--vmin", type=float, default=0,
                        help="Minimum value on colorbar.")

    parser.add_argument("--cmap", type=str,
                        help="Colormap.")

    parser.add_argument("--title", type=str, default="",
                        help="Title of the graph.")

    parser.add_argument("--plot_scale", type=float, default=0.6,
                        help="Scale the plot up and down.")

    return parser.parse_args()

def main():
    args = get_arguments()

    fig, ax = plt.subplots(figsize=(16*args.plot_scale, 9*args.plot_scale))
    fig.suptitle(args.title, fontsize=20)

    frame = np.load(args.input_filepath)

    if args.baseline_path:
        if Path(args.baseline_path).is_dir():
            baseline =  load_samples(args.baseline_path)
            baseline = np.mean(baseline, axis=0)
        else:
            baseline = np.load(args.baseline_path)
        
        frame -= baseline

    im = ax.imshow(frame, vmin=args.vmin, vmax=args.vmax, cmap=args.cmap)

    plt.axis("off")
    plt.colorbar(im, fraction=0.0265, pad=0.03)
    plt.show()

if __name__ == "__main__":
    main()
