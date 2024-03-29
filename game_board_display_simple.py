import cv2
import argparse
import cv2
import numpy as np
from surface.com import ZmqSubscriber, ZmqPublisher
from surface.misc import norm
from surface.game_board import PHOTOSYNTHESIS_FIELDS

CIRCLE_DIAMETER = 15
CIRCLE_COUNT = 7
CIRCLE_RADIUS_MARGIN = 0.2 # Percentage of circle diameter after prescaling.

def get_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--address", type=str, default="tcp://localhost:5556",
                        help="Address of the data.")

    parser.add_argument("--channel", type=str, default="detected_images",
                        help="Channel name.")
    
    parser.add_argument("--output_address", type=str, default="tcp://*:5557",
                        help="Address on which the data products will be published.")

    return parser.parse_args()

def main():
    args = get_arguments()

    rcv = ZmqSubscriber(args.address, args.channel)
    publisher = ZmqPublisher(args.output_address)
    
    displayed_size = False
    while 1:

        game_board_images = rcv.get_data()

        # Allows only for a single shape but I'm lazy
        img_size = game_board_images[0].shape[0] + 2

        max_angle = 0
        max_level = 0
        for field in PHOTOSYNTHESIS_FIELDS:
            max_angle = max((max_angle, field.angle))
            max_level = max((max_level, field.level))

        out = np.zeros((img_size*(max_level+1), img_size*(max_angle+1)), dtype=np.int16)
        if not displayed_size:
            displayed_size = True
            print(out.shape)

        img_size -= 2

        for i, img in enumerate(game_board_images):
            field = PHOTOSYNTHESIS_FIELDS[i]
            if img.shape[0] != img_size:
                img = cv2.resize(img, (img_size, img_size), interpolation=cv2.INTER_AREA)

            x1 = field.angle * img_size + 1
            x2 = (field.angle + 1) * img_size + 1

            y1 = field.level * img_size + 1
            y2 = (field.level + 1) * img_size + 1

            out[y1:y2, x1:x2] = img

            # Set border to +10
            out[y1-1, x1-1:x2] = 10
            out[y2, x1-1:x2] = 10
            out[y1-1:y2, x1-1] = 10
            out[y1-1:y2, x2] = 10

        publisher.send_data(out, args.channel)

if __name__ == "__main__":
    main()
