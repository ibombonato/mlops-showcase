# pylint: disable=E0401
from src.training_pipeline import is_best_model


def test_best_model_returns_true(mocker):
    """Assert use_model returns True
    if no best model is available on registry"""
    mocker.patch("wandb.beta.workflows.use_model", return_value=None)
    actual = is_best_model.fn(None, None, None)
    assert actual
