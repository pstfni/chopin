# Composer

Create hours of playlist from scratch in a few seconds with the `composer` entrypoint.

```shell
composer -c composition_config.yaml
```

## How to compose your playlist

You can configure your own playlist with a YAML file. First, you can give your playlist a `name`, a `description`, and a number of songs (`nb_songs`).
Several subsections are available to use different sources to customize a playlist. Take the following example:

```yaml title="A composition configuration example"
name: "Running"
description: "Playlist for working  out"
nb_songs: 200
playlists:
  - name: rock
  - name: electro
artists:
  - name: Queen
  - name: Kraftwerk
```

A playlist titled "Running" will be added to your Spotify library. It will have 200 songs:

- 50 from one of your playlist named 'rock'
- 50 from another one of your playlist, 'techno'
- 50 songs by Queen
- and 50 Kraftwerk songs.

See the [sources](sources.md) for all the available sources and their options.

## Use weights to balance your playlist

All sources of your playlists have a `weight` attribute. For your running playlist, you may want
more "rock" songs than "electro" ones.

The `weight` attribute can be used to ponder items. All weights will be normalized, and used to compute the number of
songs per item in your final playlist.

```yaml title="A composition configuration, with weights"
name: "Running"
description: "Playlist for working  out"
nb_songs: 200
playlists:
  - name: rock
    weight: 1
  - name: electro
    weight: 0.5
artists:
  - name: Queen
  - name: Kraftwerk
    weight: 0.5
```

Your new "Running" playlist will have 200 songs:

- 67 from your 'rock' playlist
- 34 from 'electro'
- 67 songs by Queen
- and 34 by Kraftwerk.

## Available sources

There are many ways to compose your playlist, not just artists and your own playlists. [sources](sources.md) 
present the options available.