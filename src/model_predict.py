# pylint: disable=C0103
import os

import joblib
from prefect import flow, get_run_logger
from wandb.beta.workflows import use_model

from components.tracking.wandb_utils import setup_tracker
from training_pipeline import get_data, split_data


@flow
def predict(pipeline):
    """Predict function"""
    get_run_logger()
    X, y = get_data()
    _, X_test, _, y_test = split_data(X, y)
    clf = pipeline
    acc = clf.score(X_test, y_test)
    print(acc)
    # write_metrics(clf, X_test, y_test)
    # plot_results(clf, X_test, y_test)


def load_pickle(filename):
    """Load model from pickle file"""
    with open(filename, "rb") as f_in:
        return joblib.load(f_in)


if __name__ == "__main__":
    run = setup_tracker()

    model_art = use_model(f"{os.environ['MODEL']}:latest")
    model_obj = model_art.model_obj()
    print(model_obj)
    # artifact = run.use_artifact("ibombonato/model-registry/mlops-test:v0", type="model")
    # print(artifact)
    # artifact_dir = artifact.download()
    # print(artifact_dir)
    # print(Path("./output/model.pkl").exists())
    # artifact = load_pickle("./output/model.pkl")
    predict(model_obj)
