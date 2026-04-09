# 🔃 Save and restore playlists

## <a name="backup"></a>💾 Backup (save) a playlist

Store and get basic statistics of an existing playlist with the `backup` command.

<div class="termy">

```console
$ chopin backup data/ rock

📝 Describing . . .
Wrote playlist rock in data/rock.json
```
</div>

Both `output` (directory path) and `name` (playlist name) are required positional arguments.


------


## <a name="restore"></a>🆙 Restore playlist


Use a playlist backup created with the [backup entrypoint](#backup) to restore a playlist, and
upload it back to Spotify.

<div class="termy">

```console
$ chopin restore playlists/my_playlist.json new_name
```

</div>