import os
import argparse
import numpy as np
from surface.com import ZmqSubscriber
from tqdm import tqdm

def get_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("outdir", type=str,
                        help="Path to folder that will contain all directories.")

    parser.add_argument("--address", type=str, default="tcp://localhost:5555",
                        help="Address of the data.")

    parser.add_argument("--channel", type=str, default="default",
                        help="Channel name.")

    parser.add_argument("--interactive", action="store_true",
                        help="Interactive mode, used for capture of datasets.")

    parser.add_argument("-n", "--n_sample", type=int, default=1,
                        help="How many samples to take in interactive mode.")

    return parser.parse_args()

def main():
    args = get_arguments()

    if os.path.exists(args.outdir):
        print(f"{args.outdir} alread exists!")

    os.makedirs(args.outdir)

    if args.interactive:
        idx = 0
        while 1:
            os.system("clear")
            print(f"Current sample count: {idx}")
            print("Press enter to capture more and q to quit")
            x = input()
            if x == "q":
                break

            print("Capturing ...")
            for i in tqdm(range(args.n_sample)):
                rcv = ZmqSubscriber(args.address, args.channel)
                data = rcv.get_data()
                np.save(os.path.join(args.outdir, f"{idx}.npy"), data)
                idx += 1
        return

    rcv = ZmqSubscriber(args.address, args.channel)
    for idx in tqdm(range(args.n_sample)):
        data = rcv.get_data()
        np.save(os.path.join(args.outdir, f"{idx}.npy"), data)

if __name__ == "__main__":
    main()
