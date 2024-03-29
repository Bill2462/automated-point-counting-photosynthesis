import os
import joblib
import numpy as np
from .misc import normalize_size

class PiecesClassifier:
    def __init__(self, path):
        scaler_filepath = os.path.join(path, "scaler.bin")
        model_filepath = os.path.join(path, "model.bin")
        classes_filepath = os.path.join(path, "classes.bin")
        target_img_size_filepath = os.path.join(path, "img_size.bin")

        self.scaler = joblib.load(scaler_filepath)
        self.model = joblib.load(model_filepath)
        self.classes = np.array(joblib.load(classes_filepath))
        self.target_img_size = joblib.load(target_img_size_filepath)
    
    def _preprocess_data(self, imgs):
        imgs = normalize_size(imgs, self.target_img_size)
        imgs = imgs.reshape((-1, imgs.shape[1]*imgs.shape[2]))
        imgs = self.scaler.transform(imgs)
        return imgs

    def forward(self, imgs):
        imgs = self._preprocess_data(imgs)
        preds = self.model.predict(imgs)

        return preds
