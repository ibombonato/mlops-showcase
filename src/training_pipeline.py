# pylint: disable=C0103
import os
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
from prefect import flow, get_run_logger, task
from sklearn.datasets import make_classification
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from wandb.beta.workflows import link_model, log_model

import wandb
from components.tracking.wandb_utils import setup_tracker


@task
def get_data():
    """Get the data"""
    X, y = make_classification(random_state=0)
    return X, y


@task
def split_data(X, y):
    """Split data"""
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)
    return X_train, X_test, y_train, y_test


@task
def train_model(X_train, y_train):
    """Make classifier pipeline"""
    clf = Pipeline([("scaler", StandardScaler()), ("svc", SVC())])
    clf.fit(X_train, y_train)
    joblib.dump(clf, "output/model.pkl")
    # clf = SVC(random_state=0)
    # clf.fit(X_train, y_train)
    return clf


@task
def write_metrics(clf, X_test, y_test):
    """Write metrics file"""
    acc = clf.score(X_test, y_test)
    wandb.log({"accuracy": acc})
    print(acc)
    with open("output/metrics.txt", "w", encoding="UTF-8") as outfile:
        outfile.write("Accuracy: " + str(acc) + "\n")


@task
def plot_results(clf, X_test, y_test):
    """Plot results"""
    ConfusionMatrixDisplay.from_estimator(clf, X_test, y_test)
    plt.savefig("output/plot.png")


@task
def regiter_model(clf):
    """Register the model"""
    model_version = log_model(clf, os.environ["WANDB_PROJECT"])
    link_model(model_version, os.environ["MODEL_REGISTRY"])


@flow(name="Training Flow")
def training_flow():
    """Training flow for setup testing"""
    Path("output").mkdir(parents=True, exist_ok=True)
    get_run_logger()
    setup_tracker()
    X, y = get_data()
    X_train, X_test, y_train, y_test = split_data(X, y)
    clf = train_model(X_train, y_train)
    write_metrics(clf, X_test, y_test)
    plot_results(clf, X_test, y_test)
    regiter_model(clf)


if __name__ == "__main__":
    training_flow()
