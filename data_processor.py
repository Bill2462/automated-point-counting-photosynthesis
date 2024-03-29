import copy
import argparse
import numpy as np
from surface.com import ZmqSubscriber, ZmqPublisher
from surface.touch_surface import DummyTouchSurface
from surface.baseline import NaiveBaseline
from surface.misc import align
from surface.game_board import PHOTOSYNTHESIS_FIELDS, crop_images_from_fields
from surface.pieces_classifier import PiecesClassifier
from surface.game_types import *
from surface.game_board import VotingBoardStateEstimator

def get_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input_address", type=str, default="tcp://localhost:5555",
                        help="Address from which raw measurements are taken.")
    
    parser.add_argument("--input_channel", type=str, default="default",
                        help="Channel from which input data will be taken.")

    parser.add_argument("--output_address", type=str, default="tcp://*:5556",
                        help="Address on which the data products will be published.")

    parser.add_argument("--dummy_data_path", type=str,
                        help="If this is set we will read samples from recording.")

    parser.add_argument("--n_avg_baseline", type=int, default=5,
                        help="Baseline is average of this many samples.")

    parser.add_argument("--pieces_model_filepath", type=str, default="models/pieces_model",
                        help="Path to the directory that stores model for pieces classification.")

    parser.add_argument("--sun_model_filepath", type=str, default="models/sun_model",
                        help="Path to the directory that stores model for sun classification.")
    
    return parser.parse_args()

def check_if_good_signal(imgs, min_n_pixel_active_threshold=0.06, pixel_active_threshold=5,
                         min_n_active_pixel_negative_threshold=0.3):
    is_good = []
    for img in imgs:
        img_flat = img.flatten()
        activation = np.abs(img_flat)
        n_above_threshold = (activation > pixel_active_threshold).sum()
        n_negative_active = ((img_flat < 0) & (activation > pixel_active_threshold)).sum()

        good_above_threshold = n_above_threshold > (len(img_flat)*min_n_pixel_active_threshold)
        good_negative_above_threshold = n_negative_active > (n_above_threshold*min_n_active_pixel_negative_threshold)

        is_good.append(good_above_threshold and good_negative_above_threshold)
    
    return is_good

def filter_preds(preds, is_good, idx_empty):
    preds_filtered = []
    for good, pred in zip(is_good, preds):
        if good:
            preds_filtered.append(pred)
        else:
            preds_filtered.append(idx_empty)

    return preds_filtered

def find_trigger(img_dt, threshold=12.0, n_vote=4):
    triggered = []
    how_many_triggered = 0
    for img in img_dt:
        img = np.abs(img)
        act = np.sum(img)/(img.shape[0] + img.shape[1])
        if act > threshold:
            triggered.append(n_vote)
            how_many_triggered += 1
        else:
            triggered.append(0)

    return np.array(triggered), how_many_triggered

def gate_predictions(preds, state, trigger):
    new_state = []
    for trig, pred, st in zip(trigger, preds, state):
        if (trig - 1) == 0:
            new_state.append(pred)
        else:
            new_state.append(st)

    return new_state

def main():
    args = get_arguments()

    publisher = ZmqPublisher(args.output_address)
    
    if args.dummy_data_path:
        subscriber = DummyTouchSurface(args.dummy_data_path)
    else:
        subscriber = ZmqSubscriber(args.input_address, args.input_channel)
    
    baseline_processor = NaiveBaseline(args.n_avg_baseline)
    pieces_model = PiecesClassifier(args.pieces_model_filepath)
    sun_model = PiecesClassifier(args.sun_model_filepath)

    for _ in range(args.n_avg_baseline):
        x = subscriber.get_data()
        x = align(x, -1)
        c_diff_last = baseline_processor(x)

    trigger = np.zeros(len(PHOTOSYNTHESIS_FIELDS), dtype=int)

    board_state = None
    sun_state = None

    state_estimator_board = VotingBoardStateEstimator(len(PHOTOSYNTHESIS_FIELDS) - 6)
    state_estimator_sun = VotingBoardStateEstimator(6)
    
    for _ in range(5):
        x = subscriber.get_data()
        x = align(x, -1)
        c_diff = baseline_processor(x)

        field_images = crop_images_from_fields(PHOTOSYNTHESIS_FIELDS, c_diff)
        c_diff_last = c_diff.copy()

        preds_board = pieces_model.forward(field_images[:-6])
        preds_sun = sun_model.forward(field_images[-6:])

        is_good = check_if_good_signal(field_images)
        preds_board = filter_preds(preds_board, is_good[:-6], len(pieces_model.classes)-1)
        preds_sun = filter_preds(preds_sun, is_good[-6:], 0)

        state_estimator_board.update_state(preds_board)
        state_estimator_sun.update_state(preds_sun)

    print("Processing pipeline started...")

    while 1:
        # Decrement trigger counter.
        for i in range(len(trigger)):
            if trigger[i] > 0:
                trigger[i] -= 1
        
        x = subscriber.get_data()
        x = align(x, -1)
        c_diff = baseline_processor(x)
        c_diff_dt = c_diff - c_diff_last

        field_images = crop_images_from_fields(PHOTOSYNTHESIS_FIELDS, c_diff)
        field_images_dt = crop_images_from_fields(PHOTOSYNTHESIS_FIELDS, c_diff_dt)
        c_diff_last = c_diff.copy()

        preds_board = pieces_model.forward(field_images[:-6])
        preds_sun = sun_model.forward(field_images[-6:])

        is_good = check_if_good_signal(field_images)
        preds_board = filter_preds(preds_board, is_good[:-6], len(pieces_model.classes)-1)
        preds_sun = filter_preds(preds_sun, is_good[-6:], 0)

        state_estimator_board.update_state(preds_board)
        state_estimator_sun.update_state(preds_sun)

        preds_board = state_estimator_board.state_estimate
        preds_sun = state_estimator_sun.state_estimate

        if board_state is None:
            board_state = copy.deepcopy(preds_board)
            sun_state = copy.deepcopy(preds_sun)
        
        board_state = gate_predictions(preds_board, board_state, trigger[:-6])
        sun_state = gate_predictions(preds_sun, sun_state, trigger[-6:])

        publisher.send_data(c_diff, "c_diff")
        publisher.send_data(field_images, "detected_images")
        publisher.send_data((board_state, sun_state), "model_predictions")

        new_trigger, how_many_triggered = find_trigger(field_images_dt)
        if how_many_triggered > 3:
            continue
        
        # Update trigger state.
        for i in range(len(trigger)):
            if new_trigger[i] > 0:
                trigger[i] = new_trigger[i]

if __name__ == "__main__":
    main()
