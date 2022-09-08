import argparse
import pickle as pkl
from pathlib import Path

from ml import data
from utils import get_logger

LOGGER = get_logger(__name__)


def main():
    """Classify playlist(s) songs into existing playlists."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--playlists",
        "-p",
        type=Path,
        default=None,
        help="Path to the .jsons describing the playlists to classify",
    )
    parser.add_argument(
        "--model",
        "-m",
        type=Path,
        default=None,
        help="Path to a trained model",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output filepath for the model in trained mode, for the classified song information in inference mode",
    )
    ARGS = vars(parser.parse_args())

    LOGGER.info("🧭 Classifying")
    playlist_paths = Path(ARGS["playlists"]).glob("*.json")
    inference_records = data.create_inference_records(playlist_paths)
    with open(ARGS["model"], "rb") as file:
        classifier = pkl.load(file)
    inference_records["playlist.name"] = classifier.predict(inference_records.iloc[:, 1:])
    with open(ARGS["output"], "w") as outfile:
        outfile.write("name;playlist\n")
        for i, record in inference_records.iterrows():
            outfile.write(record["name"])
            outfile.write(";")
            outfile.write(record["playlist.name"])
            outfile.write("\n")
