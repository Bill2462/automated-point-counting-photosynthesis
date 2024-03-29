# Automated point counting system

This is a supplementary material for the paper "I didn't have to think": Screenless Interactive Tabletop Gaming with Capacitive Surface Sensing."
(https://doi.org/10.1145/3613904.3642654)

This repository contains training data and the complete implementation of an automated point-counting system for the photosynthesis game.
GT-TF-XTC43.0L-1 touch foil is required (https://www.greentouch.com.cn/?list_21/308.html) to run this code. 

Conda environment with packages listed in `env.yaml ` is needed to run this code.

## Repository structure

 - `assets`: all images
 - `data`: dataset used for training and testing of the classifier.
 - `models`: trained models
 - `pieces`: 3D models of piece markers.
 - `surface`: a package that contains most code that is shared between scripts.
 - `templates`: a folder that contains assets for the point display website.

Scripts used during system operation:

 - `measurement_server.py`: Script that reads surface and publishes results through zmq.
 - `data_processor.py`: Script for signal processing and classifier predictions.
 - `move_finder.py`: Script that detects and publishes moves predictions
 - `system_supervisor.py`: Script that runs the ui of the system supervisor
 - `game_state_processor.py`: script that runs a virtual game implementation
 - `points_server.py`: Script that runs the website that displays points.

Visualization scripts:

 - `display.py`: Script that displays many kinds of raw data in real-time.
 - `game_board_display_simple.py`: Script that creates real-time visualization of the capacitive image of each field.
 - `gameboard_display.py`: Script that visualizes the state of the game as seen by the system.

 Miscellaneous scripts and files:

 - `plot_sample.py`: Script that plots a single capacitive image directly from .npy file.
 - `recorder.py`: Script that records the capacitive data from the surface. Used for capturing training dataset.
 - `train_classifier.py`: Training script for the classifier.
 - `training_config.json`: Configuration file for the classifier training script.
 - `table_udev_rules.rules`: UDEV rule necessary on linux to get access to debug interface of capacitive controller.
 - `env.yaml`: Dump of conda environment specification used to conduct experiments and run this system.

## Surface package structure

 - `surface/com.py`: zmq publisher and subscriber
 - `surface/data.py`: Functions related to dataset loading and processing.
 - `surface/display.py`: Data visualization code.
 - `surface/gameboard.py`: Game implementation code, move detection code, voting state estimator code.
 - `surface/game_types.py`: Data types used in the game.
 - `surface/misc.py`: Miscellaneous functions.
 - `surface/touch_surface.py`: Code that pulls data from the touch controller.
 - `surface/baseline.py`: Baseline cancellation code.
 - `surface/pieces_classifier.py`: Classifier prediction code.
