import math
import numpy as np
from dataclasses import dataclass
from enum import Enum
from .game_types import *

class Field:
    def __init__(self, level, angle, center_y, center_x, r=8):
        self.level = level
        self.angle = angle
        self.r = r

        # Coordinates
        self.coords = np.array(
            [[center_y, center_x], 
             [center_y - r, center_x - r], # left upper corner
             [center_y + r, center_x + r]], # Right down corner
            dtype=np.int16
        )
    
    def crop_image(self, img):
        return img[self.coords[1][0]:self.coords[2][0], self.coords[1][1]:self.coords[2][1]]

PHOTOSYNTHESIS_FIELDS = (
        # Game board fields (all fields are numbered counter clockwise where field 0 is on the bottom of the board
        # when you are sitting in the chair of the yellow player) 

        # Center
        Field(0, 0, 62, 137),

        # Level 1
        Field(1, 0, 78, 138),
        Field(1, 1, 70, 125),
        Field(1, 2, 56, 125),
        Field(1, 3, 48, 138),
        Field(1, 4, 55, 150),
        Field(1, 5, 71, 150),

        # Level 2
        Field(2, 0, 93, 138),
        Field(2, 1, 86, 124),
        Field(2, 2, 78, 111),
        Field(2, 3, 63, 111),
        Field(2, 4, 47, 111),
        Field(2, 5, 40, 124),
        Field(2, 6, 32, 138),
        Field(2, 7, 40, 150),
        Field(2, 8, 48, 164),
        Field(2, 9, 62, 163),
        Field(2, 10, 78, 164),
        Field(2, 11, 85, 150),

        # Level 3
        Field(3, 0, 108, 138),
        Field(3, 1, 100, 124),
        Field(3, 2, 93, 111),
        Field(3, 3, 86, 98),
        Field(3, 4, 70, 97),
        Field(3, 5, 55, 98),
        Field(3, 6, 40, 98),
        Field(3, 7, 32, 110),
        Field(3, 8, 25, 124),
        Field(3, 9, 17, 137),
        Field(3, 10, 25, 150),
        Field(3, 11, 32, 164),
        Field(3, 12, 40, 177),
        Field(3, 13, 55, 177),
        Field(3, 14, 70, 177),
        Field(3, 15, 85, 177),
        Field(3, 16, 93, 164),
        Field(3, 17, 100, 151),

        # Player 1 shop (yellow)
        Field(4, 0, 117, 54, r=3),
        Field(4, 1, 108, 54, r=3),
        Field(4, 2, 99, 55, r=3),
        Field(4, 3, 91, 55, r=3),

        Field(4, 4, 119, 43, r=5),
        Field(4, 5, 109, 43, r=5),
        Field(4, 6, 99, 43, r=5),
        Field(4, 7, 88, 43, r=5),

        Field(4, 8, 116, 29, r=6),
        Field(4, 9, 103, 29, r=6),
        Field(4, 10, 91, 29, r=6),

        Field(4, 11, 112, 12),
        Field(4, 12, 95, 12),

        # Player 2 shop (blue)
        Field(5, 0, 7, 12, r=3),
        Field(5, 1, 16, 12, r=3),
        Field(5, 2, 25, 11, r=3),
        Field(5, 3, 33, 12, r=3),

        Field(5, 4, 6, 24, r=5),
        Field(5, 5, 16, 23, r=5),
        Field(5, 6, 26, 24, r=5),
        Field(5, 7, 36, 23, r=5),

        Field(5, 8, 9, 38, r=6),
        Field(5, 9, 21, 38, r=6),
        Field(5, 10, 33, 37, r=6),

        Field(5, 11, 13, 54),
        Field(5, 12, 29, 55),

        # Sun corners (bottom, we count the corners in the same way we count the fields, counterclockwise
        # starting at the bottom of the board from the point of view of blue player)
        Field(6, 0, 121, 137),
        Field(6, 1, 92, 85),
        Field(6, 2, 34, 86),
        Field(6, 3, 4, 136, r=4),
        Field(6, 4, 32, 189),
        Field(6, 5, 92, 189)
)

