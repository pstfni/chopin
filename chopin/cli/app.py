"""Command to launch the streamlit app."""

try:
    import streamlit  # noqa: F401

    streamlit_dep = True
except ImportError:
    streamlit_dep = False

import click

from chopin.tools.logger import get_logger

logger = get_logger(__name__)


@click.command()
def app():
    """Launch a streamlit app to use chopin."""
    if not streamlit_dep:
        click.echo(
            "The streamlit dependency was not found, it is needed to build the web app."
            "Make sure you have installed the `app` optional dependency:"
            "uv sync --extra app"
        )
        exit(-1)
    from streamlit.web import cli

    cli.main_run(["app/main.py"])
