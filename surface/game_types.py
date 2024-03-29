from dataclasses import dataclass
from enum import Enum

class PieceType(Enum):
    seed = 0
    small = 1
    medium = 2
    large = 3
    sun = 4

class PlayerType(Enum):
    autumn = 0
    winter = 1
    none = 2

class MoveType(Enum):
    added = 0
    removed = 1
    bought_from_store = 2
    returned_to_store = 3

class FieldType(Enum):
    regular = 0
    store_winter = 1
    store_autumn = 2

class PointType(Enum):
    sun = 0
    score = 1

@dataclass
class Piece:
    player: PlayerType
    piece_type: PieceType

@dataclass
class Move:
    piece: Piece
    move_type: MoveType
    coordinates: tuple((int, int))

@dataclass
class Override:
    player: PlayerType
    points_type: PointType
    score_delta: int

@dataclass
class GameStateSummary:
    winter_sun_points: int = 0
    winter_score: int = 0

    autumn_sun_points: int = 0
    autumn_score: int = 0

    game_busy: bool = False
    center_next_reward: int = 19
    fertile_next_reward: int = 17
    edge_next_reward: int = 14

@dataclass
class PhotosynthesisField:
    level: int
    angle: int
    piece: Piece
    last_piece_in_round = None
