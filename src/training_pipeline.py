# pylint: disable=C0103,W0611
import os
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
from prefect import flow, get_run_logger, task
from sklearn.datasets import make_classification
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from wandb.beta.workflows import link_model, log_model, use_model

import wandb
from components.tracking.wandb_utils import setup_tracker


@task
def get_data():
    """Get the data"""
    X, y = make_classification(random_state=0, n_samples=10000, shuffle=False)
    return X, y


@task
def split_data(X, y):
    """Split data"""
    X_train, X_test, y_train, y_test = train_test_split(X, y)
    return X_train, X_test, y_train, y_test


@task
def train_model(X_train, y_train):
    """Make classifier pipeline"""

    # clf = Pipeline([("scaler", StandardScaler()), ("svc",  SVC())])
    # clf = Pipeline([("scaler", StandardScaler()), ("nb",  GaussianNB())])
    clf = Pipeline(
        [("scaler", StandardScaler()), ("tree", DecisionTreeClassifier(max_depth=3))]
    )
    clf.fit(X_train, y_train)
    joblib.dump(clf, "./output/model.pkl")
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


@flow
def compare_and_register_model(clf, X_test, y_test):
    """Compare and registry as best model"""
    is_best = is_best_model(clf, X_test, y_test)
    model_version = log_model(clf, os.environ["WANDB_PROJECT"])
    link_model(
        model_version, os.environ["MODEL_REGISTRY"], ["best"] if is_best else None
    )


@task
def is_best_model(clf, X_test, y_test):
    """
    Check if this model is better then the actual best model.
    If so, this is mared as the best model.
    """
    try:
        best_model = use_model(f"{os.environ['MODEL']}:best")
        best_model = best_model.model_obj()
    except:
        best_model = None

    if best_model is None:
        return True

    best_acc = best_model.score(X_test, y_test)

    this_acc = clf.score(X_test, y_test)

    return this_acc > best_acc


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
    # register_model(clf)
    # model_version = register_model(clf)
    compare_and_register_model(clf, X_test, y_test)


if __name__ == "__main__":
    training_flow()