PHOTOSYNTHESIS_LINES = (
    # Location  0
    (
        ((3, 15), (3, 14), (3, 13), (3, 12)),
        ((3, 16), (2, 10), (2, 9), (2, 8), (3, 11)),
        ((3, 17), (2, 11), (1, 5), (1, 4), (2, 7), (2, 10)),
        ((3, 0), (2, 0), (1, 0), (0, 0), (1, 3), (2, 6), (3, 10)),
        ((3, 1), (2, 1), (1, 1), (1, 2), (2, 5), (3, 8)),
        ((3, 2), (2, 2), (2, 3), (2, 4), (3, 7)),
        ((3, 3), (3, 4), (3, 5), (3, 6))
    ),

    (
        ((3, 0), (3, 17), (3, 16), (3, 15)),
        ((3, 1), (2, 0), (2, 11), (2, 10), (3, 14)),
        ((3, 2), (2, 1), (1, 0), (1, 5), (2, 9), (3, 13)),
        ((3, 3), (2, 2), (1, 1), (0, 0), (1, 4), (2, 8), (3, 12)),
        ((3, 4), (2, 3), (1, 2), (1, 3), (2, 7), (3, 11)),
        ((3, 5), (2, 4), (2, 5), (2, 6), (3, 10)),
        ((3, 6), (3, 7), (3, 8), (3, 9))
    ),
    (
        ((3, 3), (3, 2), (3, 1), (3, 0)),
        ((3, 4), (2, 2), (2, 1), (2, 0), (3, 17)),
        ((3, 5), (2, 3), (1, 1), (1, 0), (2, 11), (3, 16)),
        ((3, 6), (2, 4), (1, 2), (0, 0), (1, 5), (2, 10), (3, 15)),
        ((3, 7), (2, 5), (1, 3), (1, 4), (2, 9), (3, 14)),
        ((3, 8), (2, 6), (2, 7), (2, 8), (3, 13)),
        ((3, 9), (3, 10), (3, 11), (3, 12))
    ),
    (
        ((3, 6), (3, 5), (3, 4), (3, 3)),
        ((3, 7), (2, 4), (2, 3), (2, 2), (3, 2)),
        ((3, 8), (2, 5), (1, 2), (1, 1), (2, 1), (3, 1)),
        ((3, 9), (2, 6), (1, 3), (0, 0), (1, 0), (2, 0), (3, 0)),
        ((3, 10), (2, 7), (1, 4), (1, 5), (2, 11), (3, 17)),
        ((3, 11), (2, 8), (2, 9), (2, 10), (3, 16)),
        ((3, 12), (3, 13), (3, 14), (3, 15))
    ),
    (
        ((3, 9), (3, 8), (3, 7), (3, 6)),
        ((3, 10), (2, 6), (2, 5), (2, 4), (3, 5)),
        ((3, 11), (2, 7), (1, 3), (1, 2), (2, 3), (3, 4)),
        ((3, 12), (2, 8), (1, 4), (0, 0), (1, 1), (2, 2), (3, 3)),
        ((3, 13), (2, 9), (1, 5), (1, 0), (2, 1), (3, 2)),
        ((3, 14), (2, 10), (2, 11), (2, 0), (3, 1)),
        ((3, 15), (3, 16), (3, 17), (3, 0))
    ),
    (
        ((3, 12), (3, 11), (3, 10), (3, 9)),
        ((3, 13), (2, 8), (2, 7), (2, 6), (3, 8)),
        ((3, 14), (2, 9), (1, 4), (1, 3), (2, 5), (3, 7)),
        ((3, 15), (2, 10), (1, 5), (0, 0), (1, 2), (2, 4), (3, 6)),
        ((3, 16), (2, 11), (1, 0), (1, 1), (2, 3), (3, 5)),
        ((3, 17), (2, 0), (2, 1), (2, 2), (3, 4)),
        ((3, 0), (3, 1), (3, 2), (3, 3))
    )
)

