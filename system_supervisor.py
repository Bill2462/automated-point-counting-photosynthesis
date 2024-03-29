import argparse
import threading
import queue
import time
import sys
from surface.com import ZmqSubscriber, ZmqPublisher
from surface.game_types import *
from PyQt5.QtWidgets import (QLabel, QRadioButton, 
                             QPushButton, QVBoxLayout, 
                             QApplication, QWidget, QLineEdit,
                             QButtonGroup)
from PyQt5 import QtCore

def get_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input_address", type=str, default="tcp://localhost:5558",
                        help="Address from which detected moves are taken")

    parser.add_argument("--input_channel", type=str, default="moves",
                        help="Channel from which input data will be taken.")

    parser.add_argument("--output_address", type=str, default="tcp://*:5559",
                        help="Address on which the data products will be published.")
    
    return parser.parse_args()

class ZMQReceiver(QtCore.QObject):
    dataChanged = QtCore.pyqtSignal(object)

    def start(self, sub):
        self.sub = sub
        threading.Thread(target=self._execute, daemon=True).start()

    def _execute(self):
        while True:
            self.dataChanged.emit(self.sub.get_data())

class App(QWidget):

    def __init__(self, sub, pub):
        super().__init__()
        self.move_queue = queue.Queue()

        self.init_ui()

        zmq_receiver = ZMQReceiver(self)
        zmq_receiver.dataChanged.connect(self.on_new_move)
        zmq_receiver.start(sub)
        self.publisher = pub
        self.ui_clear = True
    
    @QtCore.pyqtSlot(object)
    def on_new_move(self, buf):
        # Put move into the quque
        if self.ui_clear:
            self.update_ui_state(buf)
        else:
            self.move_queue.put(buf)
        
        self.update_status_txt()
        self.update_busy_flag()
    
    def update_status_txt(self):
        self.status_label.setText(f"qsize = {self.move_queue.qsize()}")
    
    def clear_ui(self):
        self.ui_clear = True

        self.player_bt_group.setExclusive(False)     
        self.piece_bt_group.setExclusive(False)   
        self.move_type_bt_group.setExclusive(False)   
        self.points_override_type_bt_group.setExclusive(False)     

        self.move_position_txt_box.setText("")

        self.move_type_bt_place.setChecked(False)
        self.move_type_bt_remove.setChecked(False)
        self.move_type_bt_bought_from_store.setChecked(False)
        self.move_type_bt_returned_to_store.setChecked(False)

        self.piece_bt_seed.setChecked(False)
        self.piece_bt_small.setChecked(False)
        self.piece_bt_medium.setChecked(False)
        self.piece_bt_large.setChecked(False)
        self.piece_bt_sun.setChecked(False)

        self.player_bt_blue.setChecked(False)
        self.player_bt_yellow.setChecked(False)

        self.points_override_type_bt_sun.setChecked(False)
        self.points_override_type_bt_score.setChecked(False)
        
        self.player_bt_group.setExclusive(True)
        self.piece_bt_group.setExclusive(True)
        self.move_type_bt_group.setExclusive(True)
        self.points_override_type_bt_group.setExclusive(True)

    def update_ui_state(self, move):
        self.ui_clear = False

        # Player type
        if move.piece.player == PlayerType.autumn:
            self.player_bt_blue.setChecked(False)
            self.player_bt_yellow.setChecked(True)
        elif move.piece.player == PlayerType.winter:
            self.player_bt_blue.setChecked(True)
            self.player_bt_yellow.setChecked(False)
        else:
            self.player_bt_blue.setChecked(False)
            self.player_bt_yellow.setChecked(False)
        
        # Piece type
        piece_bt_states = [False, False, False, False, False]
        piece_bt_states[move.piece.piece_type.value] = True

        self.piece_bt_seed.setChecked(piece_bt_states[0])
        self.piece_bt_small.setChecked(piece_bt_states[1])
        self.piece_bt_medium.setChecked(piece_bt_states[2])
        self.piece_bt_large.setChecked(piece_bt_states[3])
        self.piece_bt_sun.setChecked(piece_bt_states[4])

        # Move type
        move_type_bt_states = [False, False, False, False]
        move_type_bt_states[move.move_type.value] = True

        self.move_type_bt_place.setChecked(move_type_bt_states[0])
        self.move_type_bt_remove.setChecked(move_type_bt_states[1])
        self.move_type_bt_bought_from_store.setChecked(move_type_bt_states[2])
        self.move_type_bt_returned_to_store.setChecked(move_type_bt_states[3])

        # Move position
        position = f"{move.coordinates[0]},{move.coordinates[1]}"
        self.move_position_txt_box.setText(position)

    def init_ui(self):
        self.player_label = QLabel('Player')
        self.player_bt_blue = QRadioButton('Blue')
        self.player_bt_yellow = QRadioButton('Yellow')
        self.player_spacer = QLabel("")
        
        self.piece_type_label = QLabel('Piece type')
        self.piece_bt_seed = QRadioButton('Seed')
        self.piece_bt_small = QRadioButton('Small')
        self.piece_bt_medium = QRadioButton('Medium')
        self.piece_bt_large = QRadioButton('Large')
        self.piece_bt_sun = QRadioButton('Sun')

        self.piece_spacer = QLabel("")

        self.move_type_label = QLabel("Move type")
        self.move_type_bt_place = QRadioButton('Place')
        self.move_type_bt_remove = QRadioButton('Remove')
        self.move_type_bt_bought_from_store = QRadioButton('Bought from store')
        self.move_type_bt_returned_to_store = QRadioButton('Returned to store')

        self.move_type_spacer = QLabel("")

        self.move_position_label = QLabel("Move position")
        self.move_position_txt_box = QLineEdit()
        self.move_position_spacer = QLabel("")

        self.move_ctrl_label = QLabel("Move control")
        self.accept_button = QPushButton('Accept move')
        self.reject_button = QPushButton('Reject move')
        self.end_game_button = QPushButton('End game')
        self.accept_button.clicked.connect(self.on_accept_move_bt_clicked)
        self.reject_button.clicked.connect(self.on_reject_move_bt_clicked)
        self.end_game_button.clicked.connect(self.on_end_game_bt_clicked)

        self.move_ctrl_spacer = QLabel("")

        self.points_override_type_label = QLabel("Points override type")

        self.points_override_type_bt_sun = QRadioButton('Sun points')
        self.points_override_type_bt_score = QRadioButton('Score')

        self.points_override_type_spacer = QLabel("")

        self.points_override_accept_button = QPushButton('Apply override')
        self.points_override_accept_button.clicked.connect(self.on_apply_override_bt_clicked)

        self.points_override_txt_box = QLineEdit()
        self.points_override_spacer = QLabel("")

        self.status_label = QLabel("")

        self.player_bt_group = QButtonGroup()        
        self.player_bt_group.addButton(self.player_bt_yellow)
        self.player_bt_group.addButton(self.player_bt_blue)

        self.piece_bt_group = QButtonGroup()
        self.piece_bt_group.addButton(self.piece_bt_seed)
        self.piece_bt_group.addButton(self.piece_bt_small)
        self.piece_bt_group.addButton(self.piece_bt_medium)
        self.piece_bt_group.addButton(self.piece_bt_large)
        self.piece_bt_group.addButton(self.piece_bt_sun)

        self.move_type_bt_group = QButtonGroup()
        self.move_type_bt_group.addButton(self.move_type_bt_place)
        self.move_type_bt_group.addButton(self.move_type_bt_remove)
        self.move_type_bt_group.addButton(self.move_type_bt_bought_from_store)
        self.move_type_bt_group.addButton(self.move_type_bt_returned_to_store)

        self.points_override_type_bt_group = QButtonGroup()
        self.points_override_type_bt_group.addButton(self.points_override_type_bt_sun)
        self.points_override_type_bt_group.addButton(self.points_override_type_bt_score)
        
        layout = QVBoxLayout()
        layout.addWidget(self.player_label)
        layout.addWidget(self.player_bt_blue)
        layout.addWidget(self.player_bt_yellow)
        layout.addWidget(self.player_spacer)
        
        layout.addWidget(self.piece_type_label)
        layout.addWidget(self.piece_bt_seed)
        layout.addWidget(self.piece_bt_small)
        layout.addWidget(self.piece_bt_medium)
        layout.addWidget(self.piece_bt_large)
        layout.addWidget(self.piece_bt_sun)
        layout.addWidget(self.piece_spacer)

        layout.addWidget(self.move_type_label)
        layout.addWidget(self.move_type_bt_place)
        layout.addWidget(self.move_type_bt_remove)
        layout.addWidget(self.move_type_bt_bought_from_store)
        layout.addWidget(self.move_type_bt_returned_to_store)

        layout.addWidget(self.move_type_spacer)

        layout.addWidget(self.move_position_label)
        layout.addWidget(self.move_position_txt_box)
        layout.addWidget(self.move_position_spacer)

        layout.addWidget(self.move_ctrl_label)
        layout.addWidget(self.accept_button)
        layout.addWidget(self.reject_button)
        layout.addWidget(self.end_game_button)
        layout.addWidget(self.move_ctrl_spacer)

        layout.addWidget(self.points_override_type_label)

        layout.addWidget(self.points_override_type_bt_sun)
        layout.addWidget(self.points_override_type_bt_score)

        layout.addWidget(self.points_override_type_spacer)

        layout.addWidget(self.points_override_txt_box)
        layout.addWidget(self.points_override_accept_button)
        layout.addWidget(self.status_label)
        
        self.setGeometry(200, 200, 300, 300)
        self.setLayout(layout)
        self.setWindowTitle('Table monitoring app')        
        self.setStyleSheet("QLabel{font-size: 18pt;}")
        self.show()

        self.update_status_txt()

    def get_move_from_ui(self):
        # Player type
        if self.player_bt_blue.isChecked():
            player = PlayerType.winter
        elif self.player_bt_yellow.isChecked():
            player = PlayerType.autumn
        else:
            player = PlayerType.none

        if self.piece_bt_seed.isChecked():
            piece = PieceType.seed
        elif self.piece_bt_small.isChecked():
            piece = PieceType.small
        elif self.piece_bt_medium.isChecked():
            piece = PieceType.medium
        elif self.piece_bt_large.isChecked():
            piece = PieceType.large
        elif self.piece_bt_sun.isChecked():
            piece = PieceType.sun
            player = PlayerType.none
        
        if self.move_type_bt_place.isChecked():
            move_type = MoveType.added
        elif self.move_type_bt_remove.isChecked():
            move_type = MoveType.removed
        elif self.move_type_bt_bought_from_store.isChecked():
            move_type = MoveType.bought_from_store
        elif self.move_type_bt_returned_to_store.isChecked():
            move_type = MoveType.returned_to_store
        
        # Move position
        txt = self.move_position_txt_box.text()
        level, angle = txt.split(",")

        pos = (int(level), int(angle))

        return Move(Piece(player, piece), move_type, pos)

    def get_override_from_ui(self):
        # Player type
        if self.player_bt_blue.isChecked():
            player = PlayerType.winter
        elif self.player_bt_yellow.isChecked():
            player = PlayerType.autumn

        if self.points_override_type_bt_sun.isChecked():
            point_type = PointType.sun
        elif self.points_override_type_bt_score.isChecked():
            point_type = PointType.score
        
        point_change = int(self.points_override_txt_box.text())

        return Override(player, point_type, point_change)

    def update_busy_flag(self):
        is_busy = self.move_queue.qsize() > 0 or (not self.ui_clear)
        self.publisher.send_data({"cmd": "update_busy_flag", "data": is_busy}, "commands")
    
    def on_end_game_bt_clicked(self):
        self.publisher.send_data({"cmd": "end_game"}, "commands")

    def on_accept_move_bt_clicked(self):
        # Load state of the UI into the move and send move.
        try:
            move = self.get_move_from_ui()
        except ValueError as _:
            return
        
        self.publisher.send_data({"cmd": "move", "data": move}, "commands")

        if self.move_queue.qsize() > 0:
            self.update_ui_state(self.move_queue.get())
        else:
            self.clear_ui()

        self.update_status_txt()
        self.update_busy_flag()

        print(int(time.time()), "accepted")

    def on_reject_move_bt_clicked(self):
        if self.move_queue.qsize() > 0:
            self.update_ui_state(self.move_queue.get())
        else:
            self.clear_ui()
        
        self.update_status_txt()
        self.update_busy_flag()

        print(int(time.time()), "rejected")

    def on_apply_override_bt_clicked(self):
        override = self.get_override_from_ui()
        self.publisher.send_data({"cmd": "override", "data": override}, "commands")
        print(int(time.time()), "override_applied", override)

def main():
    args = get_arguments()
    subscriber = ZmqSubscriber(args.input_address, args.input_channel)
    publisher = ZmqPublisher(args.output_address)

    app = QApplication(sys.argv)
    ex = App(subscriber, publisher)

    sys.exit(app.exec_())

if __name__ == '__main__':    
    main()
