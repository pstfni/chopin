# Compose

Compose playlists from scratch in a few seconds with the `compose` command.

## How to compose your playlist

You can configure your own playlist with a YAML file. First, you can give your playlist a `name`, a `description`, and a number of songs (`nb_songs`).
Several subsections are available to use different sources to customize a playlist. Take the following example:

```yaml title="A composition configuration example"
name: "Energy"
description: "Playlist for working out"
nb_songs: 16
playlists:
  - name: rock
  - name: electro
```

Give your YAML configuration to the entrypoint:

<div class="termy">
```console
$ compose --configuration playlist_composition.yaml
```
</div>

A playlist titled "Energy" will be added to your Spotify library. It will have 16 songs:

- 8 from one of your playlist named 'rock'
- 8 from another one of your playlist, 'electro'

<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/4eOSdWiCJQeMmLAdC479UV?utm_source=generator&theme=0" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>


See the [sources](sources.md) for all the available sources and their options.

## Use weights to balance your playlist

All sources of your playlists have a `weight` attribute. For your running playlist, you may want
more "rock" songs than "electro" ones.

The `weight` attribute can be used to ponder items. All weights will be normalized, and used to compute the number of
songs per item in your final playlist.

```yaml title="A composition configuration, with weights"
name: "Running"
description: "Playlist for working  out"
nb_songs: 100
playlists:
  - name: rock
    weight: 1
  - name: electro
    weight: 0.5
```

Your new "Running" playlist will have 200 songs:

- 66 from your 'rock' playlist
- 34 from 'electro'

## Choose how tracks are selected for your playlists

By default, chopin will pick a _random_ subset of tracks from your sources. It is possible to change this behaviour with the `selection_method` attribute. 

::: chopin.managers.selection
    options: 
      heading_level: 4
      show_bases: False
      members: []

If we illustrate with the example above:


```yaml title="A composition configuration, with weights and selection methods." hl_lines="9 12 15"
name: "Running"
description: "Playlist for jogging"
nb_songs: 100
playlists:
  - name: rock
    weight: 1
  - name: electro
    weight: 0.5
    selection_method: latest
uris:
  - name: 4nutUe1JAzhJSna4mwSIw1  # FIP, best-of du mois
    selection_method: popularity
```

Your new "Running" playlist will have 200 songs:

- 40 from your 'rock' playlist
- The 20 most recently released songs from your 'electro' playlist
- 40 songs from the "FIP, Best of du mois" playlist. These songs will be the most popular (on Spotify) songs from said playlist.

## Use `release_range` to filter tracks by their release date

The `release_range` option let you configure a date range for the tracks you want in your playlist.

```yaml title="A playlist for this year releases" hl_lines="9"
name: "Releases of the year"
nb_songs: 100
playlists:
  - name: pop
  - name: rock
release_range: ["01/01/2023", ]
```

## Available sources

There are many ways to compose your playlist, not just artists and your own playlists. [sources](sources.md) 
present the options available.