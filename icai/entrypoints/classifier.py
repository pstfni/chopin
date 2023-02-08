import pickle as pkl
from pathlib import Path

import typer

from icai.managers.client import ClientManager
from icai.managers.spotify_client import SpotifyClient
from icai.managers.track import TrackManager
from icai.ml import data
from icai.utils import get_logger

LOGGER = get_logger(__name__)


def main(
    local_file: Path = typer.Option(None, help="Valid path to a local file"),
    liked_songs: bool = typer.Option(False, help="Flag, to classify the user liked songs"),
    model: Path = typer.Argument(..., help="Valid path to a trained model"),
    output: Path = typer.Argument(..., help="The file where the classification summary will be written to"),
):
    """Use a model to classify a local playlist, or the user liked songs.

    A CSV will be written , with the song names and the predicted
    labels.
    """
    if not (local_file or liked_songs):
        raise typer.BadParameter("Neither local_file nor liked_songs were in the command. Please use one of them")
    if local_file and liked_songs:
        raise typer.BadParameter("Both local_file and liked_songs were in the command. Please use only one of them")

    LOGGER.info("🧭 Classifying . . . ")
    if liked_songs:
        client = ClientManager(SpotifyClient().get_client())
        track_manager = TrackManager(client)

        likes = client.get_likes()
        likes = track_manager.set_audio_features(likes)
        inference_records = data.create_inference_records_from_tracks(likes, "liked_songs")
    else:
        inference_records = data.create_inference_records_from_paths([local_file])

    with open(model, "rb") as file:
        classifier = pkl.load(file)
    inference_records["playlist.name"] = classifier.predict(inference_records.iloc[:, 1:])
    with open(output, "w") as outfile:
        outfile.write("name;playlist\n")
        for i, record in inference_records.iterrows():
            outfile.write(record["name"])
            outfile.write(";")
            outfile.write(record["playlist.name"])
            outfile.write("\n")


if __name__ == "__main__":
    typer.run(main)
