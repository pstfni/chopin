import argparse
import pickle as pkl
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier

from ml import data, train


def main():
    """Classify playlist(s) songs into existing playlists.

    You can also train a model.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", "-t", action="store_true", help="Activate the option to train a classifier")
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
        "--model",
        "-m",
        type=Path,
        default=None,
        help="In inference, path to a trained model",
    )
    parser.add_argument("--names", "-n", type=str, help="Comma separated list of playlist to classify")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output filepath for the model in trained mode, for the classified song information in inference mode",
    )
    ARGS = vars(parser.parse_args())

    if ARGS.get("train") and not ARGS.get("playlists"):
        raise ValueError("Cannot train without playlists")

    if ARGS.get("train"):
        print("🚆 Choo choo")
        train_records, val_records = data.create_train_records(list(Path("./data/playlists").glob("*.json")))
        classifier = RandomForestClassifier(n_estimators=2000, max_depth=16, random_state=0)
        classifier = train.fit(train_records, classifier)
        score = train.score(val_records, classifier)
        # Save to file in the current working directory
        with open(ARGS["output"], "wb") as file:
            pkl.dump(classifier, file)
        print(f"Saved classifier in {ARGS['output']}. Score of the classifier: {score}")

    else:
        playlist_paths = Path(ARGS["playlists"]).glob("*.json")
        inference_records = data.create_inference_records(playlist_paths)
        with open(ARGS["model"], "rb") as file:
            classifier = pkl.load(file)
        inference_records["playlist.name"] = classifier.predict(inference_records.iloc[:, 1:])
        with open(ARGS["output"], "w") as outfile:
            outfile.write("name, playlist\n")
            for i, record in inference_records.iterrows():
                outfile.write(record["name"])
                outfile.write(",")
                outfile.write(record["playlist.name"])
                outfile.write("\n")
