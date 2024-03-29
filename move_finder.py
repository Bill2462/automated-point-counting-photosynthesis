import os
import time
import joblib
import argparse
import numpy as np
from surface.com import ZmqSubscriber, ZmqPublisher
from surface.game_board import MovesDetector

def get_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input_address_preds", type=str, default="tcp://localhost:5556",
                        help="Address from which model predictions will be taken.")

    parser.add_argument("--input_channel_preds", type=str, default="model_predictions",
                        help="Channel from which input data will be taken.")

    parser.add_argument("--output_address", type=str, default="tcp://*:5558",
                        help="Address on which the data products will be published.")

    parser.add_argument("--log_file", type=str, default="log_move_finder.csv")
    
    return parser.parse_args()

def run_move_detection_pipeline(subscriber, moves_detector):
    preds_board, preds_sun = subscriber.get_data()
    return moves_detector.detect_moves(preds_board, preds_sun)

def main():
    args = get_arguments()

    publisher = ZmqPublisher(args.output_address)
    subscriber_preds = ZmqSubscriber(args.input_address_preds, args.input_channel_preds)

    classes = np.array(joblib.load("models/pieces_model/classes.bin"))
    moves_detector = MovesDetector(classes)

    if not os.path.exists(args.log_file):
        with open(args.log_file, "w") as f:
            f.write("time, move_type, piece_type, player, level, angle\n")

    print("Running")
    while 1:
        moves = run_move_detection_pipeline(subscriber_preds, moves_detector)
        for move in moves:
            print(f"Move: {move.move_type.name}, piece: {move.piece.piece_type.name}, player: {move.piece.player.name}, coordinates: {move.coordinates}")
            publisher.send_data(move, "moves")
        
            with open(args.log_file, "a") as f:
                f.write(f"{int(time.time())}, {move.move_type.name},{move.piece.piece_type.name},{move.piece.player.name},{move.coordinates[0]}, {move.coordinates[1]}\n")

if __name__ == "__main__":
    main()
