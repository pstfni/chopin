## chopin

chopin is a tool to manage your Spotify library. With the chopin CLI, you can describe, 
compose, upload or classify playlists easily.

![](docs/img/demo.gif)

Read the docs on the [chopin page](http://pstfni.github.io/chopin)

### Requirements

#### Installation

Clone the repository and setup.

It is advised to create a virtual environment for Chopin.

```shell
git clone git@github.com:pstfni/chopin.git
cd chopin/
make setup
```

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

* installed the chopin project
* created your spotify developer account and added your credentials in the `.env` file

You can make sure everything is installed properly by running:

`make check`

It should display your user names and your recent listening habits 🎧