REWARDS_CENTER = (19, 18, 18, 17, 17, 0, 0, 0, 0)
REWARDS_FERTILE = (17, 16, 14, 14, 13, 13, 0, 0, 0, 0)
REWARDS_EDGE = (14, 14, 13, 13, 13, 12, 12, 12, 12, 0, 0, 0, 0)

def crop_images_from_fields(fields, img):
    images = []
    for field in fields:
        images.append(field.crop_image(img))
    
    return images

class PhotosynthesisGameStore:
    def __init__(self):
        self.seed_count = 4
        self.small_count = 4
        self.medium_count = 3
        self.large_count = 2
    
    def print(self):
        print(f"self.seed_count: {self.seed_count}, self.small_count: {self.small_count}, self.medium_count:{self.medium_count}, self.large_count:{self.large_count}")

    def buy(self, piece: Piece):
        cost = self._perform_transaction(piece, True)
        return cost
    
    def return_piece(self, piece: Piece):
        self._perform_transaction(piece, False)

    def _perform_transaction(self, piece: Piece, take: bool):
        """
        Returns cost of taking
        """
        if piece.piece_type == PieceType["seed"]:
            self.seed_count += 1 - (2*take)
            if self.seed_count <= 1:
                return 2
            return 1

        elif piece.piece_type == PieceType["small"]:
            self.small_count += 1 - (2*take)
            if self.small_count <= 1:
                return 3
            return 2
        
        elif piece.piece_type == PieceType["medium"]:
            self.medium_count += 1 - (2*take)
            if self.medium_count == 0:
                return 4
            return 3
        
        elif piece.piece_type == PieceType["large"]:
            self.large_count += 1 - (2*take)
            if self.large_count == 0:
                return 5
            return 4

class Player:
    sun_points = 0
    score = 0

    def __init__(self):
        self.store = PhotosynthesisGameStore()

