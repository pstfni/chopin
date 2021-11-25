import setuptools

setuptools.setup(
    name="spotify-builder",
    entry_points={
        "console_scripts": [
            "composer=entrypoints.composer:main",
        ]
    },
)
