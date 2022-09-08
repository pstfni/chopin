import pickle as pkl
from pathlib import Path

import typer
from sklearn.ensemble import RandomForestClassifier

from ml import data, train
from utils import get_logger

LOGGER = get_logger(__name__)


def main(
    local_folder: Path = typer.Argument(..., help="Path to a folder containing the playlists (as JSON(s))"),
    output: Path = typer.Argument(..., help="Where to write the trained model"),
):
    """Train models to classify songs into existing playlists."""
    LOGGER.info("🚆 Training a model . . .")
    train_records, val_records = data.create_train_records(list(Path(local_folder).glob("*.json")))
    classifier = RandomForestClassifier(n_estimators=2000, max_depth=16, random_state=0)
    classifier = train.fit(train_records, classifier)
    score = train.score(val_records, classifier)
    # Save to file in the current working directory
    with open(output, "wb") as file:
        pkl.dump(classifier, file)
    LOGGER.info(f"Saved classifier in {output.as_posix()}. Score of the classifier: {score}")


if __name__ == "__main__":
    typer.run(main)
