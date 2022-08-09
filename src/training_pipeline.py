# pylint: disable=C0103

import matplotlib.pyplot as plt
from prefect import flow, task, get_run_logger
from sklearn.svm import SVC
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split


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
    """Fit classifier"""
    clf = SVC(random_state=0)
    clf.fit(X_train, y_train)
    return clf


@task
def write_metrics(clf, X_test, y_test):
    """Write metrics file"""
    acc = clf.score(X_test, y_test)
    print(acc)
    with open("output/metrics.txt", "w", encoding="UTF-8") as outfile:
        outfile.write("Accuracy: " + str(acc) + "\n")


@task
def plot_results(clf, X_test, y_test):
    """Plot results"""
    ConfusionMatrixDisplay.from_estimator(clf, X_test, y_test)
    plt.savefig("output/plot.png")


@flow(name="Training Flow")
def training_flow():
    """Training flow for setup testing"""
    logger = get_run_logger()
    logger.warning("The fun is about to begin")
    X, y = get_data()
    X_train, X_test, y_train, y_test = split_data(X, y)
    clf = train_model(X_train, y_train)
    write_metrics(clf, X_test, y_test)
    plot_results(clf, X_test, y_test)


if __name__ == "__main__":
    training_flow()