class PhotosynthesisGame:
    def __init__(self):
        self.gameboard_fields = []
        self.first_round = True

        for field in PHOTOSYNTHESIS_FIELDS:
            self.gameboard_fields.append(PhotosynthesisField(field.level, field.angle, None))
        
        # Initialize store
        self._initialize_store()

        self.autumn_player = Player()
        self.winter_player = Player()
        
        self.trees_cut_center_count = 0
        self.trees_cut_fertile_count = 0
        self.trees_cut_edge_count = 0

    def _initialize_store(self):
        self._field_from_coords(4, 0).piece = Piece(PlayerType.autumn, PieceType.seed)
        self._field_from_coords(4, 1).piece = Piece(PlayerType.autumn, PieceType.seed)
        self._field_from_coords(4, 2).piece = Piece(PlayerType.autumn, PieceType.seed)
        self._field_from_coords(4, 3).piece = Piece(PlayerType.autumn, PieceType.seed)

        self._field_from_coords(4, 4).piece = Piece(PlayerType.autumn, PieceType.small)
        self._field_from_coords(4, 5).piece = Piece(PlayerType.autumn, PieceType.small)
        self._field_from_coords(4, 6).piece = Piece(PlayerType.autumn, PieceType.small)
        self._field_from_coords(4, 7).piece = Piece(PlayerType.autumn, PieceType.small)

        self._field_from_coords(4, 8).piece = Piece(PlayerType.autumn, PieceType.medium)
        self._field_from_coords(4, 9).piece = Piece(PlayerType.autumn, PieceType.medium)
        self._field_from_coords(4, 10).piece = Piece(PlayerType.autumn, PieceType.medium)

        self._field_from_coords(4, 11).piece = Piece(PlayerType.autumn, PieceType.large)
        self._field_from_coords(4, 12).piece = Piece(PlayerType.autumn, PieceType.large)

        self._field_from_coords(5, 0).piece = Piece(PlayerType.winter, PieceType.seed)
        self._field_from_coords(5, 1).piece = Piece(PlayerType.winter, PieceType.seed)
        self._field_from_coords(5, 2).piece = Piece(PlayerType.winter, PieceType.seed)
        self._field_from_coords(5, 3).piece = Piece(PlayerType.winter, PieceType.seed)

        self._field_from_coords(5, 4).piece = Piece(PlayerType.winter, PieceType.small)
        self._field_from_coords(5, 5).piece = Piece(PlayerType.winter, PieceType.small)
        self._field_from_coords(5, 6).piece = Piece(PlayerType.winter, PieceType.small)
        self._field_from_coords(5, 7).piece = Piece(PlayerType.winter, PieceType.small)

        self._field_from_coords(5, 8).piece = Piece(PlayerType.winter, PieceType.medium)
        self._field_from_coords(5, 9).piece = Piece(PlayerType.winter, PieceType.medium)
        self._field_from_coords(5, 10).piece = Piece(PlayerType.winter, PieceType.medium)

        self._field_from_coords(5, 11).piece = Piece(PlayerType.winter, PieceType.large)
        self._field_from_coords(5, 12).piece = Piece(PlayerType.winter, PieceType.large)

    def _player_from_move(self, move: Move):
        if move.piece.player == PlayerType["winter"]:
            return self.winter_player
        
        return self.autumn_player

    def _field_from_coords(self, level: int, angle: int):
        for field in self.gameboard_fields:
            if field.angle == angle and field.level == level:
                return field

    def _add_to_board(self, move: Move):
        player = self._player_from_move(move)
        field = self._field_from_coords(move.coordinates[0], move.coordinates[1])
        field.piece = move.piece
        
        if self.first_round:
            return # Do not remove points.

        # Newly placed piece.
        if field.last_piece_in_round is None:
            player.sun_points -= 1
            return
        
        # Calculate upgrade cost.
        if field.last_piece_in_round.piece_type == PieceType["seed"]:
            player.sun_points -= 1

        elif field.last_piece_in_round.piece_type == PieceType["small"]:
            player.sun_points -= 2

        elif field.last_piece_in_round.piece_type == PieceType["medium"]:
            player.sun_points -= 3

    def _end_round(self, move):
        x = 0
        # Get lines depending on the position of the sun.
        lines = PHOTOSYNTHESIS_LINES[move.coordinates[1]]
        self.first_round = False
        for line in lines:
            pieces = []
            for line_field in line:
                for field in self.gameboard_fields:
                    if field.angle == line_field[1] and field.level == line_field[0]:
                        pieces.append(field.piece)

            occlussions = []
            @dataclass
            class Occlusion:
                ends: int
                height: int
            
            def not_ocluded(occlussions, idx, height):
                print(f"Detecting occlusion for idx: {idx}, height: {height}")
                for occlussion in occlussions:
                    if occlussion.ends >= idx:
                        if occlussion.height >= height:
                            return False

                return True

            for i, piece in enumerate(pieces):
                if piece is None:
                    x += 1
                    continue
                
                if piece.piece_type == PieceType["small"]:
                    if not_ocluded(occlussions, i, 1):
                        if piece.player == PlayerType["winter"]:
                            self.winter_player.sun_points += 1
                        else:
                            self.autumn_player.sun_points += 1

                    occlussions.append(Occlusion(i + 1, 1))

                if piece.piece_type == PieceType["medium"]:
                    if not_ocluded(occlussions, i, 2):
                        if piece.player == PlayerType["winter"]:
                            self.winter_player.sun_points += 2
                        else:
                            self.autumn_player.sun_points += 2

                    occlussions.append(Occlusion(i + 2, 2))

                if piece.piece_type == PieceType["large"]:
                    if not_ocluded(occlussions, i, 3):
                        if piece.player == PlayerType["winter"]:
                            self.winter_player.sun_points += 3
                        else:
                            self.autumn_player.sun_points += 3
                    
                    occlussions.append(Occlusion(i + 3, 3))

    def apply_point_override(self, override: Override):
        if override.player == PlayerType.winter:
            player = self.winter_player
        elif override.player == PlayerType.autumn:
            player = self.autumn_player
        
        if override.points_type == PointType.score:
            player.score += override.score_delta
        elif override.points_type == PointType.sun:
            player.sun_points += override.score_delta

    def _remove_from_board(self, move: Move):
        player = self._player_from_move(move)
        field = self._field_from_coords(move.coordinates[0], move.coordinates[1])
        
        if field is None:
            return
        
        if field.piece is None:
            return
        
        # Cutting down    
        if field.piece.piece_type == PieceType["large"]:
            player.sun_points -= 4
            if move.coordinates[0] == 0 or move.coordinates[0] == 1:
                player.score += REWARDS_CENTER[self.trees_cut_center_count]
                self.trees_cut_center_count += 1
            elif move.coordinates[0] == 2:
                player.score += REWARDS_FERTILE[self.trees_cut_fertile_count]
                self.trees_cut_fertile_count += 1
            elif move.coordinates[0] == 3:
                player.score += REWARDS_EDGE[self.trees_cut_edge_count]
                self.trees_cut_edge_count += 1
        
        field.last_piece_in_round = field.piece
        field.piece = None

    def _buy_from_store(self, move: Move):
        player = self._player_from_move(move)
        cost = player.store.buy(move.piece)
        player.sun_points -= cost

        self.last_move_cost = cost

    def _return_to_store(self, move: Move):
        player = self._player_from_move(move)
        player.store.return_piece(move.piece)

    def apply_move(self, move: Move):
        if move.move_type == MoveType["added"]:
            if move.piece.piece_type == PieceType["sun"]:
                field = self._field_from_coords(move.coordinates[0], move.coordinates[1])
                field.piece = move.piece
                self._end_round(move)
            else:
                self._add_to_board(move)
        elif move.move_type == MoveType["removed"]:
            self._remove_from_board(move)
        elif move.move_type == MoveType["bought_from_store"]:
            field = self._field_from_coords(move.coordinates[0], move.coordinates[1])
            field.piece = None
            self._buy_from_store(move)
        elif move.move_type == MoveType["returned_to_store"]:
            field = self._field_from_coords(move.coordinates[0], move.coordinates[1])
            field.piece = move.piece
            self._return_to_store(move)

        print("autumn store")
        self.autumn_player.store.print()

        print("winter store")
        self.winter_player.store.print()


    def end_game(self):
        self.autumn_player.score += math.floor(self.autumn_player.sun_points/3)
        self.winter_player.score += math.floor(self.winter_player.sun_points/3)
        self.autumn_player.sun_points = 0
        self.winter_player.sun_points = 0

