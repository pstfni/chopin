## ICAI

ICAI is a tool to manage your Spotify library. With the ICAI CLI, you can describe, 
compose, upload or classify playlists easily.

![](docs/img/demo.gif)

### Requirements

#### Installation

Clone the repository and setup.

```shell
git clone git@github.com:pierrestefani/chopin.git
cd chopin/
make setup
```

[Poetry](https://python-poetry.org/) will be installed and used to create a virtual environment for the repository.

#### Spotify developer credentials

Create a [Spotify Developer](https://developer.spotify.com/dashboard/) account and an app. The dummy application
will let you use the service.
Here is an example of a configuration for your application:
```md 
Application Name: "app"
Website: _Not needed_
Redirect URIs: `http://localhost:8888/callback`
Bundle IDs: _Not needed_
Android Packages: _Not needed_
```

Once your application is setup in the Spotify Web interface, you can add your credentials in the `.env` file:

```
client_id=""
client_secret=""
scope="user-top-read,user-library-modify,playlist-modify-public,user-library-read,user-read-playback-state"
```

More infos about the scopes and what they do is available on the [Spotify Developer documentation](https://developer.spotify.com/documentation/general/guides/authorization/scopes/)

#### Check everything works

Once you have:

* installed the icai project
* created your spotify developer account and added your credentials in the `.env` file

You can make sure everything is installed properly by running:

`make check`

It should display your user names and your recent listening habits 🎧

### Access the documentation

Run `mkdocs serve` to build the documentation. A link to the created documentation will be written in your terminal.
Everything about the project and how to use it will be explained there!