# pylint: disable=C0103
import os
from random import randint

from prefect import flow, get_run_logger, task
from sklearn.datasets import make_classification
from wandb.beta.workflows import use_model

from training_pipeline import training_flow
from wandb_utils import setup_tracker


@task
def get_production_data():
    """Get simulated data from production"""
    n_samples = randint(100, 3000)
    logger = get_run_logger()
    logger.info(f"N Samples for this run: {n_samples}")

    X, y = make_classification(random_state=0, n_samples=n_samples, shuffle=False)
    return X, y


@flow
def should_retrain(accuracy):
    """
    Function to check for model degradation.

    Since we are running with synthetic/fake data,
    this will probally trigger often if N sample is low.

    IF ACCURACY FALLS BELLOW 0.8 WE WILL RUN THE TRAIN PIPELINE
    AND THE TRAINING_FLOW WILL DEPLOY THE NEW MODEL IF
    IT HAS HIGGER ACCURACY THEN THE ACTUAL ONE
    """
    logger = get_run_logger()
    if accuracy <= 0.7:
        logger.info("RETRAINING MODEL DUE DEGRADATION")
        training_flow()


@task
def get_best_model_pipeline():
    """
    Get best model from model registry and return it

    Best model/pipeline is defined by a tag on wandb model registry
    """
    model_artifact = use_model(f"{os.environ['MODEL']}:best")
    model_obj = model_artifact.model_obj()
    print(model_obj)
    return model_obj


@flow
def predict():
    """Predict function"""
    logger = get_run_logger()
    X, y = get_production_data()

    clf = get_best_model_pipeline()
    acc = clf.score(X, y)
    logger.info(f"Accuracy on NEW DATA: {acc}")
    print(acc)
    return acc


if __name__ == "__main__":
    setup_tracker()
    daily_accuracy = predict()
    should_retrain(daily_accuracy)