def piece_from_store_position(angle):
    if angle >= 0 and angle <= 3:
        return PieceType["seed"]
    
    if angle >= 4 and angle <= 7:
        return PieceType["small"]

    if angle >= 8 and angle <= 10:
        return PieceType["medium"]

    return PieceType["large"]

class VotingBoardStateEstimator:
    def __init__(self, n_fields, n_votes=3):
        self.state_estimate = np.zeros(n_fields, dtype=np.uint8)
        self.n_votes_casted = np.zeros(n_fields, dtype=np.int8) - 1
        self.votes = np.zeros((n_fields, n_votes), dtype=np.uint8)
        self.n_votes = n_votes

    def update_state(self, model_predictions):
        # 1. Each field can be in the voting state or not.
        # 2. Voting is triggered by change in the prediction from the model.
        # 2. If field is in the voting state the predictions will be saved to votes.
        # 3. Once n_votes votes are stored in self.votes voting is performed.
        # 4. The most frequent answer is saved to self.state_estimate. If we can't find the most frequent answer we do not update the field.
        # 5. Whether field is in the voting state or not is indicated by self.vote_count. If vote count is set to -1 then voting is not performed.
        # If this number is higher than -1 voting is beeing performed.
        for i, pred in enumerate(model_predictions):
            if self.n_votes_casted[i] == -1:
                if pred != self.state_estimate[i]:
                    self.n_votes_casted[i] = 0
                    self.votes[i][0] = pred
            else:
                # Save prediction as a vote.
                self.votes[i][self.n_votes_casted[i]] = pred
                self.n_votes_casted[i] += 1
                
                # Perform voting
                if self.n_votes_casted[i] == self.n_votes:
                    vote = np.bincount(self.votes[i])
                    max_val_idxs = np.where(vote == np.max(vote))[0]
                    self.n_votes_casted[i] = - 1 # End vote

                    # Only if we can find single most frequent element we update state estimate.
                    if len(max_val_idxs) == 1:
                        self.state_estimate[i] = max_val_idxs[0]

