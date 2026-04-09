# 🔮 Queue

You cannot shuffle songs in your queue, so let's create a playlist to do so !

The `from-queue` command create a playlist from the songs in your queue.

<div class="termy">

```console
$ chopin from-queue

🔮 Queuing . . .
Playlist '🔮 Queued Mix' successfully created.
```
</div>

You can optionally provide a custom name for the playlist:

<div class="termy">

```console
$ chopin from-queue "My Custom Queue"

🔮 Queuing . . .
Playlist 'My Custom Queue' successfully created.
```
</div>


!!! warning "Spotify API limitation"
    Queues are hard to retrieve from the Spotify API. For this reason, be aware that :
        - You must be _playing_ from a device for this entrypoint to work.
        - The entrypoint will retrieve up to 20 songs from your queue, but not more.

