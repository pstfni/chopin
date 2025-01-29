# Available sources for playlist composition

### Playlists

A list of one or more of the _current user_ playlists. 

```yaml hl_lines="3 4 5 6 7 8" title="Add songs from playlists"
name: "New playlist"
nb_songs: 100
playlists:
  - name: rock
  - name: chill
  - name: pop
    weight: 0.25
```

??? warning "About playlist names"
    Playlists are given with their simplified name, stripped of emojis and spaces. For example,
    `rock 70s ✌` should be written as `rock70s` in the configuration.

    You can run the following code snippet to figure out the correct name you should give:
    ```shell
    playlist_name = "rock 70s ✌"
    python -c "from utils import simplify_string; print(simplify_string($playlist_name))"
    ```

### Artists

A list of artists to pick songs from. The `name` is used to query the Spotify API and retrieve
songs from Spotify's _This is ..._ playlists.

```yaml hl_lines="3-8" title="Add songs from artists"
name: "New playlist"
nb_songs: 20
artists:
  - name: David Bowie
  - name: The Beatles
  - name: Johnny Cash
    weight: 0.25
```


### Radios

A list of artist's radios to pick songs from. The term "radio" refers here to the 
Spotify's _Artist Name Radio_ playlists. 

Songs from radios will include a few songs from the artist, and tracks from related artists.

```yaml hl_lines="3-8" title="Add songs from radios of artists"
name: "New playlist"
nb_songs: 50
radios:
  - name: Pulp
  - name: Elvis Costello
  - name: Elliott Smith
    weight: 0.25
```


### History

`history` lets you add your favourite songs from the past! Three time ranges are available:

- `short_term` for the last 4 weeks
- `medium_term` for the last 6 months
- `long_term` for your all-time best.

```yaml title="Add songs from your most-listened titles"
history:
  - time_range: "short_term"
  - time_range: "long_term"
    weight: 0.25
```

### Uris
 
With uris, you can use any kind of playlist in your composition. Simply add the Spotify playlist uri or url
in your YAML.

```yaml title="Add songs from any Spotify public playlist"
uris:
  - name: 50FTlBiOVTyPgVtPYVUzdn
  - name: 7oK3UXsHYmC3PYGQFY5IOb
    weight: 0.5
  - name: https://open.spotify.com/playlist/7oK3UXsHYmC3PYGQFY5IOb?si=eae4b209bee740f8
    weight: 0.25
```

!!! info "Playlist URI or playlist URL ?"
    Both are supported. The URL link to share a playlist features its URI.
    For example: https://open.spotify.com/playlist/7oK3UXsHYmC3PYGQFY5IOb?si=eae4b209bee740f8 is a link for the 
    playlist URI `7oK3UXsHYmC3PYGQFY5IOb`.

??? tip "Some playlist URIs to cover your needs"
    
    - `7oK3UXsHYmC3PYGQFY5IOb` : Bob Dylan, the philosophy of modern song
    - `50FTlBiOVTyPgVtPYVUzdn` : Les Inrockuptibles, Trésors Cachés
    - ...

### Putting all this together

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
          selection_method: latest
    artists:
        - name: Grandaddy
          weight: 0.5
        - name: Elliott Smith
          weight: 0.5
    uris:
        - name: https://open.spotify.com/playlist/6LSRWYpEoo8KiXenl2xHOP?si=e83a89df1dca4728  # Les inrocks, trésors cachés
        - name: https://open.spotify.com/playlist/4nutUe1JAzhJSna4mwSIw1?si=71f802c91a04416e  # FIP, best-of du mois
    ```

???+ tip "A playlist to cheer you up"
    ```yaml
    name: "🌈 Uplifting tunes"
    nb_songs: 100
    playlists:
        - name: pop
    artists:
        - name: Stevie Wonder
        - name: Earth, Wind and Fire
          method: popularity
        - name: Vampire Weekend
        - name: Vulfpeck
    ```

## Deprecated sources

### Features

!!! danger "Unavailable since Spotify removed access to the `audio_features` API routes."

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

### Genres

!!! danger "Unavailable since Spotify removed access to Spotify-owned playlists."


With genres, you can search for genre-specific playlists curated by Spotify, such as "Bossa Nova Mix", "New Wave Mix", 
or "Singer Songwriter Mix" for example.

```yaml title="Add songs from genre playlists"
genres:
  - name: "Bossa Nova"
  - name: "80s"
  - name: "Covers"
```
