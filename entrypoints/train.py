import argparse
import pickle as pkl
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier

from ml import data, train
from utils import get_logger

LOGGER = get_logger(__name__)


def main():
    """Train models to classify songs into existing playlists."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--playlists",
        "-p",
        type=Path,
        default=None,
        help=(
            "Path to the .jsons describing the playlists. "
            "In train mode, for the train data. In inference, for the predictions"
        ),
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output filepath for the model in trained mode, for the classified song information in inference mode",
    )
    ARGS = vars(parser.parse_args())

    LOGGER.info("🚆 Choo choo")
    train_records, val_records = data.create_train_records(list(Path("./data/playlists").glob("*.json")))
    classifier = RandomForestClassifier(n_estimators=2000, max_depth=16, random_state=0)
    classifier = train.fit(train_records, classifier)
    score = train.score(val_records, classifier)
    # Save to file in the current working directory
    with open(ARGS["output"], "wb") as file:
        pkl.dump(classifier, file)
    LOGGER.info(f"Saved classifier in {ARGS['output']}. Score of the classifier: {score}")


if __name__ == "__main__":
    main()
