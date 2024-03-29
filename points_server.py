import threading
import zmq
import argparse
from flask import Flask, request, render_template
from dataclasses import dataclass
from surface.game_types import GameStateSummary

def get_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input_address", type=str, default="tcp://localhost:5560",
                        help="Address from which model predictions will be taken.")

    parser.add_argument("--input_channel", type=str, default="point_summary",
                        help="Channel from which input data will be taken.")
    
    return parser.parse_args()

class TelemetryReceiver:
    def __init__(self, address, input_channel):
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.connect(address)
        self.socket.subscribe(input_channel)
        self.game_state_summary = GameStateSummary()

    def _process_data(self):
        topic = self.socket.recv_string()
        value = self.socket.recv_pyobj()
        self.game_state_summary = value

    def start(self):
        def wrapper():
            while 1:
                self._process_data()
            
        self.thread = threading.Thread(target=wrapper)
        self.thread.start()

args = get_arguments()

points_receiver = TelemetryReceiver(args.input_address, args.input_channel)
points_receiver.start()

app = Flask(__name__)

@app.route("/")
def get_points():
    return render_template("page_template.html", 
        game_state_summary=points_receiver.game_state_summary,
    )

app.run(host="0.0.0.0")
