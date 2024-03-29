import glob
import os
import cv2
import json
import numpy as np
from pathlib import Path
from .misc import align
from .baseline import NaiveBaseline
from .game_board import crop_images_from_fields

def load_samples(path, extension="*.npy"):
    samples = []
    filepaths = list(glob.glob(os.path.join(path, extension)))
    filepaths = sorted(filepaths, key=lambda x: int(os.path.basename(x).split(".")[0]))

    for filepath in filepaths:
        samples.append(np.load(filepath))

    return samples

def _get_classes_and_filenames(dataroot, extension="*.npy"):
    classes = {}
    idx = 0

    # Find classes
    for i, p in Path(dataroot).iterdir():
        if os.path.isdir(p):
            classes[os.path.split(p)[1]] = idx
            idx += 1

    samples = []
    classes = []
    for cls, idx in classes.items():
        cls_path = os.path.join(dataroot, cls)
        samples += load_samples(cls_path, extension)
        classes += [idx]*len(samples)

    return samples, classes

def list_directories(path):
    return [f.path for f in os.scandir(path) if f.is_dir() ]

def load_json(filepath):
    with open(filepath) as f:
        return json.load(f)

def get_classes_pieces(dataset_path):
    classes = []
    class_paths = []

    for player_path in list_directories(dataset_path):
        for piece_path in list_directories(player_path):
            class_paths.append(piece_path)

            player = os.path.split(player_path)[1]
            piece = os.path.split(piece_path)[1]
            classes.append(player + " + " + piece)

    class_idx = list(range(len(classes)))

    return classes, class_paths, class_idx

def get_classes_simple(dataset_path):
    classes = []
    class_paths = []

    for cls_path in list_directories(dataset_path):
        classes.append(os.path.split(cls_path)[1])
        class_paths.append(cls_path)

    class_idx = list(range(len(classes)))

    return classes, class_paths, class_idx

def get_samples_from_field(path, fields, n_baseline, target_size):
    try:
        pos_fields = load_json(os.path.join(path, "fields.json"))["pos_fields"]
        levels = []
        angles = []
        for field in pos_fields:
            levels.append(field["level"])
            angles.append(field["angle"])
    except FileNotFoundError as _:
        field_name = os.path.split(path)[1]
        levels = [int(field_name.split("-")[0])]
        angles = [int(field_name.split("-")[1])]

    baseline_processor = NaiveBaseline(n_baseline)
    samples = load_samples(path)

    # Cancel baseline for all samples
    for i in range(len(samples)):
        sample = align(samples[i], -1)
        samples[i] = baseline_processor(sample)

    samples = samples[n_baseline:]

    negative_samples = []
    positive_samples = []
    for sample in samples:
        for i, cropped_img in enumerate(crop_images_from_fields(fields, sample)):
            if cropped_img.shape[0] != target_size[0] or cropped_img.shape[1] != target_size[1]:
                cropped_img = cv2.resize(cropped_img, target_size, interpolation=cv2.INTER_AREA)

            field = fields[i]
            if field.level in levels and field.angle in angles:
                positive_samples.append(cropped_img)
            else:
                negative_samples.append(cropped_img)

    return negative_samples, positive_samples

def load_class(path, fields, n_baseline, target_size):

    positive_samples = []
    negative_samples = []

    field_list = list_directories(path)
    if len(field_list) == 0:
        return get_samples_from_field(path, fields, n_baseline, target_size)

    for field_path in field_list:
        neg_samples, pos_samples = get_samples_from_field(field_path, fields, n_baseline, target_size)
        positive_samples += pos_samples
        negative_samples += neg_samples

    return negative_samples, positive_samples

def load_dataset(dataroot, fields, n_baseline=5, target_size=(16, 16)):
    classes, class_paths, class_idx = get_classes_pieces(dataroot)

    if len(classes) == 0:
        classes, class_paths, class_idx = get_classes_simple(dataroot)

    X = []
    Y = []
    negative_samples = []
    number_of_samples_per_class = None
    for cls_idx, cls_path in zip(class_idx, class_paths):
        neg_samples, pos_samples = load_class(cls_path, fields, n_baseline, target_size)

        n_samples_per_class = len(pos_samples)

        X += pos_samples
        Y += [cls_idx] * n_samples_per_class
        negative_samples += neg_samples

    # Stratified sample negative samples.
    negative_samples = np.array(negative_samples)
    train_neg_activation = np.sum(np.abs(negative_samples), axis=(1,2))
    train_neg_activation_threshold = train_neg_activation.mean() + train_neg_activation.mean()*0.2

    indexes_fragments = np.where(train_neg_activation > train_neg_activation_threshold)[0]
    indexes_noise = np.where(train_neg_activation <= train_neg_activation_threshold)[0]

    rand_index_fragments = np.random.choice(indexes_fragments.shape[0], n_samples_per_class//2, replace=False)
    rand_index_noise = np.random.choice(indexes_noise.shape[0], n_samples_per_class//2, replace=False)

    sampled_negatives = np.append(negative_samples[rand_index_fragments],
                                  negative_samples[rand_index_noise], axis=0)

    X, Y = np.array(X), np.array(Y)

    X = np.append(X, sampled_negatives, axis=0)
    Y = np.append(Y, np.ones(sampled_negatives.shape[0], dtype=np.int32)*len(classes))

    classes += ["empty"]
    return classes, X, Y