class MovesDetector:
    def __init__(self, pieces_classes, fields=PHOTOSYNTHESIS_FIELDS):
        self.previous_board_state_estimate = None
        self.previous_sun_state_estimate = None

        self.fields = fields

        self.pieces = []
        for piece_class in pieces_classes[:-1]:
            player, piece_type = piece_class.split("+")
            player, piece_type = player.strip(), piece_type.strip()

            self.pieces.append(Piece(PlayerType[player], PieceType[piece_type]))
        
        self.sun = Piece(PlayerType["none"], PieceType["sun"])
        
        self.winter_level = 5
        self.autumn_level = 4
        
    def detect_moves(self, board_state_estimate, sun_state_estimate):
        if self.previous_board_state_estimate is None:
            self.previous_board_state_estimate = np.copy(board_state_estimate)
            self.previous_sun_state_estimate = np.copy(sun_state_estimate)
            return []
        
        # Find changes in the state.
        idx_board_changes = np.where(self.previous_board_state_estimate != board_state_estimate)[0]
        idx_sun_changes = np.where(self.previous_sun_state_estimate != sun_state_estimate)[0]

        moves = []

        # Detect moves for the sun.
        for idx in idx_sun_changes:
            # Placing
            if self.previous_sun_state_estimate[idx] == 0:
                move = Move(self.sun, MoveType["added"], (6, idx))
            else: # Removing
                move = Move(self.sun, MoveType["removed"], (6, idx))
            
            moves.append(move)

        # Detect moves for the pieces.
        for idx in idx_board_changes:
            field = self.fields[idx]
            if field.level == self.autumn_level:
                field_type = FieldType["store_autumn"]
            elif field.level == self.winter_level:
                field_type = FieldType["store_winter"]
            else:
                field_type = FieldType["regular"]

            # Piece removed
            if board_state_estimate[idx] == 8:
                move_type = MoveType["removed"] if field_type == FieldType["regular"] else MoveType["bought_from_store"]
                piece = self.pieces[self.previous_board_state_estimate[idx]]
                
                if field_type != FieldType["regular"]:
                    piece.player = PlayerType["winter"] if field_type == FieldType["store_winter"] else PlayerType["autumn"]
                    piece.piece_type = piece_from_store_position(field.angle)
                
                moves.append(Move(piece, move_type, (field.level, field.angle)))

            # Piece added
            elif self.previous_board_state_estimate[idx] == 8:
                move_type = MoveType["added"] if field_type == FieldType["regular"] else MoveType["returned_to_store"]
                piece = self.pieces[board_state_estimate[idx]]

                if field_type != FieldType["regular"]:
                    piece.player = PlayerType["winter"] if field_type == FieldType["store_winter"] else PlayerType["autumn"]
                    piece.piece_type = piece_from_store_position(field.angle)
               
                moves.append(Move(piece, move_type, (field.level, field.angle)))
            else:
                # Piece exchanged for something else
                if field_type == FieldType["regular"]:
                    moves += [
                            Move(self.pieces[self.previous_board_state_estimate[idx]], MoveType["removed"], (field.level, field.angle)),
                            Move(self.pieces[board_state_estimate[idx]], MoveType["added"], (field.level, field.angle))
                    ]

        self.previous_board_state_estimate = np.copy(board_state_estimate)
        self.previous_sun_state_estimate = np.copy(sun_state_estimate)

        # Sort moves so all of the moves.
        sorted(moves, key=lambda x: x.move_type == MoveType["removed"])
        return moves
