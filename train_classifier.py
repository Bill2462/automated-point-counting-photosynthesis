import os
import json
import joblib
import argparse
from surface.data import load_dataset
from surface.game_board import PHOTOSYNTHESIS_FIELDS
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import RepeatedKFold, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

def load_json(filepath):
    with open(filepath) as f:
        return json.load(f)

def ensure_dir_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
    
def load_data(dataset_path, config):
    train_dataset_path = os.path.join(dataset_path, "train")
    test_dataset_path = os.path.join(dataset_path, "test")

    classes, X_train, Y_train = load_dataset(train_dataset_path, PHOTOSYNTHESIS_FIELDS,
                                              config["n_baseline"], config["img_size"])
    
    classes, X_test, Y_test = load_dataset(test_dataset_path, PHOTOSYNTHESIS_FIELDS,
                                           config["n_baseline"], config["img_size"])
    
    return classes, X_train, Y_train, X_test, Y_test

def merge_dataset_into_binary(Y_train, Y_test, classes):
    empty_class_index = classes.index("empty")
    Y_train[Y_train != empty_class_index] = 1
    Y_train[Y_train == empty_class_index] = 0
    Y_test[Y_test != empty_class_index] = 1
    Y_test[Y_test == empty_class_index] = 0

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_path', type=str, help='Path to dataset.')
    parser.add_argument('output_model_path', type=str, help='Where model output files will be saved.')
    parser.add_argument('config_path', type=str, help='Path to yaml file containing configuration for the training.')
    parser.add_argument('--binary_classifier', action="store_true", help='When set this merges all classes into a single positive class.')

    return parser.parse_args()

def preprocess_data(X_train, X_test):
    X_train_flat = X_train.reshape((-1, X_train.shape[1]*X_train.shape[2]))
    X_test_flat = X_test.reshape((-1, X_test.shape[1]*X_test.shape[2]))

    scaler = StandardScaler().fit(X_train_flat)
    X_train_scaled = scaler.transform(X_train_flat)
    X_test_scaled = scaler.transform(X_test_flat)

    return X_train_scaled, X_test_scaled, scaler

def train_model(X_train_scaled, Y_train, config):
    grid = dict(kernel=config["kernel"], tol=config["tolerance"], C=config["C"])

    model = SVC()
    cv_fold = RepeatedKFold(n_splits=config["n_splits"], n_repeats=config["n_repeats"])
    grid_search = GridSearchCV(estimator=model, param_grid=grid, n_jobs=-1, cv=cv_fold, scoring=config["scoring"])
    
    return grid_search.fit(X_train_scaled, Y_train)

def print_model_summary(preds, Y_test):
    print(f"Best model has score of {search_result.best_score_}")
    print(f"Best parameters are: {search_result.best_params_}")
    print(f"Accuracy: {accuracy_score(Y_test, preds)}")

    print("Confusion matrix: ")
    print(confusion_matrix(Y_test, preds))

    print("Classification report:")
    print(classification_report(Y_test, preds))

def save_model(path, config, model, classes, scaler):
    ensure_dir_exists(path)

    model_filepath = os.path.join(path, "model.bin")
    classes_filepath = os.path.join(path, "classes.bin")
    scaler_filepath = os.path.join(path, "scaler.bin")
    img_size_filepath = os.path.join(path, "img_size.bin")

    joblib.dump(model, model_filepath)
    joblib.dump(classes, classes_filepath)
    joblib.dump(scaler, scaler_filepath)
    joblib.dump(config["img_size"], img_size_filepath)

if __name__ == '__main__':
    args = get_args()

    config = load_json(args.config_path)

    print("Loading dataset...")
    classes, X_train, Y_train, X_test, Y_test = load_data(args.dataset_path, config)

    if args.binary_classifier:
        print("Merging all classes into a single positive class...")
        merge_dataset_into_binary(Y_train, Y_test, classes)
        classes = ["empty", "filled"]
    
    print(f"{X_train.shape[0]} training samples loaded")
    print(f"{X_test.shape[0]} test samples loaded")
    print(f"{len(classes)} classes found!")

    X_train_scaled, X_test_scaled, scaler = preprocess_data(X_train, X_test)

    print("Training model...")
    search_result = train_model(X_train_scaled, Y_train, config)

    model = search_result.best_estimator_
    preds = model.predict(X_test_scaled)
    print_model_summary(preds, Y_test)
    
    print(f"Saving model to {args.output_model_path}...")

    save_model(args.dataset_path, config, model, classes, scaler)
