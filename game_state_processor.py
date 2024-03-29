import os
import time
import argparse
from surface.com import ZmqSubscriber, ZmqPublisher
from surface.game_board import (
    PhotosynthesisGame,
    REWARDS_CENTER,
    REWARDS_FERTILE,
    REWARDS_EDGE
)
from surface.game_types import *

def get_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input_address_supervisor", type=str, default="tcp://localhost:5559",
                        help="Address from which supervisor commands will be taken.")

    parser.add_argument("--input_channel_commands", type=str, default="commands",
                        help="Channel from which supervisor commands were taken.")
    
    parser.add_argument("--output_address", type=str, default="tcp://*:5560",
                        help="Address on which the data products will be published.")
    
    parser.add_argument("--log_file", type=str, default="log_game_state_processor.csv")
    
    return parser.parse_args()

def main():
    args = get_arguments()

    subscriber_moves = ZmqSubscriber(args.input_address_supervisor, args.input_channel_commands)
    publisher_points = ZmqPublisher(args.output_address)
    game = PhotosynthesisGame()

    if not os.path.exists(args.log_file):
        with open(args.log_file, "w") as f:
            f.write("time, move_type, piece_type, player, level, angle\n")

    is_busy = False

    while 1:
        packet = subscriber_moves.get_data()
        if packet["cmd"] == "move":
            data = packet["data"]
            game.apply_move(data)

            with open(args.log_file, "a") as f:
                move = data
                f.write(f"{int(time.time())}, {move.move_type.name},{move.piece.piece_type.name},{move.piece.player.name},{move.coordinates[0]}, {move.coordinates[1]}\n")

        elif packet["cmd"] == "override":
            data = packet["data"]
            game.apply_point_override(data)
        elif packet["cmd"] == "end_game":
            game.end_game()
        elif packet["cmd"] == "update_busy_flag":
            is_busy = packet["data"]
            data = f"Is busy_updated to {is_busy}"

        print(int(time.time()), data)
        
        publisher_points.send_data(GameStateSummary(game.winter_player.sun_points, game.winter_player.score,
                                                game.autumn_player.sun_points, game.autumn_player.score,
                                                is_busy,
                                                REWARDS_CENTER[game.trees_cut_center_count],
                                                REWARDS_FERTILE[game.trees_cut_fertile_count],
                                                REWARDS_EDGE[game.trees_cut_edge_count]), "point_summary")
        
        publisher_points.send_data(game.gameboard_fields, "board_state")

if __name__ == "__main__":
    main()
