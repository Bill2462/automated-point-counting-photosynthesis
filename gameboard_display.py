import cv2
import argparse
import numpy as np
from surface.com import ZmqSubscriber, ZmqPublisher
from surface.misc import norm
from surface.game_types import *

def get_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--address", type=str, default="tcp://localhost:5560",
                        help="Address of the data.")

    parser.add_argument("--channel", type=str, default="board_state",
                        help="Channel name.")
    
    parser.add_argument("--board_img", type=str, default="assets/board_lines_bleak.jpg",
                        help="Channel name.")

    return parser.parse_args()

def piece_to_txt(piece: PieceType):
    if piece == PieceType.seed:
        piece_txt = "SD"
    elif piece == PieceType.small:
        piece_txt = "SM"
    elif piece == PieceType.medium:
        piece_txt = "M"
    elif piece == PieceType.large:
        piece_txt = "L"
    elif piece == PieceType.sun:
        piece_txt = "S"
    else:
        piece_txt = ""
    
    return piece_txt

def show_piece(img, pos, player: PlayerType, piece: PieceType):
    txt = piece_to_txt(piece)
    font = cv2.FONT_HERSHEY_SIMPLEX
    org = (pos[1], pos[0])
    fontScale = 1

    if player == PlayerType.autumn:
        color = (0, 122, 255)
    elif player == PlayerType.winter:
        color = (255, 163, 0)
    else:
        color = (0, 0, 255)

    thickness = 2

    return cv2.putText(img, txt, org, font,
                    fontScale, color, thickness, cv2.LINE_AA)

IMG_POSITIONS = (
    (963, 554),

    (819, 558),
    (896, 434),
    (1037, 435),
    (1107, 554),
    (1034, 681),
    (894, 680),

    (668, 558),
    (747, 435),
    (818, 311),
    (962, 311),
    (1106, 314),
    (1176, 437),
    (1248, 557),
    (1176, 678),
    (1103, 798),
    (960, 801),
    (815, 804),
    (744, 680),

    (516, 558),
    (594, 432),
    (668, 308),
    (743, 185),
    (893, 186),
    (1043, 191),
    (1181, 191),
    (1253, 312),
    (1322, 437),
    (1400, 554),
    (1320, 677),
    (1248, 800),
    (1176, 923),
    (1034, 923),
    (888, 924),
    (740, 926),
    (666, 804),
    (593, 683),
    
    (930, 2040),
    (1074, 2040),
    (1227, 2036),
    (1379, 2042),
    (891, 1835),
    (1061, 1835),
    (1235, 1833),
    (1412, 1832),
    (939, 1592),
    (1149, 1587),
    (1368, 1586),
    (1004, 1293),
    (1301, 1295),

    (650, 1269),
    (492, 1271),
    (339, 1271),
    (191, 1269),
    (680, 1478),
    (506, 1473),
    (329, 1475),
    (155, 1473),
    (633, 1724),
    (416, 1721),
    (195, 1721),
    (566, 2021),
    (273, 2015),

    (391, 554),
    (691, 87),
    (1235, 102),
    (1486, 548),
    (1228, 991),
    (689, 1018)
)

def main():
    args = get_arguments()

    board_image_original = cv2.imread(args.board_img)

    rcv = ZmqSubscriber(args.address, args.channel)

    while 1:
        board_img = board_image_original.copy()
        game_state = rcv.get_data()

        for i, field in enumerate(game_state):
            if field.piece is None:
                continue

            board_img = show_piece(board_img, IMG_POSITIONS[i], field.piece.player, field.piece.piece_type)
        
        board_img = cv2.resize(board_img, None, fx=0.6, fy=0.6)
        cv2.imshow("Board preview", board_img)
        cv2.waitKey(10)

if __name__ == "__main__":
    main()
