from typing import Any

import pandas as pd


def fit(train_records: pd.DataFrame, model: Any):
    """
    Fit a `model` on train_records, and compute the score (sklearn .score()) on test records.
    Args:
        train_records: A dataframe with train tracks and their playlist label.
        model: A sklearn model

    Returns:
        The trained model
    """
    # Ignore the track name (first column), and create a label dataframe with the label (last column)
    X_train, y_train = train_records.iloc[:, 1:-1], train_records.iloc[:, -1]
    model.fit(X_train, y_train)
    return model


def score(test_records: pd.DataFrame, model: Any):
    """Returns the sklearn .score() of a given model on a records dataframe.

    Args:
        test_records: A dataframe with test tracks and their target label
        model: A trained model

    Returns:
        A score
    """
    # Ignore the track name (first column), and create a label dataframe with the label (last column)
    X_val, y_val = test_records.iloc[:, 1:-1], test_records.iloc[:, -1]
    score = model.score(X_val, y_val)
    return score
