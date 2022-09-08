import setuptools

setuptools.setup(
    name="spotify-builder",
    entry_points={
        "console_scripts": [
            "composer=entrypoints.composer:main",
            "describer=entrypoints.describer:main",
            "classifier=entrypoints.classifier:main",
            "train=entrypoints.train:main",
        ]
    },
)
