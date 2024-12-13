# 💾 Save and restore playlists

## <a name="backup"></a>💾 Backup (save) a playlist

Store and get basic statistics of an existing playlist with the `backup` command.

<div class="termy">

```console
$ describe --name "rock" --output data/

📝 Describing . . .
Wrote playlist rock in data/rock.json
```
</div>

If you don't specify a name, all your playlists will be saved

If you specify an output directory, the entrypoint will dump all the tracks data in a readable JSON. 

<div class="termy">

```console
$ describe --output data/ 

📝 Describing . . .
Wrote playlist pop in data/pop.json
Wrote playlist rock in data/rock.json
Wrote playlist electro in data/electro.json
```
</div>


------


## <a name="restore"></a>🆙 Restore playlist


Use a playlist backup created with the [describe entrypoint](#backup) to restore a playlist, and
upload it back to Spotify.

<div class="termy">

```console
$ restore playlists/my_playlist.json 
```

</div>

You can give a new name to your playlist:

<div class="termy">

```console
$ restore playlists/my_playlist.json --name new_name
```