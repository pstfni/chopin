# Available sources for playlist composition

## playlists

A list of one or more of the _current user_ playlists. 

```yaml title="Add songs from playlists"
playlists:
  - name: rock
  - name: chill
  - name: pop
    weight: 0.25
```

!!! warning "About playlist names"
    Playlists are given with their simplified name, stripped of emojis and spaces. For example,
    `rock 70s ✌` should be written as `rock70s` in the configuration.

    You can run the following code snippet to figure out the correct name you should give:
    ```shell
    playlist_name = "rock 70s ✌"
    python -c "from utils import simplify_string; print(simplify_string($playlist_name))"
    ```

## artists

A list of artists to pick songs from. The `name` is used to query the Spotify API and retrieve
songs from Spotify's _This is ..._ playlists.

```yaml title="Add songs from artists"
artists:
  - name: David Bowie
  - name: The Beatles
  - name: Johnny Cash
    weight: 0.25
```

## radios

A list of artist's radios to pick songs from. The term "radio" refers here to the 
Spotify's _Artist Name Radio_ playlists. 

Songs from radios will include a few songs from the artist, and tracks from related artists.

```yaml title="Add songs from artists' radios"
radios:
  - name: Pulp
  - name: Elvis Costello
  - name: Elliott Smith
    weight: 0.25
```

!!! info "Radios and Spotify API"
    The Spotify API do not let you easily access or find these _Artist Name Radio_ playlists.
    
    For this feature, their behaviour was reproduced by picking songs of the artist, fetching its 
    related artists, and finally picking top songs of each related artists.

## features

With features, you can add recommendations to your playlist. Based on the current playlist composition, and 
the feature `value`, recommended songs will be added. Available features are described in the [API reference](../reference/schemas.md#base-schemas)

Features come from [Spotify audio features analysis](https://developer.spotify.com/documentation/web-api/reference/#/operations/get-audio-features)

```yaml hl_lines="4 5 6 7 8" title="Recommend songs based on track features"
artists:
  - name: David Bowie
  - name: The Beatles
features:
  - name: acousticness
    value: 0.6
  - name: popularity
    value: 80
```

The above composition configuration will:

1. Add Bowie and Beatles songs to your playlists. 
2. Based on these songs, it will recommend relatively acoustic new ones.
3. Finally, it will recommend popular songs.

## history

`history` let you add your best songs from the past! Three time ranges are available:

- `short_term` for the last 4 weeks
- `medium_term` for the last 6 months
- `long_term` for your all time best.

```yaml title="Add songs from your most-listened titles"
history:
  - time_range: "short_term"
  - time_range: "long_term"
    weight: 0.25
```

## uris

For full flexibility, you can use any kind of playlist in your composition. Simply add the Spotify playlist uri
in your YAML.

```yaml title="Add songs from any Spotify public playlist"
uris:
  - name: 50FTlBiOVTyPgVtPYVUzdn
  - name: 7oK3UXsHYmC3PYGQFY5IOb
    weight: 0.5
```

!!! info "Finding the URI of a playlist"
    URIs are hard to read but can be easily retrieved. The URL link to share a playlist will feature its URI:
    For example: https://open.spotify.com/playlist/7oK3UXsHYmC3PYGQFY5IOb?si=eae4b209bee740f8 is a link for the 
    playlist URI `7oK3UXsHYmC3PYGQFY5IOb`.

!!! abstract "Some playlist URIs to cover your needs"
    
    - `7oK3UXsHYmC3PYGQFY5IOb` : Bob Dylan, the philosophy of modern song
    - `50FTlBiOVTyPgVtPYVUzdn` : Les Inrockuptibles, Trésors Cachés
    - ...


## Putting all this together

You can add as many items from as many sections as you'd like ! And create all kinds of playlists

???+ tip "A playlist for your monthly best-of"
    ```yaml
    name: "🍔 Monthly Best Of"
    nb_songs: 50
    history:
        - time_range: short_term
    ```

???+ tip "A playlist for a chill evening"
    ```yaml
    name: "🌆 Calm Tunes"
    nb_songs: 100
    playlists:
        - name: chill
    artists:
        - name: Grandaddy
          weight: 0.5
        - name: Elliott Smith
          weight: 0.5
    radios:
        - name: Richard Hawley
          weight: 0.5
        - name: Bon Iver
          weight: 0.5
    features:
        - name: acousticness
          value: 0.8
          weight: 0.5
    ```

???+ tip "A playlist to cheer you up"
    ```yaml
    name: "🌈 Uplifting tunes"
    nb_songs: 100
    playlists:
        - name: pop
    uris:
        - name: 37i9dQZF1DX9XIFQuFvzM4  # Feelin' Good by Spotify
        - name: 37i9dQZF1DX9wC1KY45plY  # Classic Road Trip Songs by Spotify
    features:
        - name: valence
          value: 0.8
        - name: danceability
          value: 0.7
          weight: 0.5
    ```